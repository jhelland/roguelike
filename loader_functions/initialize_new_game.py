
import libtcodpy as libtcod

from entity import Entity
from components.fighter import Fighter
from components.inventory import Inventory

from game_messages import MessageLog

from game_states import GameStates

from map_objects.game_map import GameMap

from render_functions import RenderOrder


def get_constants():
    window_title = "Roguelike"

    # window/player view parameters
    screen_width = 80
    screen_height = 50

    fov_algorithm = libtcod.FOV_SHADOW
    fov_light_walls = True
    fov_radius = 10
    fov_recompute = True

    # UI panel parameters
    ui_panel_width = 20
    ui_panel_height = 7
    ui_panel_y = screen_height - ui_panel_height

    # Message log parameters
    message_panel_x = ui_panel_width + 2
    message_panel_width = screen_width - ui_panel_width - 2
    message_panel_height = ui_panel_height - 1

    # World parameters
    map_width = 80
    map_height = 43

    room_max_size = 15
    room_min_size = 10
    max_rooms = 30

    max_monsters_per_room = 3
    max_items_per_room = 50

    colors = {
        'dark_wall': libtcod.Color(0, 0, 100),
        'dark_ground': libtcod.Color(50, 50, 150),
        'light_wall': libtcod.Color(130, 110, 50),
        'light_ground': libtcod.Color(200, 180, 50)
    }

    constants = {
        "window_title": window_title,
        "screen_width": screen_width,
        "screen_height": screen_height,
        "fov_algorithm": fov_algorithm,
        "fov_light_walls": fov_light_walls,
        "fov_radius": fov_radius,
        "fov_recompute": fov_recompute,
        "ui_panel_width": ui_panel_width,
        "ui_panel_height": ui_panel_height,
        "ui_panel_y": ui_panel_y,
        "message_panel_x": message_panel_x,
        "message_panel_width": message_panel_width,
        "message_panel_height": message_panel_height,
        "map_width": map_width,
        "map_height": map_height,
        "room_max_size": room_max_size,
        "room_min_size": room_min_size,
        "max_rooms": max_rooms,
        "max_monsters_per_room": max_monsters_per_room,
        "max_items_per_room": max_items_per_room,
        "colors": colors
    }

    return constants


def get_game_variables(constants):
    # instantiate entities
    fighter_component = Fighter(hp=30, defense=2, power=5)
    inventory_component = Inventory(26)
    player = Entity(
        0,
        0,
        '@',
        libtcod.white,
        "Player",
        blocks=True,
        render_order=RenderOrder.ACTOR,
        fighter=fighter_component,
        inventory=inventory_component
    )
    entities = [player]

    # Instantiate world map.
    # Monsters will be added to entities upon map generation.
    game_map = GameMap(constants["map_width"], constants["map_height"])
    game_map.make_map(
        constants["max_rooms"],
        constants["room_min_size"],
        constants["room_max_size"],
        constants["map_width"],
        constants["map_height"],
        player,
        entities,
        constants["max_monsters_per_room"],
        constants["max_items_per_room"]
    )

    message_log = MessageLog(constants["message_panel_x"], constants["message_panel_width"], constants["message_panel_height"])

    # first turn in world should be player's
    game_state = GameStates.PLAYER_TURN

    return player, entities, game_map, message_log, game_state
