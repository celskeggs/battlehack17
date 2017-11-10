import battlecode
import time
import random

#Start a game
game = battlecode.Game('testplayer')

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

def nearest_opponents(state, entity):
    nearest_thrower = None
    nearest_dist = 10000
    opponents = []
    for other_entity in state.get_entities(entity_type=battlecode.Entity.THROWER):
        if(entity == other_entity):
            continue
        dist = entity.location.adjacent_distance_to(other_entity.location)
        if(dist < nearest_dist):
            dist = nearest_dist
            opponents = []
            opponents.append(other_entity)
        elif(dist == nearest_dist):
            opponents.append[other_entity]

    return opponents

def furthest_opponents(state, entity):
    nearest_thrower = None
    nearest_dist = 10000
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
            opponents.append[other_entity]

    return opponents



for state in game.turns():
    # Your Code will run within this loop
    for entity in state.get_entities(team=state.my_team): 
        # This line gets all the bots on your team
        if(state.turn % 100 == 0):
            for direction in battlecode.Direction.directions():
                if entity.can_build(direction):
                    entity.queue_build(direction)

        my_location = entity.location
        near_entities = entity.entities_within_euclidean_distance(1.9)
        near_entities = list(filter(lambda x: x.can_be_picked, near_entities))

        if(len(list(entity.entities_within_adjacent_distance(1))) > 1):
            moved = False
            far_ops = furthest_opponents(state, entity)
            for op in far_ops:
                if(entity.can_move(entity.location.direction_to(op))):
                    entity.queue_move(entity.location.direction_to(op))
                    moved = True
                    break
                elif(entity.can_move(entity.location.direction_to(op).rotate_right())):
                    entity.queue_move(entity.location.direction_to(op).rotate_right())
                    moved = True
                    break
                elif(entity.can_move(entity.location.direction_to(op).rotate_left())):
                    entity.queue_move(entity.location.direction_to(op).rotate_left())
                    moved = True
                    break
            if(not moved):
                for pickup_entity in near_entities:
                    assert entity.location.is_adjacent(pickup_entity.location)
                    if entity.can_pickup(pickup_entity):
                        entity.queue_pickup(pickup_entity)

        else: 
            for pickup_entity in near_entities:
                assert entity.location.is_adjacent(pickup_entity.location)
                if entity.can_pickup(pickup_entity):
                    entity.queue_pickup(pickup_entity)
                    far_ops = furthest_opponents(state, entity)
                    for op in far_ops:
                        if(entity.can_throw(entity.location.direction_to(op))):
                            entity.queue_throw(entity.location.direction_to(op))
                            moved = True
                            break
                        elif(entity.can_throw(entity.location.direction_to(op).rotate_right())):
                            entity.queue_throw(entity.location.direction_to(op).rotate_right())
                            moved = True
                            break
                        elif(entity.can_throw(entity.location.direction_to(op).rotate_left())):
                            entity.queue_throw(entity.location.direction_to(op).rotate_left())
                            moved = True
                            break
            
        


end = time.clock()
print('clock time: '+str(end - start))
print('per round: '+str((end - start) / 1000))
