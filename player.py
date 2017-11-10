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
CANCEL = object()


@strategy_elements.append
def build_new_statues(state, entity):
    global sectors_we_have
    if state.turn % 10 <= 1:
        for direction in Direction.directions():
            nloc = entity.location.adjacent_location_in_direction(direction)
            if state.map.location_on_map(nloc) and state.map.sector_at(nloc).top_left in sectors_we_have:
                continue
            if entity.can_build(direction):
                entity.queue_build(direction)


@strategy_elements.append
def pick_up_adjacent_entities(state, entity):
    adjacent = list(fast_adjacent_entities(state, entity.location)) # entity.entities_within_adjacent_distance(1))
    if len(adjacent) >= 6:
        return CANCEL
    for pickup_entity in adjacent:
        if entity.can_pickup(pickup_entity):
            entity.queue_pickup(pickup_entity)
            break


@strategy_elements.append
def try_throwing_entities(state, entity):
    if entity.holding is not None:
        far_ops = furthest_opponents(state, entity)
        for op in far_ops:
            if entity.location != op.location:
                direction = entity.location.direction_to(op.location)
                if entity.can_throw(direction):
                    entity.queue_throw(direction)
                    break
                if entity.can_throw(direction.rotate_right()):
                    entity.queue_throw(direction.rotate_right())
                    break
                if entity.can_throw(direction.rotate_left()):
                    entity.queue_throw(direction.rotate_left())
                    break


@strategy_elements.append
def try_move_away(state, entity):
    far_ops = furthest_opponents(state, entity)
    for op in far_ops:
        if entity.location != op.location:
            direction = entity.location.direction_to(op.location)
            if entity.can_move(direction):
                entity.queue_move(direction)
                break
            if entity.can_move(direction.rotate_right()):
                entity.queue_move(direction.rotate_right())
                break
            if entity.can_move(direction.rotate_left()):
                entity.queue_move(direction.rotate_left())
                break


for state in game.turns():
    sectors_we_have = set()
    for entity in state.get_entities(team=state.my_team, entity_type=battlecode.Entity.STATUE):
        sectors_we_have.add(state.map.sector_at(entity.location).top_left)
#    print("sectors we have: %d" % len(sectors_we_have))
        
    # Your Code will run within this loop
    for entity in state.get_entities(team=state.my_team, entity_type=battlecode.Entity.THROWER):
        for strategy_func in strategy_elements:
            if strategy_func(state, entity) is CANCEL:
                break

end = time.clock()
print('clock time: '+str(end - start))
print('per round: '+str((end - start) / 1000))

