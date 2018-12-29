
import libtcodpy as libtcod
from random import randint

from game_messages import Message


class BasicMonster:
    def take_turn(self, target, fov_map, game_map, entities):
        results = []

        monster = self.owner
        if libtcod.map_is_in_fov(fov_map, monster.x, monster.y):

            if monster.distance_to(target) >= 2:
                monster.move_astar(target, entities, game_map)

            elif target.fighter.hp > 0:
                results.extend(monster.fighter.attack(target))

        return results


class ConfusedMonster:
    def __init__(self, prev_ai, num_of_turns=10):
        self.prev_ai = prev_ai
        self.num_of_turns = num_of_turns

    def take_turn(self, target, fov_map, game_map, entities):
        results = []

        if self.num_of_turns > 0:
            random_x = self.owner.x + randint(0, 2) - 1
            random_y = self.owner.y + randint(0, 2) - 1

            # Check for self collision
            if random_x != self.owner.x and random_y != self.owner.y:
                self.owner.move_towards(random_x, random_x, game_map, entities)

            self.num_of_turns -= 1
        else:
            self.owner.ai = self.prev_ai
            results.append({"message": Message("The {0} shakes off its confusion!".format(self.owner.name), libtcod.red)})

        return results

