import battlecode
from battlecode import Direction
import time
import random

#Start a game
game = battlecode.Game('player')

start = time.clock()

#define helper functions here
def nearest_glass_state(state, entity):
    nearest_statue = None
    nearest_dist = 10000
    for other_entity in state.get_entities(entity_type=battlecode.Entity.STATUE):
        if(entity == other_entity):
            continue
        dist = entity.location.adjacent_distance_to(other_entity.location)
        if(dist< nearest_dist):
            dist = nearest_dist
            nearest_statue = other_entity

    return nearest_statue

def fast_adjacent_entities(state, location):
    for direction in Direction.directions():
        nloc = location.adjacent_location_in_direction(direction)
        if nloc in state.map._occupied:
            yield state.map._occupied[nloc]

def nearest_opponents(state, entity):
    nearest_thrower = None
    nearest_dist = 10000
    opponents = []
    for other_entity in state.get_entities(entity_type=battlecode.Entity.THROWER):
        if(entity == other_entity) or entity.team != other_entity.team:
            continue
        dist = entity.location.adjacent_distance_to(other_entity.location)
        if(dist < nearest_dist):
            dist = nearest_dist
            opponents = []
            opponents.append(other_entity)
        elif(dist == nearest_dist):
            opponents.append(other_entity)

    return opponents

def furthest_opponents(state, entity):
    nearest_thrower = None
    nearest_dist = 0
    opponents = []
    for other_entity in state.get_entities(entity_type=battlecode.Entity.THROWER):
        if(entity == other_entity):
            continue
        dist = entity.location.adjacent_distance_to(other_entity.location)
        if(dist > nearest_dist):
            dist = nearest_dist
            opponents = []
            opponents.append(other_entity)
        elif(dist == nearest_dist):
            opponents.append(other_entity)

    return opponents


strategy_elements = []


def is_in_diagonal(loc1, loc2):
    dx, dy = loc1.x - loc2.x, loc1.y - loc2.y
    return dx == 0 or dy == 0 or abs(dx) == abs(dy)


for state in game.turns():
    sectors_we_have = set()
    unit_collection_points = {}
    attack_targets = set()
    available_units = []
    units_by_sector = {sector.top_left: [] for sector in state.map._sectors.values()}
    for entity in state.entities.values():
        if entity.type == battlecode.Entity.STATUE:
            if entity.team == state.my_team:
                # goal: protect this statue, by bringing a unit nearby
                # TODO unit_collection_points[entity.location] = 1
                sectors_we_have.add(state.map.sector_at(entity.location).top_left)
            else:
                # goal: destroy this statue, by bringing units nearby and attacking the statue
                unit_collection_points[entity.location] = 5
                attack_targets.add(entity.location)
        elif entity.type == battlecode.Entity.THROWER:
            if entity.team == state.my_team:
                if entity.held_by is None:
                    available_units.append(entity)
                    units_by_sector[state.map.sector_at(entity.location).top_left].append(entity)
            else:
                # goal: destroy this unit
                attack_targets.add(entity.location)

    for sector in state.map._sectors.values():
        if sector.top_left not in sectors_we_have:
            build_queued = False
            for unit in units_by_sector[sector.top_left]:
                if not unit.can_act: continue
                for direction in Direction.directions():
                    if unit.can_build(direction): # TODO: make sure they build in THIS sector
                        if (state.map.sector_at(unit.location.adjacent_location_in_direction(direction)) == sector):
                            unit.queue_build(direction)
                            build_queued = True
                            break
