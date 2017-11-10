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
            bad = []
            for opponent in nearest_opponents(state, entity):
                bad.append(entity.location.direction_to(opponent.location))
                bad.append(entity.location.direction_to(opponent.location).rotate_counter_clockwise_degrees(45))
                bad.append(entity.location.direction_to(opponent.location).rotate_counter_clockwise_degrees(-45))
            for direction in battlecode.Direction.directions():
                if (entity.can_move(direction) and (direction not in bad)):
                    entity.queue_move(direction)
                    moved = True
            if(not moved):
                for direction in battlecode.Direction.directions():
                    if entity.can_build(direction):
                        entity.queue_build(direction)
        else:
            for pickup_entity in near_entities:
                assert entity.location.is_adjacent(pickup_entity.location)
                if entity.can_pickup(pickup_entity):
                    entity.queue_pickup(pickup_entity)

        statue = nearest_glass_state(state, entity)
        if(statue != None):
            direction = entity.location.direction_to(statue.location)
            if entity.can_throw(direction):
                entity.queue_throw(direction)
        


end = time.clock()
print('clock time: '+str(end - start))
print('per round: '+str((end - start) / 1000))
