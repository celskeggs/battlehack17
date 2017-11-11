import battlecode
from battlecode import Direction
from battlecode import Location
# from queue import PriorityQueue
import time
import random

DIRS = [Direction.SOUTH_WEST, Direction.SOUTH,
                Direction.SOUTH_EAST, Direction.EAST,
                Direction.NORTH_EAST, Direction.NORTH,
                Direction.NORTH_WEST, Direction.WEST]
def greedy_cheater_helper(state, start, end):
    assert state.map.location_on_map(start)
    assert state.map.location_on_map(end)

    directions = [Direction(1, 0), Direction(-1, 0), Direction(1, 0), Direction(-1, 0),
                     Direction(-1, 1), Direction(1, 1), Direction(-1, -1), Direction(1, -1)]
    if end in state.map._occupied:
        for direction in directions:
            if end.adjacent_location_in_direction(direction) not in state.map._occupied:
                end = end.adjacent_location_in_direction(direction)
                break

    if(start == end):
        return []

    path = [start]

def gen_map(state):
    board = [[False for x in range(state.map.height)] for y in range(state.map.width)]
    for i in range(state.map.width):
        for j in range(state.map.height):
            if Location(i, j) in state.map._occupied and not state.map._occupied[Location(i, j)].is_thrower:
                board[i][j] = True
    
    for i in range(state.map.width):
        for j in range(state.map.height):
            if board[i][j]:
                if i >= 1 and i <= state.map.width - 2:
                    if j >= 1 and j <= state.map.height - 2:
                        if not (board[i+1][j] or board[i-1][j] or board[i][j+1] or board[i][j-1]):
                            board[i][j] = False
    return board

def gen_zoning(state, board):
    zone = [[False for y in range(state.map.height)] for x in range(state.map.width)]
    remain = [(x,y) for x in range(state.map.width) for y in range(state.map.height) if board[x][y]]
    while remain:
        to_traverse = [remain.pop()]
        min_x, min_y, max_x, max_y = to_traverse[0] * 2
        while to_traverse:
            x, y = to_traverse.pop()
            for adjx, adjy in [(x,y+1),(x,y-1),(x+1,y),(x-1,y)]:
                if (adjx, adjy) in remain:
                    to_traverse.append((adjx, adjy))
                    remain.remove((adjx, adjy))
            if x < min_x: min_x = x
            if y < min_y: min_y = y
            if x > max_x: max_x = x
            if y > max_y: max_y = y
        if min_x < 1: min_x = 1
        if min_y < 1: min_x = 1
        if max_x >= state.map.width - 1: max_x = state.map.width - 2
        if max_y >= state.map.height - 1: max_y = state.map.height - 2
        for x in range(min_x - 1, max_x + 2):
            for y in range(min_y - 1, max_y + 2):
                zone[x][y] = True
#    for i in range(1, len(board) - 1):
#        for j in range(1, len(board[0]) - 1):
#            if board[i][j]:
#                zone[i][j] = True
#                zone[i+1][j] = True
#                zone[i-1][j] = True
#                zone[i][j+1] = True
#                zone[i][j-1] = True
#                zone[i+1][j+1] = True
#                zone[i-1][j-1] = True
#                zone[i+1][j-1] = True
#                zone[i-1][j+1] = True
    return zone

class BinQueue:
    def __init__(self):
        self.bins = [[]]
        self.smallest_bin = 0

    def put(self, value, priority):
        assert priority >= 0
        if priority < self.smallest_bin:
            self.smallest_bin = priority
        while len(self.bins) < priority + 1:
            self.bins.append([])
        self.bins[priority].append(value)

    def empty(self):
        while not self.bins[self.smallest_bin]:
            if len(self.bins) <= self.smallest_bin + 1:
                return True
            else:
                self.smallest_bin += 1
        return False

    def get(self):
        if self.empty():  # also advances to filled bin
            raise Exception("empty")
        return self.bins[self.smallest_bin].pop()

