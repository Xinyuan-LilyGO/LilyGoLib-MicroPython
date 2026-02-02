import lvgl as lv

recreate_main_page = None
encoder = None
_display_backlight = None
_system_info = None
_charger = None
_devices_status = None

def set_references(recreate_func, encoder_obj, display_backlight_func, system_info_func, devices_status_func, charger_func):
    global recreate_main_page, encoder, _display_backlight, _system_info, _devices_status, _charger
    recreate_main_page = recreate_func
    encoder = encoder_obj
    _display_backlight = display_backlight_func
    _system_info = system_info_func
    _devices_status = devices_status_func
    _charger = charger_func
    
def setting():
    # Clear all current screen elements
    scr = lv.screen_active()
    # Remove all children from the screen
    while True:
        child = scr.get_child(0)
        if child is None:
            break
        child.delete()
    
    # Set background to black
    scr.set_style_bg_color(lv.color_hex(0x000000), 0)
    
    # Create a separate selection box object that will overlay on top of items
    selection_box = lv.obj(scr)
    selection_box.set_style_border_width(4, 0)  # Thick white border
    selection_box.set_style_border_color(lv.color_hex(0xffffff), 0)
    selection_box.set_style_border_opa(lv.OPA.COVER, 0)
    selection_box.set_style_bg_opa(lv.OPA.TRANSP, 0)  # Transparent background
    selection_box.set_style_radius(3, 0)  # Slightly rounded corners
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
    
    # Item 1: Display & Backlight
    symbol_set_label1 = lv.label(scr)
    symbol_set_label1.set_text(lv.SYMBOL.SETTINGS)
    symbol_set_label1.set_style_text_font(lv.font_montserrat_20, 0)
    symbol_set_label1.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    symbol_set_label1.set_pos(20, 95)
    
    text_set_label1 = lv.label(scr)
    text_set_label1.set_text("Display & Backlight")
    text_set_label1.set_style_text_font(lv.font_montserrat_20, 0)
    text_set_label1.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    text_set_label1.set_pos(60, 95)  # Position next to symbol
    
    selection_items.append(symbol_set_label1)  # Use symbol as reference for selection
    item_positions.append((15, 90))  # Adjusted position: left 3px total, up 4px total
    item_sizes.append((440, 30))  # Long size for other items
    
    # Item 2: System Info
    symbol_set_label2 = lv.label(scr)
    symbol_set_label2.set_text(lv.SYMBOL.SETTINGS)
    symbol_set_label2.set_style_text_font(lv.font_montserrat_20, 0)
    symbol_set_label2.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    symbol_set_label2.set_pos(20, 135)
    
    text_set_label2 = lv.label(scr)
    text_set_label2.set_text("System Info")
    text_set_label2.set_style_text_font(lv.font_montserrat_20, 0)
    text_set_label2.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    text_set_label2.set_pos(60, 135)
    
    selection_items.append(symbol_set_label2)
    item_positions.append((15, 130))  # Adjusted position: left 3px total, up 4px total
    item_sizes.append((440, 30))  # Long size
    
    # Item 3: Devices status
    symbol_set_label3 = lv.label(scr)
    symbol_set_label3.set_text(lv.SYMBOL.SETTINGS)
    symbol_set_label3.set_style_text_font(lv.font_montserrat_20, 0)
    symbol_set_label3.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    symbol_set_label3.set_pos(20, 175)
    
    text_set_label3 = lv.label(scr)
    text_set_label3.set_text("Devices status")
    text_set_label3.set_style_text_font(lv.font_montserrat_20, 0)
    text_set_label3.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    text_set_label3.set_pos(60, 175)
    
    selection_items.append(symbol_set_label3)
    item_positions.append((15, 170))  # Adjusted position: left 3px total, up 4px total
    item_sizes.append((440, 30))  # Long size
    
    # Item 4: Charger
    symbol_set_label4 = lv.label(scr)
    symbol_set_label4.set_text(lv.SYMBOL.SETTINGS)
    symbol_set_label4.set_style_text_font(lv.font_montserrat_20, 0)
    symbol_set_label4.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    symbol_set_label4.set_pos(20, 215)
    
    text_set_label4 = lv.label(scr)
    text_set_label4.set_text("Charger")
    text_set_label4.set_style_text_font(lv.font_montserrat_20, 0)
    text_set_label4.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    text_set_label4.set_pos(60, 215)
    
    selection_items.append(symbol_set_label4)
    item_positions.append((15, 215 - 4))  # Adjusted position: left 3px total, up 4px total
    item_sizes.append((440, 30))  # Long size
    
    # Position selection box over first item (back button) by default
    current_selection = 0
    x, y = item_positions[current_selection]
    width, height = item_sizes[current_selection]
    selection_box.set_size(width, height)
    selection_box.set_pos(x, y)
    
    # Handle encoder input in setting page
    while True:
        key = encoder.update()
        
        if key == "down":
            # Move selection down
            current_selection = (current_selection + 1) % 5
            # Move and resize selection box to new position
            x, y = item_positions[current_selection]
            width, height = item_sizes[current_selection]
            selection_box.set_size(width, height)
            selection_box.set_pos(x, y)
            
        elif key == "up":
            # Move selection up
            current_selection = (current_selection - 1) % 5
            # Move and resize selection box to new position
            x, y = item_positions[current_selection]
            width, height = item_sizes[current_selection]
            selection_box.set_size(width, height)
            selection_box.set_pos(x, y)
            
        elif key == "enter":
            # Check if back button is selected
            if current_selection == 0:
                break  # Exit the loop to return to main page
            # For other selections, you can add specific handling here
            if current_selection == 1:
                _display_backlight()
                # Clear all current screen elements
                scr = lv.screen_active()
                while True:
                    child = scr.get_child(0)
                    if child is None:
                        break
                    child.delete()
                
                # Recreate setting page elements
                scr.set_style_bg_color(lv.color_hex(0x000000), 0)
                # Recreate selection box
                selection_box = lv.obj(scr)
                selection_box.set_style_border_width(4, 0)
                selection_box.set_style_border_color(lv.color_hex(0xffffff), 0)
                selection_box.set_style_border_opa(lv.OPA.COVER, 0)
                selection_box.set_style_bg_opa(lv.OPA.TRANSP, 0)
                selection_box.set_style_radius(3, 0)
                selection_box.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
                
                # Recreate selection items
                selection_items = []
                item_positions = []
                item_sizes = []
                
                # Item 0: Back button
                symbol_left_label = lv.label(scr)
                symbol_left_label.set_text(lv.SYMBOL.LEFT)
                symbol_left_label.set_style_text_font(lv.font_montserrat_20, 0)
                symbol_left_label.set_style_text_color(lv.color_hex(0xffffff), 0)
                symbol_left_label.set_pos(20, 55)
                selection_items.append(symbol_left_label)
                item_positions.append((12, 50))
                item_sizes.append((30, 30))
                
                # Item 1: Display & Backlight
                symbol_set_label1 = lv.label(scr)
                symbol_set_label1.set_text(lv.SYMBOL.SETTINGS)
                symbol_set_label1.set_style_text_font(lv.font_montserrat_20, 0)
                symbol_set_label1.set_style_text_color(lv.color_hex(0xffffff), 0)
                symbol_set_label1.set_pos(20, 95)
                
                text_set_label1 = lv.label(scr)
                text_set_label1.set_text("Display & Backlight")
                text_set_label1.set_style_text_font(lv.font_montserrat_20, 0)
                text_set_label1.set_style_text_color(lv.color_hex(0xffffff), 0)
                text_set_label1.set_pos(60, 95)
                
                selection_items.append(symbol_set_label1)
                item_positions.append((15, 90))
                item_sizes.append((440, 30))
                
                # Item 2: System Info
                symbol_set_label2 = lv.label(scr)
                symbol_set_label2.set_text(lv.SYMBOL.SETTINGS)
                symbol_set_label2.set_style_text_font(lv.font_montserrat_20, 0)
                symbol_set_label2.set_style_text_color(lv.color_hex(0xffffff), 0)
                symbol_set_label2.set_pos(20, 135)
                
                text_set_label2 = lv.label(scr)
                text_set_label2.set_text("System Info")
                text_set_label2.set_style_text_font(lv.font_montserrat_20, 0)
                text_set_label2.set_style_text_color(lv.color_hex(0xffffff), 0)
                text_set_label2.set_pos(60, 135)
                
                selection_items.append(symbol_set_label2)
                item_positions.append((15, 130))
                item_sizes.append((440, 30))
                
                # Item 3: Devices status
                symbol_set_label3 = lv.label(scr)
                symbol_set_label3.set_text(lv.SYMBOL.SETTINGS)
                symbol_set_label3.set_style_text_font(lv.font_montserrat_20, 0)
                symbol_set_label3.set_style_text_color(lv.color_hex(0xffffff), 0)
                symbol_set_label3.set_pos(20, 175)
                
                text_set_label3 = lv.label(scr)
                text_set_label3.set_text("Devices status")
                text_set_label3.set_style_text_font(lv.font_montserrat_20, 0)
                text_set_label3.set_style_text_color(lv.color_hex(0xffffff), 0)
                text_set_label3.set_pos(60, 175)
                
                selection_items.append(symbol_set_label3)
                item_positions.append((15, 170))
                item_sizes.append((440, 30))
                
                # Item 4: Charger
                symbol_set_label4 = lv.label(scr)
                symbol_set_label4.set_text(lv.SYMBOL.SETTINGS)
                symbol_set_label4.set_style_text_font(lv.font_montserrat_20, 0)
                symbol_set_label4.set_style_text_color(lv.color_hex(0xffffff), 0)
                symbol_set_label4.set_pos(20, 215)
                
                text_set_label4 = lv.label(scr)
                text_set_label4.set_text("Charger")
                text_set_label4.set_style_text_font(lv.font_montserrat_20, 0)
                text_set_label4.set_style_text_color(lv.color_hex(0xffffff), 0)
                text_set_label4.set_pos(60, 215)
                
                selection_items.append(symbol_set_label4)
                item_positions.append((15, 211))
                item_sizes.append((440, 30))
                
                # Reset selection box position
                x, y = item_positions[current_selection]
                width, height = item_sizes[current_selection]
                selection_box.set_size(width, height)
                selection_box.set_pos(x, y)
            
            elif current_selection == 2:
                _system_info()
                # Clear all current screen elements
                scr = lv.screen_active()
                while True:
                    child = scr.get_child(0)
                    if child is None:
                        break
                    child.delete()
                
                # Recreate setting page elements
                scr.set_style_bg_color(lv.color_hex(0x000000), 0)
                # Recreate selection box
                selection_box = lv.obj(scr)
                selection_box.set_style_border_width(4, 0)
                selection_box.set_style_border_color(lv.color_hex(0xffffff), 0)
                selection_box.set_style_border_opa(lv.OPA.COVER, 0)
                selection_box.set_style_bg_opa(lv.OPA.TRANSP, 0)
                selection_box.set_style_radius(3, 0)
                selection_box.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
                
                # Recreate selection items
                selection_items = []
                item_positions = []
                item_sizes = []
                
                # Item 0: Back button
                symbol_left_label = lv.label(scr)
                symbol_left_label.set_text(lv.SYMBOL.LEFT)
                symbol_left_label.set_style_text_font(lv.font_montserrat_20, 0)
                symbol_left_label.set_style_text_color(lv.color_hex(0xffffff), 0)
                symbol_left_label.set_pos(20, 55)
                selection_items.append(symbol_left_label)
                item_positions.append((12, 50))
                item_sizes.append((30, 30))
                
                # Item 1: Display & Backlight
                symbol_set_label1 = lv.label(scr)
                symbol_set_label1.set_text(lv.SYMBOL.SETTINGS)
                symbol_set_label1.set_style_text_font(lv.font_montserrat_20, 0)
                symbol_set_label1.set_style_text_color(lv.color_hex(0xffffff), 0)
                symbol_set_label1.set_pos(20, 95)
                
                text_set_label1 = lv.label(scr)
                text_set_label1.set_text("Display & Backlight")
                text_set_label1.set_style_text_font(lv.font_montserrat_20, 0)
                text_set_label1.set_style_text_color(lv.color_hex(0xffffff), 0)
                text_set_label1.set_pos(60, 95)
                
                selection_items.append(symbol_set_label1)
                item_positions.append((15, 90))
                item_sizes.append((440, 30))
                
                # Item 2: System Info
                symbol_set_label2 = lv.label(scr)
                symbol_set_label2.set_text(lv.SYMBOL.SETTINGS)
                symbol_set_label2.set_style_text_font(lv.font_montserrat_20, 0)
                symbol_set_label2.set_style_text_color(lv.color_hex(0xffffff), 0)
                symbol_set_label2.set_pos(20, 135)
                
                text_set_label2 = lv.label(scr)
                text_set_label2.set_text("System Info")
                text_set_label2.set_style_text_font(lv.font_montserrat_20, 0)
                text_set_label2.set_style_text_color(lv.color_hex(0xffffff), 0)
                text_set_label2.set_pos(60, 135)
                
                selection_items.append(symbol_set_label2)
                item_positions.append((15, 130))
                item_sizes.append((440, 30))
                
                # Item 3: Devices status
                symbol_set_label3 = lv.label(scr)
                symbol_set_label3.set_text(lv.SYMBOL.SETTINGS)
                symbol_set_label3.set_style_text_font(lv.font_montserrat_20, 0)
                symbol_set_label3.set_style_text_color(lv.color_hex(0xffffff), 0)
                symbol_set_label3.set_pos(20, 175)
                
                text_set_label3 = lv.label(scr)
                text_set_label3.set_text("Devices status")
                text_set_label3.set_style_text_font(lv.font_montserrat_20, 0)
                text_set_label3.set_style_text_color(lv.color_hex(0xffffff), 0)
                text_set_label3.set_pos(60, 175)
                
                selection_items.append(symbol_set_label3)
                item_positions.append((15, 170))
                item_sizes.append((440, 30))
                
                # Item 4: Charger
                symbol_set_label4 = lv.label(scr)
                symbol_set_label4.set_text(lv.SYMBOL.SETTINGS)
                symbol_set_label4.set_style_text_font(lv.font_montserrat_20, 0)
                symbol_set_label4.set_style_text_color(lv.color_hex(0xffffff), 0)
                symbol_set_label4.set_pos(20, 215)
                
                text_set_label4 = lv.label(scr)
                text_set_label4.set_text("Charger")
                text_set_label4.set_style_text_font(lv.font_montserrat_20, 0)
                text_set_label4.set_style_text_color(lv.color_hex(0xffffff), 0)
                text_set_label4.set_pos(60, 215)
                
                selection_items.append(symbol_set_label4)
                item_positions.append((15, 211))
                item_sizes.append((440, 30))
                
                # Reset selection box position
                x, y = item_positions[current_selection]
                width, height = item_sizes[current_selection]
                selection_box.set_size(width, height)
                selection_box.set_pos(x, y)
                
            elif current_selection == 3:
                _devices_status()
                # Clear all current screen elements
                scr = lv.screen_active()
                while True:
                    child = scr.get_child(0)
                    if child is None:
                        break
                    child.delete()
                
                # Recreate setting page elements
                scr.set_style_bg_color(lv.color_hex(0x000000), 0)
                # Recreate selection box
                selection_box = lv.obj(scr)
                selection_box.set_style_border_width(4, 0)
                selection_box.set_style_border_color(lv.color_hex(0xffffff), 0)
                selection_box.set_style_border_opa(lv.OPA.COVER, 0)
                selection_box.set_style_bg_opa(lv.OPA.TRANSP, 0)
                selection_box.set_style_radius(3, 0)
                selection_box.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
                
                # Recreate selection items
                selection_items = []
                item_positions = []
                item_sizes = []
                
                # Item 0: Back button
                symbol_left_label = lv.label(scr)
                symbol_left_label.set_text(lv.SYMBOL.LEFT)
                symbol_left_label.set_style_text_font(lv.font_montserrat_20, 0)
                symbol_left_label.set_style_text_color(lv.color_hex(0xffffff), 0)
                symbol_left_label.set_pos(20, 55)
                selection_items.append(symbol_left_label)
                item_positions.append((12, 50))
                item_sizes.append((30, 30))
                
                # Item 1: Display & Backlight
                symbol_set_label1 = lv.label(scr)
                symbol_set_label1.set_text(lv.SYMBOL.SETTINGS)
                symbol_set_label1.set_style_text_font(lv.font_montserrat_20, 0)
                symbol_set_label1.set_style_text_color(lv.color_hex(0xffffff), 0)
                symbol_set_label1.set_pos(20, 95)
                
                text_set_label1 = lv.label(scr)
                text_set_label1.set_text("Display & Backlight")
                text_set_label1.set_style_text_font(lv.font_montserrat_20, 0)
                text_set_label1.set_style_text_color(lv.color_hex(0xffffff), 0)
                text_set_label1.set_pos(60, 95)
                
                selection_items.append(symbol_set_label1)
                item_positions.append((15, 90))
                item_sizes.append((440, 30))
                
                # Item 2: System Info
                symbol_set_label2 = lv.label(scr)
                symbol_set_label2.set_text(lv.SYMBOL.SETTINGS)
                symbol_set_label2.set_style_text_font(lv.font_montserrat_20, 0)
                symbol_set_label2.set_style_text_color(lv.color_hex(0xffffff), 0)
                symbol_set_label2.set_pos(20, 135)
                
                text_set_label2 = lv.label(scr)
                text_set_label2.set_text("System Info")
                text_set_label2.set_style_text_font(lv.font_montserrat_20, 0)
                text_set_label2.set_style_text_color(lv.color_hex(0xffffff), 0)
                text_set_label2.set_pos(60, 135)
                
                selection_items.append(symbol_set_label2)
                item_positions.append((15, 130))
                item_sizes.append((440, 30))
                
                # Item 3: Devices status
                symbol_set_label3 = lv.label(scr)
                symbol_set_label3.set_text(lv.SYMBOL.SETTINGS)
                symbol_set_label3.set_style_text_font(lv.font_montserrat_20, 0)
                symbol_set_label3.set_style_text_color(lv.color_hex(0xffffff), 0)
                symbol_set_label3.set_pos(20, 175)
                
                text_set_label3 = lv.label(scr)
                text_set_label3.set_text("Devices status")
                text_set_label3.set_style_text_font(lv.font_montserrat_20, 0)
                text_set_label3.set_style_text_color(lv.color_hex(0xffffff), 0)
                text_set_label3.set_pos(60, 175)
                
                selection_items.append(symbol_set_label3)
                item_positions.append((15, 170))
                item_sizes.append((440, 30))
                
                # Item 4: Charger
                symbol_set_label4 = lv.label(scr)
                symbol_set_label4.set_text(lv.SYMBOL.SETTINGS)
                symbol_set_label4.set_style_text_font(lv.font_montserrat_20, 0)
                symbol_set_label4.set_style_text_color(lv.color_hex(0xffffff), 0)
                symbol_set_label4.set_pos(20, 215)
                
                text_set_label4 = lv.label(scr)
                text_set_label4.set_text("Charger")
                text_set_label4.set_style_text_font(lv.font_montserrat_20, 0)
                text_set_label4.set_style_text_color(lv.color_hex(0xffffff), 0)
                text_set_label4.set_pos(60, 215)
                
                selection_items.append(symbol_set_label4)
                item_positions.append((15, 211))
                item_sizes.append((440, 30))
                
                # Reset selection box position
                x, y = item_positions[current_selection]
                width, height = item_sizes[current_selection]
                selection_box.set_size(width, height)
                selection_box.set_pos(x, y)
                
            elif current_selection == 4:
                _charger()
                # Clear all current screen elements
                scr = lv.screen_active()
                while True:
                    child = scr.get_child(0)
                    if child is None:
                        break
                    child.delete()
                
                # Recreate setting page elements
                scr.set_style_bg_color(lv.color_hex(0x000000), 0)
                # Recreate selection box
                selection_box = lv.obj(scr)
                selection_box.set_style_border_width(4, 0)
                selection_box.set_style_border_color(lv.color_hex(0xffffff), 0)
                selection_box.set_style_border_opa(lv.OPA.COVER, 0)
                selection_box.set_style_bg_opa(lv.OPA.TRANSP, 0)
                selection_box.set_style_radius(3, 0)
                selection_box.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
                
                # Recreate selection items
                selection_items = []
                item_positions = []
                item_sizes = []
                
                # Item 0: Back button
                symbol_left_label = lv.label(scr)
                symbol_left_label.set_text(lv.SYMBOL.LEFT)
                symbol_left_label.set_style_text_font(lv.font_montserrat_20, 0)
                symbol_left_label.set_style_text_color(lv.color_hex(0xffffff), 0)
                symbol_left_label.set_pos(20, 55)
                selection_items.append(symbol_left_label)
                item_positions.append((12, 50))
                item_sizes.append((30, 30))
                
                # Item 1: Display & Backlight
                symbol_set_label1 = lv.label(scr)
                symbol_set_label1.set_text(lv.SYMBOL.SETTINGS)
                symbol_set_label1.set_style_text_font(lv.font_montserrat_20, 0)
                symbol_set_label1.set_style_text_color(lv.color_hex(0xffffff), 0)
                symbol_set_label1.set_pos(20, 95)
                
                text_set_label1 = lv.label(scr)
                text_set_label1.set_text("Display & Backlight")
                text_set_label1.set_style_text_font(lv.font_montserrat_20, 0)
                text_set_label1.set_style_text_color(lv.color_hex(0xffffff), 0)
                text_set_label1.set_pos(60, 95)
                
                selection_items.append(symbol_set_label1)
                item_positions.append((15, 90))
                item_sizes.append((440, 30))
                
                # Item 2: System Info
                symbol_set_label2 = lv.label(scr)
                symbol_set_label2.set_text(lv.SYMBOL.SETTINGS)
                symbol_set_label2.set_style_text_font(lv.font_montserrat_20, 0)
                symbol_set_label2.set_style_text_color(lv.color_hex(0xffffff), 0)
                symbol_set_label2.set_pos(20, 135)
                
                text_set_label2 = lv.label(scr)
                text_set_label2.set_text("System Info")
                text_set_label2.set_style_text_font(lv.font_montserrat_20, 0)
                text_set_label2.set_style_text_color(lv.color_hex(0xffffff), 0)
                text_set_label2.set_pos(60, 135)
                
                selection_items.append(symbol_set_label2)
                item_positions.append((15, 130))
                item_sizes.append((440, 30))
                
                # Item 3: Devices status
                symbol_set_label3 = lv.label(scr)
                symbol_set_label3.set_text(lv.SYMBOL.SETTINGS)
                symbol_set_label3.set_style_text_font(lv.font_montserrat_20, 0)
                symbol_set_label3.set_style_text_color(lv.color_hex(0xffffff), 0)
                symbol_set_label3.set_pos(20, 175)
                
                text_set_label3 = lv.label(scr)
                text_set_label3.set_text("Devices status")
                text_set_label3.set_style_text_font(lv.font_montserrat_20, 0)
                text_set_label3.set_style_text_color(lv.color_hex(0xffffff), 0)
                text_set_label3.set_pos(60, 175)
                
                selection_items.append(symbol_set_label3)
                item_positions.append((15, 170))
                item_sizes.append((440, 30))
                
                # Item 4: Charger
                symbol_set_label4 = lv.label(scr)
                symbol_set_label4.set_text(lv.SYMBOL.SETTINGS)
                symbol_set_label4.set_style_text_font(lv.font_montserrat_20, 0)
                symbol_set_label4.set_style_text_color(lv.color_hex(0xffffff), 0)
                symbol_set_label4.set_pos(20, 215)
                
                text_set_label4 = lv.label(scr)
                text_set_label4.set_text("Charger")
                text_set_label4.set_style_text_font(lv.font_montserrat_20, 0)
                text_set_label4.set_style_text_color(lv.color_hex(0xffffff), 0)
                text_set_label4.set_pos(60, 215)
                
                selection_items.append(symbol_set_label4)
                item_positions.append((15, 211))
                item_sizes.append((440, 30))
                
                # Reset selection box position
                x, y = item_positions[current_selection]
                width, height = item_sizes[current_selection]
                selection_box.set_size(width, height)
                selection_box.set_pos(x, y)
                
    # Return to original page by recreating all elements
    recreate_main_page()

