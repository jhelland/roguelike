
import libtcodpy as libtcod

from loader_functions.initialize_new_game import get_constants, get_game_variables
from loader_functions.data_loaders import load_game, save_game

from render_functions import clear_all, render_all
from input_handlers import handle_keys, handle_mouse, handle_main_menu_keys, get_main_menu_option_from_index, get_inventory_option_from_index, get_level_up_option_from_index
from game_states import GameStates
from game_messages import Message
from death_functions import kill_monster, kill_player
from fov_functions import recompute_fov, initialize_fov

from entity import get_blocking_entities_at_location

from menus import main_menu, message_box


def play_game(player,
              entities,
              game_map,
              message_log,
              game_state,
              window_main,
              ui_panel,
              constants,
              key,
              mouse):
    prev_game_state = game_state
    targeting_item = None  # Keep track of item requiring targeting that player attempts to use

    # Instantiate FOV variables
    fov_recompute = True
    fov_map = initialize_fov(game_map)

    # Make sure it's the player's turn before starting
    game_state = GameStates.PLAYER_TURN

    # Main game loop
    while not libtcod.console_is_window_closed():
        # Check for player input
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)

        # Get player FOV
        if fov_recompute:
            recompute_fov(
                fov_map,
                player.x,
                player.y,
                constants["fov_radius"],
                constants["fov_light_walls"],
                constants["fov_algorithm"]
            )

        # Render map, entities, player FOV
        menu_click_results = render_all(
            window_main,
            ui_panel,
            entities,
            game_map,
            fov_map,
            fov_recompute,
            message_log,
            constants["screen_width"],
            constants["screen_height"],
            constants["ui_panel_width"],
            constants["ui_panel_height"],
            constants["ui_panel_y"],
            mouse,
            constants["colors"],
            game_state
        )
        fov_recompute = False

        # Display rendered content
        libtcod.console_flush()

        # Clear entities for sake of updating positions.
        clear_all(window_main, entities)

        # Get user input and parse/handle it
        action = handle_keys(key, game_state)
        mouse_action = handle_mouse(mouse)

        move = action.get("move")  # player move
        fullscreen_key_pressed = action.get("fullscreen")
        wait = action.get("wait")  # don't move during turn
        pickup = action.get("pickup")  # pick up item
        show_inventory = action.get("show_inventory")
        inventory_index = action.get("inventory_index")
        drop_inventory = action.get("drop_inventory")
        take_stairs = action.get("take_stairs")
        level_up = action.get("level_up")
        show_character_screen = action.get("show_character_screen")
        exit_key_pressed = action.get("exit")

        left_click = mouse_action.get("left_click")
        right_click = mouse_action.get("right_click")

        # Handle results of inventory item click
        for result in menu_click_results:
            item_clicked = result.get("item_clicked")

            if item_clicked:
                option = get_inventory_option_from_index(item_clicked)
                option = dict(option, **get_level_up_option_from_index(item_clicked))  # extend dictionary

                inventory_index = option.get("inventory_index")
                level_up = option.get("level_up")

        # Handle player actions if it's their turn
        player_turn_results = []  # To store messages for results of player actions

        if move and game_state == GameStates.PLAYER_TURN:
            # Update player position
            dx, dy = move
            destination_x = player.x + dx
            destination_y = player.y + dy
            if not game_map.is_tile_blocked(destination_x, destination_y):
                # If monster is blocking target tile, attack it.
                # Otherwise, move to target tile.
                target = get_blocking_entities_at_location(entities, destination_x, destination_y)
                if target:
                    player_turn_results.extend(player.fighter.attack(target))
                else:
                    player.move(dx, dy)
                    fov_recompute = True

                game_state = GameStates.ENEMY_TURN  # End player's turn

        # Player waiting
        elif wait and game_state == GameStates.PLAYER_TURN:
            game_state = GameStates.ENEMY_TURN
            message_log.add_message(Message("You wait.", libtcod.white))

        # Player picks up item
        elif pickup and game_state == GameStates.PLAYER_TURN:
            for entity in entities:
                if entity.item and entity.x == player.x and entity.y == player.y:
                    pickup_results = player.inventory.add_item(entity)
                    player_turn_results.extend(pickup_results)
                    break
            else:
                message_log.add_message(Message("There is nothing here to pick up.", libtcod.yellow))

        if show_inventory:
            prev_game_state = game_state
            game_state = GameStates.SHOW_INVENTORY

        if drop_inventory:
            prev_game_state = game_state
            game_state = GameStates.DROP_INVENTORY

        # Handle using/dropping items in inventory
        if inventory_index is not None and \
                prev_game_state != GameStates.PLAYER_DEAD and \
                inventory_index < len(player.inventory.items):
            item = player.inventory.items[inventory_index]

            if game_state == GameStates.SHOW_INVENTORY:
                player_turn_results.extend(player.inventory.use_item(item, entities=entities, fov_map=fov_map))
            elif game_state == GameStates.DROP_INVENTORY:
                player_turn_results.extend(player.inventory.drop_item(item))

        # Handle player taking stairs down
        if take_stairs and game_state == GameStates.PLAYER_TURN:
            for entity in entities:
                if entity.stairs and entity.x == player.x and entity.y == player.y:
                    entities = game_map.next_floor(player, message_log, constants)
                    fov_map = initialize_fov(game_map)
                    fov_recompute = True
                    libtcod.console_clear(window_main)
                    break
            else:
                message_log.add_message(Message("There are no stairs here.", libtcod.yellow))

        if level_up:
            if level_up == "hp":
                player.fighter.base_max_hp += 20
                player.fighter.hp += 20
            elif level_up == "str":
                player.fighter.base_power += 1
            elif level_up == "def":
                player.fighter.base_defense += 1

            game_state = prev_game_state

        if show_character_screen:
            prev_game_state = game_state
            game_state = GameStates.CHARACTER_SCREEN

        # Targeting mode for item.
        # Left click selects target tile, right click cancels targeting.
        if game_state == GameStates.TARGETING:
            if left_click:
                target_x, target_y = left_click

                item_use_results = player.inventory.use_item(targeting_item, entities=entities, fov_map=fov_map,
                                                             target_x=target_x, target_y=target_y)
                player_turn_results.extend(item_use_results)
            elif right_click:
                player_turn_results.append({"targeting_cancelled": True})

        # Enter fullscreen mode
        if fullscreen_key_pressed:
            libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

        # Exit events
        if exit_key_pressed:
            # Exit menu
            if game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY, GameStates.CHARACTER_SCREEN):
                game_state = prev_game_state

            # Exit targeting mode
            elif game_state == GameStates.TARGETING:
                player_turn_results.append({"targeting_cancelled": True})

            # Exit game
            else:
                # Save before exiting
                save_game(player, entities, game_map, message_log, game_state)
                return True

        # Handle results of player's turn
        # (!) Must go after all changes to player_turn_results
        for result in player_turn_results:
            message = result.get("message")
            dead_entity = result.get("dead")
            item_added = result.get("item_added")
            item_consumed = result.get("item_consumed")
            item_dropped = result.get("item_dropped")
            equip = result.get("equip")
            targeting = result.get("targeting")
            targeting_cancelled = result.get("targeting_cancelled")
            xp = result.get("xp")

            if message:
                message_log.add_message(message)

            # Handle player death and/or monster death
            if dead_entity:
                if dead_entity == player:
                    message, game_state = kill_player(dead_entity)
                else:
                    message = kill_monster(dead_entity)

                message_log.add_message(message)

            # If player picks up item, remove it from entity list and end player turn
            if item_added:
                entities.remove(item_added)
                game_state = GameStates.ENEMY_TURN

            # If player drops item, end turn
            if item_dropped:
                print("item dropped")
                entities.append(item_dropped)
                game_state = GameStates.ENEMY_TURN

            if equip:
                equip_results = player.equipment.toggle_equip(equip)

                for equip_result in equip_results:
                    equipped = equip_result.get("equipped")
                    unequipped = equip_result.get("unequipped")

                    if equipped:
                        message_log.add_message(Message("You equipped the {0}.".format(equipped.name)))

                    if unequipped:
                        message_log.add_message(Message("You unequipped the {0}.".format(unequipped.name)))

                    game_state = GameStates.ENEMY_TURN

            # If player uses an item, end turn
            if item_consumed:
                game_state = GameStates.ENEMY_TURN

            if targeting_cancelled:
                game_state = prev_game_state
                prev_game_state = GameStates.PLAYER_TURN
                message_log.add_message(Message("Targeting cancelled."))

            if targeting:
                prev_game_state = game_state
                game_state = GameStates.TARGETING

                targeting_item = targeting

                message_log.add_message(targeting_item.item.targeting_message)

            if xp:
                leveled_up = player.level.add_xp(xp)
                message_log.add_message(Message("You gain {0} experience points!".format(xp)))

                if leveled_up:
                    message_log.add_message(Message("You feel power surge through you! Welcome to level {0}.".format(player.level.current_level) + '!', libtcod.yellow))
                    prev_game_state = game_state
                    game_state = GameStates.LEVEL_UP

        # Handle enemy actions if it's their turn
        if game_state == GameStates.ENEMY_TURN:
            for entity in entities:
                if entity.ai:  # Filters out player since player doesn't have AI component
                    # Do A* pathing towards player if monster is within player FOV
                    enemy_turn_results = entity.ai.take_turn(player, fov_map, game_map, entities)

                    # Handle results of enemy action
                    for result in enemy_turn_results:
                        message = result.get("message")
                        dead_entity = result.get("dead")

                        if message:
                            message_log.add_message(message)

                        # Handle player death and/or monster death
                        if dead_entity:
                            if dead_entity == player:
                                message, game_state = kill_player(dead_entity)
                            else:
                                message = kill_monster(dead_entity)

                            message_log.add_message(message)

                            # Stop handling enemy turns if player has died.
                            if game_state == GameStates.PLAYER_DEAD:
                                break

                # Skip setting turn back to player if player is dead
                if game_state == GameStates.PLAYER_DEAD:
                    break

            # End enemy turns
            else:
                game_state = GameStates.PLAYER_TURN