#Takes a state, a starting location, and an ending location, and finds the fastest path
#around obstacles to get between the two. Returns an empty list if the location is inaccessible
def a_star(state, start, end, board):
    directions = [Direction(1, 0), Direction(-1, 0), Direction(1, 0), Direction(-1, 0),
                     Direction(-1, 1), Direction(1, 1), Direction(-1, -1), Direction(1, -1)]
    if end in state.map._occupied:
        for direction in directions:
            if end.adjacent_location_in_direction(direction) not in state.map._occupied:
                end = end.adjacent_location_in_direction(direction)
                break

    if(start == end):
        return []

    came_from = {}
    cost_so_far = {}
    direction_from = {}
    frontier = BinQueue()
    start_point = (start.x, start.y)
    frontier.put(start_point, 0)
    came_from[start_point] = None
    direction_from[start_point]  = None
    cost_so_far[start_point] = 0
    traversed = set()
    found = False

    while not frontier.empty():

        pos = frontier.get()
        if pos == end:
            found = True
            break
        if pos in traversed:
            continue
        traversed.add(pos)
        cur_x = pos[0]
        cur_y = pos[1]
        north = (cur_x, cur_y + 1)
        south = (cur_x, cur_y - 1)
        east = (cur_x + 1, cur_y)
        west = (cur_x - 1, cur_y)
        north_west =(cur_x - 1, cur_y + 1)
        north_east =(cur_x + 1, cur_y + 1)
        south_west =(cur_x - 1, cur_y + 1)
        south_east =(cur_x + 1, cur_y - 1)
        locations = [(north, Direction(1, 0)), (south, Direction(-1, 0)), (east, Direction(1, 0)), (west, Direction(-1, 0)),
                     (north_west, Direction(-1, 1)), (north_east, Direction(1, 1)), (south_west, Direction(-1, -1)), (south_east, Direction(1, -1))]

        for place, direction in locations:
            
            if 0 < place[0] < state.map.width and 0 < place[1] < state.map.height :
                if board[place[0]][place[1]]:
                    continue
                new_cost = cost_so_far[pos] + 1 
                if place not in cost_so_far or new_cost < cost_so_far[place]:
                    cost_so_far[place] = new_cost
                    priority = new_cost + max(abs(place[0] - end.x), abs(place[1]- end.y))
                    frontier.put(place, priority)
                    came_from[place] = pos
                    direction_from[place] = direction
    if(found):
        trace = end
        path = [end]
        while trace != start:
            path.insert(0, direction_from[trace])
            trace = came_from[trace]
        return path
    else:
        return []


def directions_rand():
    random.shuffle(DIRS)
    return list(DIRS)


def fast_adjacent_entities(state, location):
    for direction in directions_rand():
        nloc = location.adjacent_location_in_direction(direction)
        if nloc in state.map._occupied:
            yield state.map._occupied[nloc]

def is_in_diagonal(loc1, loc2):
    dx, dy = loc1.x - loc2.x, loc1.y - loc2.y
    return dx == 0 or dy == 0 or abs(dx) == abs(dy)


MOTION_KEY = {" ": (0, 0), "1": (-1, 1), "^": (0, 1), "<": (-1, 0), "v": (0, 1), ">": (1, 0), "9": (1, -1)}
MOTION_MAP = [" <<999v ",
              " <<99v <",
              " <99v <1",   # 1^
              " <9v <11",   # < >
              " <v <111",   #  v9
              " < <11vv",
              "  vvvvvv",
              "        "][::-1]
DIST_MAP =   ["01222110",
              "01221101",
              "01211011",
              "01110112",
              "01101122",
              "01011222",
              "00111111",
              "00000000"][::-1]
