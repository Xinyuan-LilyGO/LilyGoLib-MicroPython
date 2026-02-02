import lvgl as lv
import time
import keypad
from machine import Pin, I2C

recreate_main_page = None
encoder = None
i2c = I2C(0, scl=Pin(2), sda=Pin(3), freq=400000)
kb = keypad.TCA8418(i2c)
kb.setup_keypad()


def set_references(recreate_func, encoder_obj=None):
    global recreate_main_page, encoder
    recreate_main_page = recreate_func
    if encoder_obj is not None:
        encoder = encoder_obj

def keyboard():
    # Clear all current screen elements
    scr = lv.screen_active()
    # Remove all children from the screen
    while True:
        child = scr.get_child(0)
        if child is None:
            break
        child.delete()
    
    # Create the color object for screen test
    color_obj = lv.obj(scr)
    color_obj.set_size(480, 320)  # Match screen size after rotation
    color_obj.align(lv.ALIGN.CENTER, 0, 0)
    
    # Create inversion style similar to images
    inv_style = lv.style_t()
    inv_style.init()
    inv_style.set_bg_opa(lv.OPA.COVER)
    inv_style.set_blend_mode(lv.BLEND_MODE.DIFFERENCE)
    color_obj.add_style(inv_style, 0)
    
    color_obj.set_style_bg_color(lv.color_hex(0xffffff), 0)
    
    # Create a separate selection box object that will overlay on top of items
    selection_box = lv.obj(scr)
    selection_box.set_style_border_width(4, 0)  # Thick white border
    selection_box.set_style_border_color(lv.color_hex(0xffffff), 0)
    selection_box.set_style_border_opa(lv.OPA.COVER, 0)
    selection_box.set_style_bg_opa(lv.OPA.TRANSP, 0)  # Transparent background
    selection_box.set_style_radius(8, 0)  # 8 pixel rounded corners to match input box
    selection_box.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)  # Disable scrollbar

    # Create labels for each selection item (no containers needed)
    selection_items = []
    item_positions = []
    item_sizes = []  # Store different sizes for selection box

    # Item 0: Back button (lv.SYMBOL.LEFT)
    symbol_left_label = lv.label(scr)
    symbol_left_label.set_text(lv.SYMBOL.LEFT)
    symbol_left_label.set_style_text_font(lv.font_montserrat_20, 0)
    symbol_left_label.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    symbol_left_label.set_pos(20, 55)
    selection_items.append(symbol_left_label)

    item_positions.append((12, 50))  # Adjusted position: left 3px total, up 4px total
    item_sizes.append((30, 30))  # Smaller size for back button

    # Add middle rectangle area (input box)
    middle_rect = lv.obj(scr)
    middle_rect.set_size(430, 100)
    middle_rect.set_pos(25, 90)
    middle_rect.set_style_bg_color(lv.color_hex(0x000000), 0)
    middle_rect.set_style_border_width(2, 0)
    middle_rect.set_style_border_color(lv.color_hex(0xffffff), 0)
    middle_rect.set_style_radius(8, 0)  # 8 pixel rounded corners

    # Enable scrolling for the container
    middle_rect.set_scrollbar_mode(lv.SCROLLBAR_MODE.ON)
    middle_rect.set_style_clip_corner(True, 0)  # Clip content to rounded corners
    # For older LVGL versions, just enabling scrollbar mode is sufficient for scrolling

    # Note: Scrollbar styling methods are removed for older LVGL version compatibility

    # Add text label inside input box to display input content
    input_text = lv.label(middle_rect)
    input_text.set_style_text_color(lv.color_hex(0xffffff), 0)
    input_text.set_style_text_font(lv.font_montserrat_24, 0)
    input_text.set_style_text_align(lv.TEXT_ALIGN.LEFT, 0)
    input_text.set_style_text_line_space(0, 0)  # Set smaller line spacing
    input_text.set_width(410)
    input_text.set_pos(0, -10)  # Position at top-left corner with 10px padding
    input_text.set_text("")

    # Add input box to selection items
    selection_items.append(middle_rect)
    item_positions.append((20, 85))  # Adjusted position to frame the input box
    item_sizes.append((440, 110))    # Adjusted size to frame the input box

    # Add bottom text instructions
    text1 = lv.label(scr)
    text1.set_text("<Middle orange button> + Key = Symbol Mode")
    text1.set_style_text_font(lv.font_montserrat_14, 0)
    text1.set_style_text_color(lv.color_hex(0xffffff), 0)
    text1.set_pos(70, 200)

    text2 = lv.label(scr)
    text2.set_text("CAP + Key = Capitalize")
    text2.set_style_text_font(lv.font_montserrat_14, 0)
    text2.set_style_text_color(lv.color_hex(0xffffff), 0)
    text2.set_pos(170, 220)


    # Position selection box over first item (back button) by default
    current_selection = 0
    x, y = item_positions[current_selection]
    width, height = item_sizes[current_selection]
    selection_box.set_size(width, height)
    selection_box.set_pos(x, y)

    
    
    while True:
        key = encoder.update()
        
        if key == "down": 
            # Move selection down
            current_selection = (current_selection + 1) % len(selection_items)  # Use actual number of items
            # Move and resize selection box to new position
            x, y = item_positions[current_selection]
            width, height = item_sizes[current_selection]
            selection_box.set_size(width, height)
            selection_box.set_pos(x, y)
            
            
        elif key == "up":
            # Move selection up
            current_selection = (current_selection - 1) % len(selection_items)  # Use actual number of items
            # Move and resize selection box to new position
            x, y = item_positions[current_selection]
            width, height = item_sizes[current_selection]
            selection_box.set_size(width, height)
            selection_box.set_pos(x, y)
            
            
        elif key == "enter":
            # Check if back button is selected
            if current_selection == 0:
                break  # Exit the loop to return to main page
            # Handle input box selection
            elif current_selection == 1:
                # Enter input mode with blinking cursor
                input_mode = True
                
                try:
                    # Input mode loop
                    while input_mode:
                        key = encoder.update()
                        # Check for exit input mode
                        if key == "enter":
                            input_mode = False
                        # Handle up/down keys for scrolling
                        elif key == "up":
                            middle_rect.scroll_by(0, 50, True)  # Scroll up
                        elif key == "down":
                            middle_rect.scroll_by(0, -50, True)  # Scroll down
                        boardKey = kb.get_key()
                        if boardKey is not None:
                            # Get current text
                            current_text = input_text.get_text()
                            # Add new character to text
                            new_text = current_text + str(boardKey)
                            # Update display
                            input_text.set_text(new_text)
                            # Ensure the last line is visible (scroll to bottom)
                            middle_rect.scroll_to_y(input_text.get_height() - middle_rect.get_height(), True)
                            # Move cursor after the new character
                            time.sleep(0.11)
                finally:
                    pass
    
    # Clear the screen again to prepare for returning to original page
    scr = lv.screen_active()
    while True:
        child = scr.get_child(0)
        if child is None:
            break
        child.delete()
    
    # Return to original page by recreating all elements
    recreate_main_page()


