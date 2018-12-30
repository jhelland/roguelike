
import libtcodpy as libtcod

from game_states import GameStates


def handle_keys(key, game_state):
    if game_state == GameStates.PLAYER_TURN:
        return handle_player_turn_keys(key)
    elif game_state == GameStates.PLAYER_DEAD:
        return handle_player_dead_keys(key)
    elif game_state == GameStates.TARGETING:
        return handle_targeting_keys(key)
    elif game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY):
        return handle_inventory_keys(key)
    elif game_state == GameStates.LEVEL_UP:
        return handle_level_up_menu_keys(key)
    elif game_state == GameStates.CHARACTER_SCREEN:
        return handle_character_screen(key)

    return {}


def handle_player_turn_keys(key):
    key_char = chr(key.c)

    # Toggle full screen
    if key.lalt and key_char == 'f':  # Mac: lalt == option
        return {"fullscreen": True}

    # Movement keys
    if key.vk == libtcod.KEY_UP or key_char == 'k':         # north
        return {"move": (0, -1)}
    elif key.vk == libtcod.KEY_DOWN or key_char == 'j':     # south
        return {"move": (0, 1)}
    elif key.vk == libtcod.KEY_LEFT or key_char == 'h':     # west
        return {"move": (-1, 0)}
    elif key.vk == libtcod.KEY_RIGHT or key_char == 'l':    # east
        return {"move": (1, 0)}
    elif key_char == 'y':                                   # north-west
        return {"move": (-1, -1)}
    elif key_char == 'u':                                   # north-east
        return {"move": (1, -1)}
    elif key_char == 'b':                                   # south-west
        return {"move": (-1, 1)}
    elif key_char == 'n':                                   # south-east
        return {"move": (1, 1)}
    elif key_char == ' ':                                   # wait
        return {"wait": True}

    # Action keys
    if key_char == 'g':
        return {"pickup": True}
    elif key_char == 'i':
        return {"show_inventory": True}
    elif key_char == 'd':
        return {"drop_inventory": True}
    elif key.vk == libtcod.KEY_ENTER or (key.shift and key_char == '.'):
        return {"take_stairs": True}

    # Toggle character stats screen
    elif key_char == 'c':
        return {"show_character_screen": True}

    # Exit key
    if key.vk == libtcod.KEY_ESCAPE:
        return {"exit": True}

    # No key was pressed
    return {}


def handle_targeting_keys(key):
    if key.vk == libtcod.KEY_ESCAPE:
        return {"exit": True}

    return {}


def handle_player_dead_keys(key):
    key_char = chr(key.c)

    if key_char == 'i':  # Show inventory
        return {"show_inventory": True}

    if key.lalt and key_char == 'f':  # Toggle fullscreen
        return {"fullscreen": True}
    elif key.vk == libtcod.KEY_ESCAPE:  # Exit menu
        return {"exit": True}

    return {}


def handle_inventory_keys(key):
    result = get_inventory_option_from_index(key.c)

    if key.lalt and chr(key.c) == 'f':  # toggle fullscreen
        result = {"fullscreen": True}
    elif key.vk == libtcod.KEY_ESCAPE or key.c == ord('i'):  # exit menu
        result = {"exit": True}

    return result


def get_inventory_option_from_index(index):
    index -= ord('a')
    if index >= 0:
        return {"inventory_index": index}

    return {}


def handle_main_menu_keys(key):
    key_char = chr(key.c)

    result = get_main_menu_option_from_index(key_char)

    if key.vk == libtcod.KEY_ESCAPE:
        return {"exit": True}

    return result


def get_main_menu_option_from_index(index):
    if index == 'a':
        return {"new_game": True}
    elif index == 'b':
        return {"load_game": True}
    elif index == 'c':
        return {"exit": True}

    return {}


def handle_level_up_menu_keys(key):
    result = {}

    if key:
        key_char = chr(key.c)
        result = get_level_up_option_from_index(key_char)

    return result


def get_level_up_option_from_index(index):
    index_ = index
    if type(index) != str:
        index_ = chr(index)

    if index_ == 'a':
        return {"level_up": "hp"}
    elif index_ == 'b':
        return {"level_up": "str"}
    elif index_ == 'c':
        return {"level_up": "def"}

    return {}


def handle_character_screen(key):
    if key.vk == libtcod.KEY_ESCAPE or key.c == ord('c'):
        return {"exit": True}

    return {}


def handle_mouse(mouse):
    x, y = mouse.cx, mouse.cy

    if mouse.lbutton_pressed:
        return {"left_click": (x, y)}
    elif mouse.rbutton_pressed:
        return {"right_click": (x, y)}

    return {}
