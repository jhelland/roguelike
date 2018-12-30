
import libtcodpy as libtcod
from random import randint

from render_functions import RenderOrder

from game_messages import Message

from random_utils import random_choice_from_dict, weight_from_dungeon_level

from map_objects.tile import Tile
from map_objects.rectangle import Rect

from entity import Entity
from components.ai import BasicMonster
from components.fighter import Fighter
from components.item import Item
from components.stairs import Stairs
from components.equipment import EquipmentSlots
from components.equippable import Equippable

from item_functions import heal, cast_lightning, cast_fireball, cast_confusion


class GameMap:
    def __init__(self, width, height, dungeon_level=1):
        self.width = width
        self.height = height
        self.tiles = self.initialize_tiles()
        self.dungeon_level = dungeon_level

    def initialize_tiles(self):
        tiles = [[Tile(True) for y in range(self.height)] for x in range(self.width)]

        return tiles

    def make_map(self,
                 max_rooms,
                 room_min_size,
                 room_max_size,
                 map_width,
                 map_height,
                 player,
                 entities):
        rooms = []

        center_of_last_room_x = None
        center_of_last_room_y = None

        for r in range(max_rooms):
            # random width and height
            width = randint(room_min_size, room_max_size)
            height = randint(room_min_size, room_max_size)

            # random position without going out of bounds
            x = randint(0, map_width - width - 1)
            y = randint(0, map_height - height - 1)

            # create rectangle from specs
            new_room = Rect(x, y, width, height)

            # run through other rooms and check for intersections
            for other_room in rooms:
                if new_room.is_intersecting(other_room):
                    break
            else:
                # no intersections
                # make room walkable
                self.create_room(new_room)

                # get center coordinates of new room
                (new_center_x, new_center_y) = new_room.get_center_coords()

                center_of_last_room_x = new_center_x
                center_of_last_room_y = new_center_y

                if len(rooms) == 0:
                    # starting room for player
                    player.x = new_center_x
                    player.y = new_center_y
                else:
                    # connect new room to previous room
                    (prev_center_x, prev_center_y) = rooms[-1].get_center_coords()

                    # create random tunnel
                    if randint(0, 1):
                        # move horizontally then vertically
                        self.create_horiz_tunnel(prev_center_x, new_center_x, prev_center_y)
                        self.create_vert_tunnel(prev_center_y, new_center_y, new_center_x)
                    else:
                        # move vertically then horizontally
                        self.create_vert_tunnel(prev_center_y, new_center_y, prev_center_x)
                        self.create_horiz_tunnel(prev_center_x, new_center_x, new_center_y)

                # fill with monsters
                self.place_entities_in_room(new_room, entities)

                # append new room to list
                rooms.append(new_room)

        stairs_component = Stairs(self.dungeon_level + 1)
        down_stairs = Entity(
            center_of_last_room_x,
            center_of_last_room_y,
            '>',
            libtcod.white,
            "Stairs Down",
            render_order=RenderOrder.STAIRS,
            stairs=stairs_component
        )
        entities.append(down_stairs)

    def create_room(self, room_rect):
        # go through tiles in rectangle and make them passable
        for x in range(room_rect.x1 + 1, room_rect.x2):
            for y in range(room_rect.y1 + 1, room_rect.y2):
                self.tiles[x][y].blocked = False
                self.tiles[x][y].block_sight = False

    def create_horiz_tunnel(self, x1, x2, y):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False

    def create_vert_tunnel(self, y1, y2, x):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False

    def place_entities_in_room(self, room_rect, entities):
        max_monsters_per_room = weight_from_dungeon_level([[2, 1], [3, 4], [5, 6]], self.dungeon_level)
        max_items_per_room = weight_from_dungeon_level([[1, 1], [2, 4]], self.dungeon_level)

        # get random number of monsters
        number_of_monsters = randint(0, max_monsters_per_room)
        number_of_items = randint(0, max_items_per_room)

        monster_chances = {
            "orc": 80,
            "troll": weight_from_dungeon_level([[15, 3], [30, 5], [60, 7]], self.dungeon_level),
        }
        item_chances = {
            "healing_potion": 35,
            "sword": weight_from_dungeon_level([[5, 4]], self.dungeon_level),
            "shield": weight_from_dungeon_level([[15, 8]], self.dungeon_level),
            "lightning_scroll": weight_from_dungeon_level([[25, 4]], self.dungeon_level),
            "fireball_scroll": weight_from_dungeon_level([[25, 6]], self.dungeon_level),
            "confusion_scroll": weight_from_dungeon_level([[10, 2]], self.dungeon_level),
        }

        for i in range(number_of_monsters):
            # choose random location in room
            x = randint(room_rect.x1 + 1, room_rect.x2 - 1)
            y = randint(room_rect.y1 + 1, room_rect.y2 - 1)

            # make sure no monster is already in spot
            if not any([entity for entity in entities if entity.x == x and entity.y == y]):
                monster_choice = random_choice_from_dict(monster_chances)

                if monster_choice == "orc":
                    fighter_component = Fighter(hp=20, defense=0, power=4, xp=35)
                    ai_component = BasicMonster()
                    monster = Entity(
                        x,
                        y,
                        'o',
                        libtcod.desaturated_green,
                        "Orc",
                        blocks=True,
                        render_order=RenderOrder.ACTOR,
                        fighter=fighter_component,
                        ai=ai_component
                    )
                else:  # Place troll
                    fighter_component = Fighter(hp=30, defense=2, power=8, xp=100)
                    ai_component = BasicMonster()
                    monster = Entity(
                        x,
                        y,
                        'T',
                        libtcod.darker_green,
                        "Troll",
                        blocks=True,
                        render_order=RenderOrder.ACTOR,
                        fighter=fighter_component,
                        ai=ai_component
                    )
                entities.append(monster)

        for i in range(number_of_items):
            x = randint(room_rect.x1 + 1, room_rect.x2 - 1)
            y = randint(room_rect.y1 + 1, room_rect.y2 - 1)

            if not any([entity for entity in entities if entity.x == x and entity.y == y]):
                item_choice = random_choice_from_dict(item_chances)

                if item_choice == "healing_potion":
                    item_component = Item(use_function=heal, amount=40)
                    item = Entity(
                        x,
                        y,
                        '!',
                        libtcod.violet,
                        "Potion of Healing",
                        render_order=RenderOrder.ITEM,
                        item=item_component
                    )
                elif item_choice == "sword":
                    equippable_component = Equippable(EquipmentSlots.MAIN_HAND, power_bonus=3)
                    item = Entity(
                        x,
                        y,
                        '/',
                        libtcod.sky,
                        "Sword",
                        equippable=equippable_component
                    )
                elif item_choice == "shield":
                    equippable_component = Equippable(EquipmentSlots.OFF_HAND, defense_bonus=1)
                    item = Entity(
                        x,
                        y,
                        '[',
                        libtcod.darker_orange,
                        "Shield",
                        equippable=equippable_component
                    )
                elif item_choice == "fireball_scroll":
                    item_component = Item(
                        use_function=cast_fireball,
                        targeting=True,
                        targeting_message=Message("Left-click a target tile for fireball. Right-click or Esc to cancel.", libtcod.light_cyan),
                        damage=25,
                        radius=3
                    )
                    item = Entity(
                        x,
                        y,
                        '#',
                        libtcod.red,
                        "Scroll of Fireball",
                        render_order=RenderOrder.ITEM,
                        item=item_component
                    )
                elif item_choice == "confusion_scroll":
                    item_component = Item(
                        use_function=cast_confusion,
                        targeting=True,
                        targeting_message=Message("Left-click a target tile for fireball. Right-click or Esc to cancel.", libtcod.light_cyan)
                    )
                    item = Entity(
                        x,
                        y,
                        '#',
                        libtcod.light_green,
                        "Scroll of Confusion",
                        render_order=RenderOrder.ITEM,
                        item=item_component
                    )
                else:  # Place lightning scroll
                    item_component = Item(use_function=cast_lightning, damage=40, maximum_range=5)
                    item = Entity(
                        x,
                        y,
                        '#',
                        libtcod.yellow,
                        "Lightning Scroll",
                        render_order=RenderOrder.ITEM,
                        item=item_component
                    )
                entities.append(item)

    def is_tile_blocked(self, x, y):
        if self.tiles[x][y].blocked:
            return True

        return False

    def next_floor(self, player, message_log, constants):
        self.dungeon_level += 1
        entities = [player]

        self.tiles = self.initialize_tiles()
        self.make_map(
            constants["max_rooms"],
            constants["room_min_size"],
            constants["room_max_size"],
            constants["map_width"],
            constants["map_height"],
            player,
            entities
        )

        player.fighter.heal(player.fighter.max_hp // 2)

        message_log.add_message(Message("You take a moment to rest and recover your strength", libtcod.light_violet))

        return entities