strafing_lookup = {}
for dx in range(0, 8):
    for dy in range(0, 8):
        ldx, ldy = MOTION_KEY[MOTION_MAP[dy][dx]]
        strafing_lookup[(dx,dy)] = (ldx, ldy, int(DIST_MAP[dy][dx]))
        strafing_lookup[(-dx,dy)] = (-ldx, ldy, int(DIST_MAP[dy][dx]))
        strafing_lookup[(dx,-dy)] = (ldx, -ldy, int(DIST_MAP[dy][dx]))
        strafing_lookup[(-dx,-dy)] = (-ldx, -ldy, int(DIST_MAP[dy][dx]))


def calc_strafe_dist(loc1, loc2):
    assert -7 <= loc1.x - loc2.x <= 7 and -7 <= loc1.y - loc2.y <= 7
    ldx, ldy, dist = strafing_lookup[loc1.x - loc2.x, loc1.y - loc2.y]
    return dist


def calc_strafe(loc1, loc2):
    assert -7 <= loc1.x - loc2.x <= 7 and -7 <= loc1.y - loc2.y <= 7
    ldx, ldy, dist = strafing_lookup[loc1.x - loc2.x, loc1.y - loc2.y]
    return Direction(ldx, ldy)


def calculate_broad_goals(state):
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
                unit_collection_points[entity.location] = 4
                attack_targets.add(entity.location)
        elif entity.type == battlecode.Entity.THROWER:
            if entity.team == state.my_team:
                if entity.held_by is None and entity.can_act:
                    available_units.append(entity)
                    units_by_sector[state.map.sector_at(entity.location).top_left].append(entity)
            else:
                # goal: destroy this unit
                attack_targets.add(entity.location)

    # have units build anything they can before we make plans
    for unit in available_units:
        for direction in directions_rand():
            adj = unit.location.adjacent_location_in_direction(direction)
            if state.map.location_on_map(adj) and state.map.sector_at(adj).top_left not in sectors_we_have:
                if unit.can_build(direction):
                    unit.queue_build(direction)
                    sectors_we_have.add(state.map.sector_at(adj).top_left)
                    break

    # now send units towards new places
    for sector in state.map._sectors.values():
        if sector.top_left not in sectors_we_have:
            unit_collection_points[sector.top_left + (state.map.sector_size // 2, state.map.sector_size // 2)] = 1
    
    total_requests = sum(unit_collection_points.values())
    if total_requests and len(available_units) >= total_requests + 2:
        extra_units_to_distribute = (len(available_units) - total_requests) // 2
        uniform_extra_fraction = extra_units_to_distribute // total_requests
        # allocate large blocks (update later)
        extra_units_to_distribute -= uniform_extra_fraction * total_requests
        # allocate small blocks
        choices = []
        for key, value in unit_collection_points.items():
            choices += [key] * value
        random.shuffle(choices)
        # update large blocks
        for key, value in unit_collection_points.items():
            unit_collection_points[key] *= 1 + uniform_extra_fraction
        # update small blocks
        for choice in choices[:extra_units_to_distribute]:
            unit_collection_points[key] += 1
        assert sum(unit_collection_points.values()) == total_requests + (len(available_units) - total_requests) // 2

    return sectors_we_have, unit_collection_points, attack_targets, available_units, units_by_sector


def plan_attacks(state, available_units, attack_targets):
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
            assert unit.is_holding and unit.can_act
            hittable_glass = None
            hittable_thrower = None
            hittable_surface = None
            move_away_from = None
            for direction in directions_rand():
                blocker = unit.location.adjacent_location_in_direction(direction)
                if not state.map.location_on_map(blocker):
                    continue
                if blocker in state.map._occupied:
                    # can't throw in this direction
                    blocker_obj = state.map._occupied[blocker]
                    if blocker_obj.type != battlecode.Entity.HEDGE and blocker_obj.team != state.my_team and unit.can_move(direction.rotate_opposite()):
                        move_away_from = direction
                    continue
                hit_anything = False
                for dist in range(2, 8):
                    cell = unit.location + (dist * direction.dx, dist * direction.dy)
                    if cell not in state.map._occupied:
                        continue
                    hit_anything = True
                    collision_with = state.map._occupied[cell]
                    if collision_with.team == state.my_team: # don't throw this way!
                        continue
                    if collision_with.type == battlecode.Entity.THROWER:
                        hittable_thrower = direction
                        break
                    elif collision_with.type == battlecode.Entity.STATUE:
                        hittable_glass = direction
                        break
                    else:
                        assert collision_with.type == battlecode.Entity.HEDGE
                        if unit.holding.team != state.my_team:  # i.e. hedges are a fine target iff we're carrying an enemy
                            hittable_surface = direction
                            break
                if not hit_anything and state.map.location_on_map(cell) and (state.map.tile_at(cell) == "G") == (unit.holding.team == state.my_team):
                    hittable_surface = direction
            hittable_final = hittable_glass or hittable_thrower  # TODO: be willing to hold on to team members for a short time
            if hittable_final:
                assert unit.is_holding and unit.can_act
                assert unit.can_throw(hittable_final)
                unit.queue_throw(hittable_final)
            elif move_away_from is not None:
                if unit.can_move(move_away_from.rotate_opposite()):
                    unit.queue_move(move_away_from.rotate_opposite())
            else:
                strafe_dist = 1e3000
                best_target = None
                for target in attack_targets:
                    if 2 <= unit.location.adjacent_distance_to(target) <= 7:
                        lstrafe = calc_strafe_dist(unit.location, target)
                        if lstrafe < strafe_dist:
                            strafe_dist, best_target = lstrafe, target
                            if lstrafe == 1:
                                break
                if best_target is not None:
                    direction = calc_strafe(unit.location, best_target)
                    if unit.can_move(direction):
                        unit.queue_move(direction)
                    # TODO: what if we can't do that
                elif hittable_surface is not None:
                    assert unit.can_throw(hittable_surface)
                    unit.queue_throw(hittable_surface)


def assign_units_to_goals(state, unit_collection_points):
    remaining = dict(unit_collection_points)
    unit_directives = []
    for unit in available_units:
        if not unit.can_act:
            continue
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
    return unit_directives


def move_units(state, available_units, unit_directives, board):
    # have units actually move
    zone = gen_zoning(state, board)
    for unit, goal in unit_directives:
        if unit.location == goal:
            continue

        if zone[unit.location.x][unit.location.y]:
            direction = a_star(state, unit.location, goal, board)
            if len(direction) == 0:
                direction = [unit.location.direction_to(goal)]
        else:
            direction = [unit.location.direction_to(goal)]

        if unit.can_move(direction[0]):
            unit.queue_move(direction[0])
        elif unit.can_move(direction[0].rotate_counter_clockwise_degrees(45)):
            unit.queue_move(direction[0].rotate_counter_clockwise_degrees(45))
        elif unit.can_move(direction[0].rotate_counter_clockwise_degrees(315)):
            unit.queue_move(direction[0].rotate_counter_clockwise_degrees(315))

    # motion away from others if we haven't done anything else
    for unit in available_units:
        if unit.can_act:
            for direction in directions_rand():
                found = state.map._occupied.get(unit.location.adjacent_location_in_direction(direction.rotate_opposite()),None)
                if found and found.team == state.my_team:
                    if unit.can_move(direction):
                        unit.queue_move(direction)

if __name__ == "__main__":
    game = battlecode.Game('player')
    start = time.clock()
    loop_start = time.time()

    for state in game.turns():
        board = gen_map(state)
        last_start = loop_start
        loop_start = time.time()
        sectors_we_have, unit_collection_points, attack_targets, available_units, units_by_sector = calculate_broad_goals(state)

        plan_attacks(state, available_units, attack_targets)

        unit_directives = assign_units_to_goals(state, unit_collection_points)

        move_units(state, available_units, unit_directives, board)
        loop_end = time.time()
    #    print((loop_end - loop_start) * 1000, "\t", (loop_start - last_start) * 1000, "\t", state.turn)

    end = time.clock()
    print('clock time: '+str(end - start))
    print('per round: '+str((end - start) / 1000))

