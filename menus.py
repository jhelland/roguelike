
import libtcodpy as libtcod


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
                   inventory,
                   inventory_width,
                   screen_width,
                   screen_height):
    # Show a menu with each item of the inventory as an option
    if len(inventory.items) == 0:
        options = ["Inventory is empty."]
    else:
        options = [item.name for item in inventory.items]

    menu(window, header, options, inventory_width, screen_width, screen_height)


def main_menu(window,
              background_image,
              screen_width,
              screen_height):
    libtcod.image_blit_2x(background_image, 0, 0, 0)

    libtcod.console_set_default_foreground(0, libtcod.black)
    libtcod.console_print_ex(
        0,
        screen_width // 2 - 7,
        screen_height // 2 - 4,
        libtcod.BKGND_NONE,
        libtcod.CENTER,
        "By jhelland"
    )
    menu(
        window,
        "",
        ["Play a new game", "Continue last game", "Quit"],
        24,
        screen_width,
        screen_height
    )


def message_box(window, header, width, screen_width, screen_height):
    menu(window, header, [], width, screen_width, screen_height)
