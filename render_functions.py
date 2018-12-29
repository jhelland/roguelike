
import libtcodpy as libtcod
from enum import Enum

from game_states import GameStates
from menus import inventory_menu


class RenderOrder(Enum):
    CORPSE = 1
    ITEM = 2
    ACTOR = 3


def get_names_under_mouse(mouse, entities, fov_map):
    x, y = mouse.cx, mouse.cy

    # Get names of entities at mouse position within player FOV
    names = [entity.name for entity in entities if
             entity.x == x and entity.y == y and
             libtcod.map_is_in_fov(fov_map, entity.x, entity.y)]
    names = ', '.join(names)

    return names.capitalize()


def render_bar(panel,
               x,
               y,
               total_width,
               name,
               value,
               maximum,
               bar_color,
               back_color):
    bar_width = int(float(value) / maximum * total_width)

    libtcod.console_set_default_background(panel, back_color)
    libtcod.console_rect(panel, x, y, total_width, 1, False, libtcod.BKGND_SCREEN)

    libtcod.console_set_default_background(panel, bar_color)
    if bar_width > 0:
        libtcod.console_rect(panel, x, y, bar_width, 1, False, libtcod.BKGND_SCREEN)

    libtcod.console_set_default_foreground(panel, libtcod.white)
    libtcod.console_print_ex(
        panel,
        x + total_width // 2,
        y,
        libtcod.BKGND_NONE,
        libtcod.CENTER,
        "{0}: {1}/{2}".format(name, value, maximum)
    )


def render_all(window,
               ui_panel,
               entities,
               game_map,
               fov_map,
               fov_recompute,
               message_log,
               screen_width,
               screen_height,
               ui_panel_width,
               ui_panel_height,
               ui_panel_y,
               mouse,
               colors,
               game_state):
    # draw game map
    if fov_recompute:
        for y in range(game_map.height):
            for x in range(game_map.width):
                visible = libtcod.map_is_in_fov(fov_map, x, y)
                wall = game_map.tiles[x][y].block_sight

                if visible:
                    if wall:
                        libtcod.console_set_char_background(window, x, y, colors.get("light_wall"), libtcod.BKGND_SET)
                        libtcod.console_set_char_foreground(window, x, y, libtcod.white)
                        libtcod.console_set_char(window, x, y, '#')
                    else:
                        libtcod.console_set_char_background(window, x, y, colors.get("light_ground"), libtcod.BKGND_SET)
                        libtcod.console_set_char_foreground(window, x, y, libtcod.white)
                        libtcod.console_set_char(window, x, y, '.')

                    game_map.tiles[x][y].explored = True

                elif game_map.tiles[x][y].explored:
                    if wall:
                        libtcod.console_set_char_background(window, x, y, colors.get("dark_wall"), libtcod.BKGND_SET)
                        libtcod.console_set_char_foreground(window, x, y, libtcod.light_gray)
                        libtcod.console_set_char(window, x, y, '#')
                    else:
                        libtcod.console_set_char_background(window, x, y, colors.get("dark_ground"), libtcod.BKGND_SET)
                        libtcod.console_set_char_foreground(window, x, y, libtcod.lighter_gray)
                        libtcod.console_set_char(window, x, y, '.')

    # get entities in rendering order
    entities_in_render_order = sorted(entities, key=lambda x: x.render_order.value)

    # Draw all entities in rendering order e.g. corpses should be below player.
    for entity in entities_in_render_order:
        draw_entity(window, entity, fov_map)

    # Blit offscreen window to main window
    libtcod.console_blit(window, 0, 0, screen_width, screen_height, 0, 0, 0)

    # Prepare offscreen UI panel for drawing
    player = entities[0]  # first entity is always player
    libtcod.console_set_default_background(ui_panel, libtcod.black)
    libtcod.console_clear(ui_panel)

    # Draw event message log to offscreen UI panel
    for y, message in enumerate(message_log.messages):  # Draw message log
        libtcod.console_set_default_foreground(ui_panel, message.color)
        libtcod.console_print_ex(
            ui_panel,
            message_log.x,
            y + 1,
            libtcod.BKGND_NONE,
            libtcod.LEFT,
            message.text
        )

    # Draw player HP bar to offscreen UI panel
    render_bar(
        ui_panel,
        1,
        1,
        ui_panel_width,
        "HP",
        player.fighter.hp,
        player.fighter.max_hp,
        libtcod.light_red,
        libtcod.darker_red
    )

    # Draw entity name at mouse position to offscreen UI panel
    libtcod.console_set_default_foreground(ui_panel, libtcod.light_gray)
    libtcod.console_print_ex(
        ui_panel,
        1,
        0,
        libtcod.BKGND_NONE,
        libtcod.LEFT,
        get_names_under_mouse(mouse, entities, fov_map)
    )

    # Blit UI panel to main window
    libtcod.console_blit(
        ui_panel,
        0,
        0,
        screen_width,
        ui_panel_height,
        0,
        0,
        ui_panel_y
    )

    if game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY):
        if game_state == GameStates.SHOW_INVENTORY:
            inventory_header = "Press the key next to item to use it. Press Esc to cancel.\n"
        else:
            inventory_header = "Press the key next to item to drop it. Press Esc to cancel.\n"

        inventory_menu(
            window,
            inventory_header,
            player.inventory,
            50,
            screen_width,
            screen_height
        )


def draw_entity(window, entity, fov_map):
    if libtcod.map_is_in_fov(fov_map, entity.x, entity.y):
        libtcod.console_set_default_foreground(window, entity.color)
        libtcod.console_put_char(window, entity.x, entity.y, entity.char, libtcod.BKGND_NONE)


def clear_all(window, entities):
    # clear all entities from window
    for entity in entities:
        clear_entity(window, entity)


def clear_entity(window, entity):
    # draw blank character over location of entity character
    libtcod.console_put_char(window, entity.x, entity.y, ' ', libtcod.BKGND_NONE)
