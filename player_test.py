import battlecode
import time
import random

#Start a game
game = battlecode.Game('player2')
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



for state in game.turns():
    # Your Code will run within this loop
    for entity in state.get_entities(team=state.my_team): 
        # This line gets all the bots on your team
        if(state.turn % 100 == 0):
            for direction in battlecode.Direction.directions():
                if entity.can_build(direction):
                    entity.queue_build(direction)
        #print("GO OG OG ")
        my_location = entity.location
        near_entities = entity.entities_within_adjacent_distance(1)
        near_entities = list(filter(lambda x: x.can_be_picked, near_entities))

        
        # moved = False
        # far_ops = furthest_opponents(state, entity)
        # #print(far_ops)
        # for op in far_ops:
        #     if(entity.location != op.location):
        #         direction = entity.location.direction_to(op.location)
        #         if(entity.can_move(direction)):
        #             entity.queue_move(direction)
        #             #print(entity.location.direction_to(op.location))
        #             moved = True
        #             break
        #         elif(entity.can_move(direction.rotate_right())):
        #             entity.queue_move(direction.rotate_right())
        #             #print(entity.location.direction_to(op.location))
        #             moved = True
        #             break
        #         elif(entity.can_move(direction.rotate_left())):
        #             entity.queue_move(direction.rotate_left())
        #             #print(entity.location.direction_to(op.location))
        #             moved = True
        #             break
        

        # for pickup_entity in entity.entities_within_adjacent_distance(1):
        #     if entity.can_pickup(pickup_entity):
        #         entity.queue_pickup(pickup_entity)
                
        # if(entity.holding is not None):
        #     far_ops = furthest_opponents(state, entity)
        #     for op in far_ops:
        #         if(entity.location != op.location):
        #             direction = entity.location.direction_to(op.location)
        #             if(entity.can_throw(direction)):
        #                 entity.queue_throw(direction)
        #                 break
        #             elif(entity.can_throw(direction.rotate_right())):
        #                 entity.queue_throw(direction.rotate_right())
        #                 break
        #             elif(entity.can_throw(direction.rotate_left())):
        #                 entity.queue_throw(direction.rotate_left())
        #                 break
            
        


end = time.clock()
print('clock time: '+str(end - start))
print('per round: '+str((end - start) / 1000))
