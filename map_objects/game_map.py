
import libtcodpy as libtcod
from random import randint

from render_functions import RenderOrder

from game_messages import Message

from map_objects.tile import Tile
from map_objects.rectangle import Rect

from entity import Entity
from components.ai import BasicMonster
from components.fighter import Fighter
from components.item import Item

from item_functions import heal, cast_lightning, cast_fireball, cast_confusion


class GameMap:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.tiles = self.initialize_tiles()

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
                 entities,
                 max_monsters_per_room,
                 max_items_per_room):
        rooms = []
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
                self.place_entities_in_room(new_room, entities, max_monsters_per_room, max_items_per_room)

                # append new room to list
                rooms.append(new_room)

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

    @staticmethod
    def place_entities_in_room(room_rect, entities, max_monsters_per_room, max_items_per_room):
        # get random number of monsters
        number_of_monsters = randint(0, max_monsters_per_room)
        number_of_items = randint(0, max_items_per_room)

        for i in range(number_of_monsters):
            # choose random location in room
            x = randint(room_rect.x1 + 1, room_rect.x2 - 1)
            y = randint(room_rect.y1 + 1, room_rect.y2 - 1)

            # make sure no monster is already in spot
            if not any([entity for entity in entities if entity.x == x and entity.y == y]):
                if randint(0, 100) < 80:  # Place orc
                    fighter_component = Fighter(hp=10, defense=0, power=3)
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
                    fighter_component = Fighter(hp=16, defense=1, power=4)
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
                item_chance = randint(0, 100)

                if item_chance < 70:  # Place health potion
                    # Randomly select strength of healing potion
                    potion_chance = randint(0, 100)
                    if potion_chance < 70:
                        heal_amount = 4
                        potion_name = "Measly Potion of Healing"
                    else:
                        heal_amount = 8
                        potion_name = "Adequate Potion of Healing"

                    item_component = Item(use_function=heal, amount=heal_amount)
                    item = Entity(
                        x,
                        y,
                        '!',
                        libtcod.violet,
                        potion_name,
                        render_order=RenderOrder.ITEM,
                        item=item_component
                    )
                elif item_chance < 80:  # Place fireball scroll
                    item_component = Item(
                        use_function=cast_fireball,
                        targeting=True,
                        targeting_message=Message("Left-click a target tile for fireball. Right-click or Esc to cancel.", libtcod.light_cyan),
                        damage=12,
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
                elif item_chance < 90:
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
                    item_component = Item(use_function=cast_lightning, damage=20, maximum_range=5)
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
