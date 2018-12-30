
import math
import libtcodpy as libtcod

from render_functions import RenderOrder

from components.item import Item


class Entity:
    """
    Generic object representing players, enemies, items, etc.
    """
    def __init__(self,
                 x,
                 y,
                 char,
                 color,
                 name,
                 blocks=False,
                 render_order=RenderOrder.CORPSE,
                 fighter=None,
                 ai=None,
                 item=None,
                 inventory=None,
                 stairs=None,
                 level=None,
                 equipment=None,
                 equippable=None):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.blocks = blocks
        self.render_order = render_order
        self.fighter = fighter
        self.ai = ai
        self.item = item
        self.inventory = inventory
        self.stairs = stairs
        self.level = level
        self.equipment = equipment
        self.equippable = equippable

        if self.fighter:
            self.fighter.owner = self

        if self.ai:
            self.ai.owner = self

        if self.item:
            self.item.owner = self

        if self.inventory:
            self.inventory.owner = self

        if self.stairs:
            self.stairs.owner = self

        if self.level:
            self.level.owner = self

        if self.equipment:
            self.equipment.owner = self

        if self.equippable:
            self.equippable.owner = self

            if not self.item:
                item = Item()
                self.item = item
                self.item.owner = self

    def move(self, dx, dy):
        # move entity specified amount
        self.x += dx
        self.y += dy

    def move_towards(self, target_x, target_y, game_map, entities):
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx**2 + dy**2)

        dx = int(round(dx / distance))
        dy = int(round(dy / distance))

        if not (game_map.is_tile_blocked(self.x + dx, self.y + dy) or
                get_blocking_entities_at_location(entities, self.x + dx, self.y + dy)):
            self.move(dx, dy)

    def move_astar(self, target, entities, game_map):
        # create FOV map that has dimensions of game map
        fov = libtcod.map_new(game_map.width, game_map.height)

        # scan current map each turn and set all walls to be blocking
        for y in range(game_map.height):
            for x in range(game_map.width):
                libtcod.map_set_properties(
                    fov,
                    x,
                    y,
                    not game_map.tiles[x][y].block_sight,
                    not game_map.tiles[x][y].blocked
                )

        # Scan all objects to see if something needs to be navigated around.
        # Also check that the object isn't self or the target.
        # Ignore situation where self is next to target -- AI class handles this.
        for entity in entities:
            if entity.blocks and entity != self and entity != target:
                libtcod.map_set_properties(fov, entity.x, entity.y, True, False)  # set wall so it must be navigated around

        # Allocate A* path.
        # 1.41 is the normalized diagonal cost of moving. If diagonal movement is not allowed, then set to 0.
        my_path = libtcod.path_new_using_map(fov, 1.41)

        # Compute the path between self and target coordinates
        libtcod.path_compute(my_path, self.x, self.y, target.x, target.y)

        # Check if path exists and is shorter than 25 tiles.
        # Keep path size low to prevent monsters from running around the map.
        if not libtcod.path_is_empty(my_path) and libtcod.path_size(my_path) < 25:
            # Find the next coordinates in computed full path.
            x, y = libtcod.path_walk(my_path, True)
            if x or y:
                # Set self's coordinates to next path tile
                self.x = x
                self.y = y
        else:
            # Keep old move function as a backup e.g. if something blocks a doorway,
            # self will still move towards target.
            self.move_towards(target.x, target.y, game_map, entities)

        # delete path to free memory
        libtcod.path_delete(my_path)

    def distance_to(self, other):
        dx = other.x - self.x
        dy = other.y - self.y
        return math.sqrt(dx**2 + dy**2)

    def distance_to_point(self, x, y):
        dx = x - self.x
        dy = y - self.y
        return math.sqrt(dx**2 + dy**2)


def get_blocking_entities_at_location(entities, location_x, location_y):
    for entity in entities:
        if entity.blocks and entity.x == location_x and entity.y == location_y:
            return entity

    return None