#                    else:
#                        print("can't build")
                if build_queued:
                    break
            if not build_queued:
                unit_collection_points[sector.top_left + (state.map.sector_size // 2, state.map.sector_size // 2)] = 1

    # assign units to locations
    remaining = dict(unit_collection_points)
    unit_directives = []
    for unit in available_units:
        smallest_dist = 1e3000
        best_goal = None
        for collection_point, needed in remaining.items():
            assert needed > 0
            ndist = unit.location.adjacent_distance_to(collection_point)
            if ndist < smallest_dist:
                smallest_dist = ndist
                best_goal = collection_point
        if best_goal is not None:
            unit_directives.append((unit, best_goal))
            remaining[best_goal] -= 1
            if remaining[best_goal] == 0:
                del remaining[best_goal]

#    print(unit_directives)

    # attack loop
    for unit in available_units:
        if not unit.can_act: continue
        if unit.holding is None:
            do_we_have_something_to_attack = False
            to_pick_up = None
            for target in attack_targets:
                dist = unit.location.adjacent_distance_to(target)
                if dist <= 7:
                    if target in state.map._occupied and unit.can_pickup(state.map._occupied[target]):
                        to_pick_up = target
                    else:
                        do_we_have_something_to_attack = True
            if to_pick_up is not None:
                unit.queue_pickup(state.map._occupied[to_pick_up])
            elif do_we_have_something_to_attack:
                for adjacent in fast_adjacent_entities(state, unit.location):
                    if unit.can_pickup(adjacent):
                        unit.queue_pickup(adjacent)
        else:
            smallest = 8
            best_target = None
            smallest_linear = 8
            best_linear = None
            should_back_up_from = None
            for target in attack_targets:
                dist = unit.location.adjacent_distance_to(target)
                if dist == 0:
                    continue
                if 2 <= dist < smallest:
                    smallest = dist
                    best_target = target
                if 2 <= dist < smallest_linear and is_in_diagonal(unit.location, target):
                    smallest_linear = dist
                    best_linear = target
                if dist == 1:
                    should_back_up_from = target
            if best_linear is not None:
                direction = unit.location.direction_to(best_linear)
                if unit.can_throw(direction):
                    unit.queue_throw(direction)
            elif should_back_up_from is not None:
                direction = unit.location.direction_to(should_back_up_from).rotate_opposite()
                if unit.can_move(direction):
                    unit.queue_move(direction)
                elif unit.can_move(direction.rotate_left()):
                    unit.queue_move(direction.rotate_left())
                elif unit.can_move(direction.rotate_right()):
                    unit.queue_move(direction.rotate_right())
            elif best_target is not None:
                direction = unit.location.direction_to(best_target)
                if unit.can_move(direction.rotate_left()):
                    unit.queue_move(direction.rotate_left())
                elif unit.can_move(direction.rotate_right()):
                    unit.queue_move(direction.rotate_right())
            else:
                for direction in Direction.directions():
                    land_at = unit.location + (direction.dx * 7, direction.dy * 7)
                    if state.map.location_on_map(land_at) and (state.map.tile_at(land_at) == "G") == (unit.holding.team == state.my_team):
                        if unit.can_throw(direction):
                            unit.queue_throw(direction)
                            break

    # have units actually move
    for unit, goal in unit_directives:
        if unit.location == goal:
            continue
        direction = unit.location.direction_to(goal)
#        print("trying to move towards directive")
        if not unit.can_act:
            pass
#            print("can't act")
        if unit.can_move(direction):
            unit.queue_move(direction)
        elif unit.can_move(direction.rotate_counter_clockwise_degrees(45)):
            unit.queue_move(direction.rotate_counter_clockwise_degrees(45))
        elif unit.can_move(direction.rotate_counter_clockwise_degrees(315)):
            unit.queue_move(direction.rotate_counter_clockwise_degrees(315))
#        else:
#            print("but could not: %s -> %s (direction %s,%s)" % (unit.location, goal, direction.dx, direction.dy))

    # motion away from others if we haven't done anything else
    for unit in available_units:
        if unit.can_act:
            for direction in Direction.directions():
                found = state.map._occupied.get(unit.location.adjacent_location_in_direction(direction.rotate_opposite()),None)
                if found and found.team == state.my_team:
                    if unit.can_move(direction):
                        unit.queue_move(direction)

end = time.clock()
print('clock time: '+str(end - start))
print('per round: '+str((end - start) / 1000))

