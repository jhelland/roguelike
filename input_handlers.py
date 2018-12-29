
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

    return {}


def handle_player_turn_keys(key):
    key_char = chr(key.c)

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

    # Toggle full screen
    if key.vk == libtcod.KEY_ENTER and key.lalt:  # Mac: lalt == option
        return {"fullscreen": True}

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

    if key.vk == libtcod.KEY_ENTER and key.lalt:  # Toggle fullscreen
        return {"fullscreen": True}
    elif key.vk == libtcod.KEY_ESCAPE:  # Exit menu
        return {"exit": True}

    return {}


def handle_inventory_keys(key):
    index = key.c - ord('a')

    if index >= 0:  # use inventory item
        return {"inventory_index": index}

    if key.vk == libtcod.KEY_ENTER and key.lalt:  # toggle fullscreen
        return {"fullscreen": True}
    elif key.vk == libtcod.KEY_ESCAPE:  # exit menu
        return {"exit": True}

    return {}


def handle_main_menu(key):
    key_char = chr(key.c)

    if key_char == 'a':
        return {"new_game": True}
    elif key_char == 'b':
        return {"load_game": True}
    elif key_char == 'c' or key.vk == libtcod.KEY_ESCAPE:
        return {"exit": True}

    return {}


def handle_mouse(mouse):
    x, y = mouse.cx, mouse.cy

    if mouse.lbutton_pressed:
        return {"left_click": (x, y)}
    elif mouse.rbutton_pressed:
        return {"right_click": (x, y)}

    return {}
