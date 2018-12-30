
import libtcodpy as libtcod


def menu_clickable(window,
                   header,
                   options,
                   width,
                   screen_width,
                   screen_height,
                   mouse):
    if len(options) > 26:
        raise ValueError("Cannot have menu with more than 26 options")

    results = []

    # Calculate total height for the header (after auto-wrap) and one line per option
    header_height = libtcod.console_get_height_rect(window, 0, 0, width, screen_height, header)
    if header == "":
        header_height = 0
    height = len(options) + header_height

    # Create an off-screen console that represents the menu's window
    window_menu = libtcod.console_new(width, height)

    # Print the header with auto-wrap
    libtcod.console_set_default_foreground(window_menu, libtcod.white)
    libtcod.console_print_rect_ex(window_menu, 0, 0, width, height, libtcod.BKGND_NONE, libtcod.LEFT, header)

    # Print all the options
    y = header_height
    letter_index = ord('a')
    return_letter_index = letter_index
    menu_clicked = False

    mouse_x, mouse_y = mouse.cx, mouse.cy
    mouse_offset_x = screen_width // 2 - width // 2  # Left edge of menu
    mouse_offset_y = screen_height // 2 - height // 2

    for option_text in options:
        if option_text == "Inventory is empty.":
            libtcod.console_print_ex(window_menu, 0, y, libtcod.BKGND_NONE, libtcod.LEFT, option_text)
            break
        else:
            text = "(" + chr(letter_index) + ") " + option_text

            # Highlight menu option if mouse hovers over it
            if mouse_x and mouse_y and\
                    (mouse_offset_x <= mouse_x < mouse_offset_x + width and
                     mouse_offset_y + y <= mouse_y < min(mouse_offset_y + y + 1, mouse_offset_y + height)):
                if mouse.lbutton_pressed:
                    menu_clicked = True
                    return_letter_index = letter_index
                libtcod.console_set_default_foreground(window_menu, libtcod.green)
                libtcod.console_print_ex(window_menu, 0, y, libtcod.BKGND_NONE, libtcod.LEFT, text)
            else:
                libtcod.console_set_default_foreground(window_menu, libtcod.white)
                libtcod.console_print_ex(window_menu, 0, y, libtcod.BKGND_NONE, libtcod.LEFT, text)
            y += 1
            letter_index += 1

    # Blit contents of menu window to main window
    x = screen_width // 2 - width // 2
    y = screen_height // 2 - height // 2
    libtcod.console_blit(window_menu, 0, 0, width, height, 0, x, y, 1.0, 0.7)

    if menu_clicked:
        results.append({"item_clicked": return_letter_index})

    return results


def menu(window,
         header,
         options,
         width,
         screen_width,
         screen_height):
    if len(options) > 26:
        raise ValueError("Cannot have menu with more than 26 options")

    # Calculate total height for the header (after auto-wrap) and one line per option
    header_height = libtcod.console_get_height_rect(window, 0, 0, width, screen_height, header)
    height = len(options) + header_height

    # Create an off-screen console that represents the menu's window
    window_menu = libtcod.console_new(width, height)

    # Print the header with auto-wrap
    libtcod.console_set_default_foreground(window_menu, libtcod.white)
    libtcod.console_print_rect_ex(window_menu, 0, 0, width, height, libtcod.BKGND_NONE, libtcod.LEFT, header)

    # Print all the options
    y = header_height
    letter_index = ord('a')

    for option_text in options:
        if option_text == "Inventory is empty.":
            libtcod.console_print_ex(window_menu, 0, y, libtcod.BKGND_NONE, libtcod.LEFT, option_text)
            break
        else:
            text = "(" + chr(letter_index) + ") " + option_text
            libtcod.console_print_ex(window_menu, 0, y, libtcod.BKGND_NONE, libtcod.LEFT, text)
            y += 1
            letter_index += 1

    # Blit contents of menu window to main window
    x = screen_width // 2 - width // 2
    y = screen_height // 2 - height // 2
    libtcod.console_blit(window_menu, 0, 0, width, height, 0, x, y, 1.0, 0.7)