def main():
    constants = get_constants()

    # Instantiate main window
    libtcod.console_set_custom_font("arial10x10.png", libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
    libtcod.console_init_root(constants["screen_width"], constants["screen_height"], constants["window_title"], False)

    # Instantiate offscreen window for drawing
    window_main = libtcod.console_new(constants["screen_width"], constants["screen_height"])

    # Instantiate UI window
    ui_panel = libtcod.console_new(constants["screen_width"], constants["ui_panel_height"])

    player = None
    entities = []
    game_map = None
    message_log = None
    game_state = None

    show_main_menu = True
    show_load_error_message = False

    main_menu_background_image = libtcod.image_load("ainsley.png")  #("menu_background.png")

    key = libtcod.Key()
    mouse = libtcod.Mouse()

    while not libtcod.console_is_window_closed():
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)

        if show_main_menu:
            action_keyboard = handle_main_menu_keys(key)

            # .get() returns None if not found
            new_game = bool(action_keyboard.get("new_game"))
            load_saved_game = bool(action_keyboard.get("load_game"))
            exit_game = bool(action_keyboard.get("exit"))

            menu_click_results = main_menu(
                window_main,
                main_menu_background_image,
                constants["screen_width"],
                constants["screen_height"],
                mouse
            )

            # Handle results of mouse click on menu item
            for result in menu_click_results:
                item_clicked = chr(result.get("item_clicked"))

                if item_clicked:
                    action_mouse = get_main_menu_option_from_index(item_clicked)

                    new_game |= bool(action_mouse.get("new_game"))
                    load_saved_game |= bool(action_mouse.get("load_game"))
                    exit_game |= bool(action_mouse.get("exit"))

            if show_load_error_message:
                message_box(
                    window_main,
                    "No save game to load",
                    50,
                    constants["screen_width"],
                    constants["screen_height"]
                )

            libtcod.console_flush()

            if show_load_error_message and (new_game or load_saved_game or exit_game):
                show_load_error_message = False
            elif new_game:
                player, entities, game_map, message_log, game_state = get_game_variables(constants)
                game_state = GameStates.PLAYER_TURN

                show_main_menu = False
            elif load_saved_game:
                try:
                    player, entities, game_map, message_log, game_state = load_game()
                    show_main_menu = False
                except FileNotFoundError:
                    show_load_error_message = True
            elif exit_game:
                break

        else:
            libtcod.console_clear(window_main)
            play_game(
                player,
                entities,
                game_map,
                message_log,
                game_state,
                window_main,
                ui_panel,
                constants,
                key,
                mouse
            )
            show_main_menu = True


if __name__ == "__main__":
     main()