def inventory_menu(window,
                   header,
                   player,
                   inventory_width,
                   screen_width,
                   screen_height,
                   mouse):
    # Show a menu with each item of the inventory as an option
    if len(player.inventory.items) == 0:
        options = ["Inventory is empty."]
    else:
        options = []

        for item in player.inventory.items:
            if player.equipment.main_hand == item:
                options.append("{0} (main hand)".format(item.name))
            elif player.equipment.off_hand == item:
                options.append("{0} (off-hand)".format(item.name))
            else:
                options.append(item.name)

    return menu_clickable(
        window,
        header,
        options,
        inventory_width,
        screen_width,
        screen_height,
        mouse
    )


def main_menu(window,
              background_image,
              screen_width,
              screen_height,
              mouse):
    libtcod.image_blit_2x(background_image, 0, 0, 0)

    libtcod.console_set_default_foreground(0, libtcod.black)
    libtcod.console_print_ex(
        0,
        screen_width // 2 - 7,
        screen_height // 2 - 4,
        libtcod.BKGND_NONE,
        libtcod.CENTER,
        "You look hungry"
    )
    return menu_clickable(
        window,
        "",
        ["Play a new game", "Continue last game", "Quit"],
        24,
        screen_width,
        screen_height,
        mouse
    )


def level_up_menu(window,
                  header,
                  player,
                  menu_width,
                  screen_width,
                  screen_height,
                  mouse):
    options = ["Constitution (+20 HP, from {0})".format(player.fighter.max_hp),
               "Strength (+1 attack, from {0})".format(player.fighter.power),
               "Agility (+1 defense, from {0})".format(player.fighter.defense)]

    return menu_clickable(
        window,
        header,
        options,
        menu_width,
        screen_width,
        screen_height,
        mouse
    )


def character_screen_menu(player,
                          character_screen_width,
                          character_screen_height,
                          screen_width,
                          screen_height):
    window = libtcod.console_new(character_screen_width, character_screen_height)

    libtcod.console_set_default_foreground(window, libtcod.white)

    libtcod.console_print_rect_ex(window, 0, 1, character_screen_width, character_screen_height, libtcod.BKGND_NONE, libtcod.LEFT, 'Character Information')
    libtcod.console_print_rect_ex(window, 0, 2, character_screen_width, character_screen_height, libtcod.BKGND_NONE, libtcod.LEFT, 'Level: {0}'.format(player.level.current_level))
    libtcod.console_print_rect_ex(window, 0, 3, character_screen_width, character_screen_height, libtcod.BKGND_NONE, libtcod.LEFT, 'Experience: {0}'.format(player.level.current_xp))
    libtcod.console_print_rect_ex(window, 0, 4, character_screen_width, character_screen_height, libtcod.BKGND_NONE, libtcod.LEFT, 'Experience to Level: {0}'.format(player.level.experience_to_next_level))
    libtcod.console_print_rect_ex(window, 0, 6, character_screen_width, character_screen_height, libtcod.BKGND_NONE, libtcod.LEFT, 'Maximum HP: {0}'.format(player.fighter.max_hp))
    libtcod.console_print_rect_ex(window, 0, 7, character_screen_width, character_screen_height, libtcod.BKGND_NONE, libtcod.LEFT, 'Attack: {0}'.format(player.fighter.power))
    libtcod.console_print_rect_ex(window, 0, 8, character_screen_width, character_screen_height, libtcod.BKGND_NONE, libtcod.LEFT, 'Defense: {0}'.format(player.fighter.defense))

    x = screen_width // 2 - character_screen_width // 2
    y = screen_height // 2 - character_screen_height // 2
    libtcod.console_blit(window, 0, 0, character_screen_width, character_screen_height, 0, x, y, 1.0, 0.7)


def message_box(window, header, width, screen_width, screen_height):
    menu(window, header, [], width, screen_width, screen_height)
