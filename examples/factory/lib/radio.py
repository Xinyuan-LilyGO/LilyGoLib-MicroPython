import lvgl as lv
import time

recreate_main_page = None
encoder = None
dropdown_selections = [0] * 9  # 保存每个下拉框的选择索引

dropdown_options_list = [
    ["DISABLE", "ENABLE"],
    ["Disable", "TX Mode", "RX Mode", "TxContinuousWave"],
    ["433MHZ", "470MHZ", "842MHZ", "850MHZ", "868MHZ", "915MHZ", "923MHZ", "945MHZ"],
    ["41.7KHz", "62.5KHz", "125KHz", "250KHz", "500KHz", "KHz"],
    ["2dBm", "5dBm", "10dBm", "12dBm", "17dBm", "20dBm", "22dBm"],
    ["100ms", "200ms", "500ms", "1000ms", "2000ms", "3000ms"],
    ["5", "6", "7", "8"],
    ["5", "6", "7", "8","9", "10", "11", "12"],
    ["100", "200", "300", "400"]
]
dropdown_item_height = 25
dropdown_max_visible = 3

def set_references(recreate_func, encoder_obj=None):
    global recreate_main_page, encoder
    recreate_main_page = recreate_func
    if encoder_obj is not None:
        encoder = encoder_obj

def update_item_positions(selection_items, scroll_offset, dropdown_displays=None, dropdown_lists=None, dropdown_arrows=None, dropdown_x_positions=None, dropdown_widths=None):
    """Update the visual position of all items based on scroll offset"""
    base_y_start = 55
    item_spacing = 40
    
    for i, item in enumerate(selection_items):
        if i == 0:
            x, y = 20, base_y_start
        else:
            monitor_index = i - 1
            x = 20
            y = 95 + (monitor_index * item_spacing)
        item.set_pos(x, y - scroll_offset)

    if dropdown_displays:
        for i, dropdown_display in enumerate(dropdown_displays):
            monitor_index = i
            x = dropdown_x_positions[i] if dropdown_x_positions else 270
            y = 95 + (monitor_index * item_spacing)
            dropdown_display.set_pos(x, y - scroll_offset)
    
    if dropdown_arrows:
        for i, arrow in enumerate(dropdown_arrows):
            monitor_index = i
            x = dropdown_x_positions[i] if dropdown_x_positions else 270
            width = dropdown_widths[i] if dropdown_widths else 80
            y = 95 + (monitor_index * item_spacing)
            arrow.set_pos(x + width - 20, y + 5 - scroll_offset)
    
    if dropdown_lists:
        for i, dropdown_list in enumerate(dropdown_lists):
            if dropdown_list:
                monitor_index = i
                x = dropdown_x_positions[i] if dropdown_x_positions else 270
                y = 95 + (monitor_index * item_spacing)
                base_y = y + 35
                dropdown_list.set_pos(x, base_y - scroll_offset)

def create_dropdown_component(scr, options, initial_value, x, y, width=80, height=30):
    dropdown_display = lv.textarea(scr)
    dropdown_display.set_size(width, height)
    dropdown_display.set_pos(x, y)
    dropdown_display.set_text(initial_value)
    dropdown_display.set_one_line(True)
    dropdown_display.set_style_text_color(lv.color_hex(0xffffff), 0)
    dropdown_display.set_style_border_color(lv.color_hex(0xffffff), 0)
    dropdown_display.set_style_border_width(1, 0)
    dropdown_display.set_style_border_opa(lv.OPA.COVER, 0)
    dropdown_display.set_style_radius(3, 0)
    dropdown_display.set_style_bg_opa(lv.OPA.TRANSP, 0)
    dropdown_display.set_placeholder_text("")
    
    arrow_symbol = lv.label(scr)
    arrow_symbol.set_text(lv.SYMBOL.DOWN)
    arrow_symbol.set_style_text_font(lv.font_montserrat_16, 0)
    arrow_symbol.set_style_text_color(lv.color_hex(0xffffff), 0)
    arrow_symbol.set_pos(x + width - 20, y + 5)
    
    dropdown_list = lv.obj(lv.layer_top())
    item_height = dropdown_item_height
    total_height = dropdown_max_visible * item_height
    dropdown_list.set_size(width, total_height)
    dropdown_list.set_pos(x, y + height + 2)
    dropdown_list.set_style_border_width(1, 0)
    dropdown_list.set_style_border_color(lv.color_hex(0xffffff), 0)
    dropdown_list.set_style_bg_color(lv.color_hex(0x000000), 0)
    dropdown_list.set_style_radius(3, 0)
    dropdown_list.set_style_clip_corner(True, 0)
    dropdown_list.set_style_bg_opa(lv.OPA.COVER, 0)
    dropdown_list.set_style_opa(lv.OPA.COVER, 0)
    dropdown_list.set_height(0)
    
    dropdown_base_y = y
    return dropdown_display, arrow_symbol, dropdown_list, options, initial_value, dropdown_base_y

def radio(should_recreate=True):
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
    
    # Dropdown components arrays
    dropdown_displays = []
    dropdown_arrows = []
    dropdown_lists = []
    dropdown_items_arrays = []
    dropdown_base_y_list = []
    
    # Item 0: Back button (lv.SYMBOL.LEFT)
    symbol_left_label = lv.label(scr)
    symbol_left_label.set_text(lv.SYMBOL.LEFT)
    symbol_left_label.set_style_text_font(lv.font_montserrat_20, 0)
    symbol_left_label.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    symbol_left_label.set_pos(20, 55)
    selection_items.append(symbol_left_label)
    item_positions.append((12, 50))  # Adjusted position: left 3px total, up 4px total
    item_sizes.append((30, 30))  # Smaller size for back button
    
    # Item 1: 
    text_set_label1 = lv.label(scr)
    text_set_label1.set_text("State:")
    text_set_label1.set_style_text_font(lv.font_montserrat_20, 0)
    text_set_label1.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    text_set_label1.set_pos(50, 95)  # Position next to symbol
    
    dropdown1 = create_dropdown_component(scr, dropdown_options_list[0], dropdown_options_list[0][dropdown_selections[0]], 235, 95, 200, 30)
    dropdown_displays.append(dropdown1[0])
    dropdown_arrows.append(dropdown1[1])
    dropdown_lists.append(dropdown1[2])
    dropdown_items_arrays.append(dropdown1[3])
    dropdown_base_y_list.append(dropdown1[5])
    
    selection_items.append(text_set_label1)  # Use symbol as reference for selection
    item_positions.append((15, 90))  # Adjusted position: left 3px total, up 4px total
    item_sizes.append((440, 30))  # Long size for other items
    
    # Item 2: 
    text_set_label2 = lv.label(scr)
    text_set_label2.set_text("Mode:")
    text_set_label2.set_style_text_font(lv.font_montserrat_20, 0)
    text_set_label2.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    text_set_label2.set_pos(50, 135)
    
    dropdown2 = create_dropdown_component(scr, dropdown_options_list[1], dropdown_options_list[1][dropdown_selections[1]], 235, 135, 200, 30)
    dropdown_displays.append(dropdown2[0])
    dropdown_arrows.append(dropdown2[1])
    dropdown_lists.append(dropdown2[2])
    dropdown_items_arrays.append(dropdown2[3])
    dropdown_base_y_list.append(dropdown2[5])
    
    selection_items.append(text_set_label2)
    item_positions.append((15, 130))  # Adjusted position: left 3px total, up 4px total
    item_sizes.append((440, 30))  # Long size
    
    # Item 3: 
    text_set_label3 = lv.label(scr)
    text_set_label3.set_text("Frequency:")
    text_set_label3.set_style_text_font(lv.font_montserrat_20, 0)
    text_set_label3.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    text_set_label3.set_pos(50, 175)
    
    dropdown3 = create_dropdown_component(scr, dropdown_options_list[2], dropdown_options_list[2][0], 235, 175, 200, 30)
    dropdown_displays.append(dropdown3[0])
    dropdown_arrows.append(dropdown3[1])
    dropdown_lists.append(dropdown3[2])
    dropdown_items_arrays.append(dropdown3[3])
    dropdown_base_y_list.append(dropdown3[5])
    
    selection_items.append(text_set_label3)
    item_positions.append((15, 170))  # Adjusted position: left 3px total, up 4px total
    item_sizes.append((440, 30))  # Long size
    
    # Item 4: 
    text_set_label4 = lv.label(scr)
    text_set_label4.set_text("Bandwidth:")
    text_set_label4.set_style_text_font(lv.font_montserrat_20, 0)
    text_set_label4.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    text_set_label4.set_pos(50, 215)
    
    dropdown4 = create_dropdown_component(scr, dropdown_options_list[3], dropdown_options_list[3][dropdown_selections[3]], 235, 215, 200, 30)
    dropdown_displays.append(dropdown4[0])
    dropdown_arrows.append(dropdown4[1])
    dropdown_lists.append(dropdown4[2])
    dropdown_items_arrays.append(dropdown4[3])
    dropdown_base_y_list.append(dropdown4[5])
    
    selection_items.append(text_set_label4)
    item_positions.append((15, 215 - 4))  # Adjusted position: left 3px total, up 4px total
    item_sizes.append((440, 30))  # Long size
    
    # Item 5: System Voltage
    text_set_label5 = lv.label(scr)
    text_set_label5.set_text("Tx Power:")
    text_set_label5.set_style_text_font(lv.font_montserrat_20, 0)
    text_set_label5.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    text_set_label5.set_pos(50, 255)
    
    dropdown5 = create_dropdown_component(scr, dropdown_options_list[4], dropdown_options_list[4][0], 235, 255, 200, 30)
    dropdown_displays.append(dropdown5[0])
    dropdown_arrows.append(dropdown5[1])
    dropdown_lists.append(dropdown5[2])
    dropdown_items_arrays.append(dropdown5[3])
    dropdown_base_y_list.append(dropdown5[5])
    
    selection_items.append(text_set_label5)
    item_positions.append((15, 250))  # Adjusted position: left 3px total, up 4px total
    item_sizes.append((440, 30))  # Long size
    
    # Item 6: Battery Percent
    text_set_label6 = lv.label(scr)
    text_set_label6.set_text("Tx Interval:")
    text_set_label6.set_style_text_font(lv.font_montserrat_20, 0)
    text_set_label6.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    text_set_label6.set_pos(50, 295)
    
    dropdown6 = create_dropdown_component(scr, dropdown_options_list[5], dropdown_options_list[5][0], 235, 295, 200, 30)
    dropdown_displays.append(dropdown6[0])
    dropdown_arrows.append(dropdown6[1])
    dropdown_lists.append(dropdown6[2])
    dropdown_items_arrays.append(dropdown6[3])
    dropdown_base_y_list.append(dropdown6[5])
    
    selection_items.append(text_set_label6)
    item_positions.append((15, 290))  # Adjusted position: left 3px total, up 4px total
    item_sizes.append((440, 30))  # Long size
    
    # Item 7: Temperature
    text_set_label7 = lv.label(scr)
    text_set_label7.set_text("Coding rate:")
    text_set_label7.set_style_text_font(lv.font_montserrat_20, 0)
    text_set_label7.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    text_set_label7.set_pos(50, 335)
    
    dropdown7 = create_dropdown_component(scr, dropdown_options_list[6], dropdown_options_list[6][dropdown_selections[6]], 235, 335, 200, 30)
    dropdown_displays.append(dropdown7[0])
    dropdown_arrows.append(dropdown7[1])
    dropdown_lists.append(dropdown7[2])
    dropdown_items_arrays.append(dropdown7[3])
    dropdown_base_y_list.append(dropdown7[5])
    
    selection_items.append(text_set_label7)
    item_positions.append((15, 330))  # Adjusted position: left 3px total, up 4px total
    item_sizes.append((440, 30))  # Long size
    
    # Item 8: Instantaneous Current
    text_set_label8 = lv.label(scr)
    text_set_label8.set_text("Spreading factor:")
    text_set_label8.set_style_text_font(lv.font_montserrat_20, 0)
    text_set_label8.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    text_set_label8.set_pos(50, 375)
    
    dropdown8 = create_dropdown_component(scr, dropdown_options_list[7], dropdown_options_list[7][dropdown_selections[7]], 235, 375, 200, 30)
    dropdown_displays.append(dropdown8[0])
    dropdown_arrows.append(dropdown8[1])
    dropdown_lists.append(dropdown8[2])
    dropdown_items_arrays.append(dropdown8[3])
    dropdown_base_y_list.append(dropdown8[5])
    
    
    selection_items.append(text_set_label8)
    item_positions.append((15, 370))  # Adjusted position: left 3px total, up 4px total
    item_sizes.append((440, 30))  # Long size
    
    # Item 9: Average Power
    text_set_label9 = lv.label(scr)
    text_set_label9.set_text("SyncWord:")
    text_set_label9.set_style_text_font(lv.font_montserrat_20, 0)
    text_set_label9.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    text_set_label9.set_pos(50, 415)
    
    dropdown9 = create_dropdown_component(scr, dropdown_options_list[8], dropdown_options_list[8][dropdown_selections[8]], 235, 415, 200, 30)
    dropdown_displays.append(dropdown9[0])
    dropdown_arrows.append(dropdown9[1])
    dropdown_lists.append(dropdown9[2])
    dropdown_items_arrays.append(dropdown9[3])
    dropdown_base_y_list.append(dropdown9[5])
    
    selection_items.append(text_set_label9)
    item_positions.append((15, 410))  # Adjusted position: left 3px total, up 4px total
    item_sizes.append((440, 30))  # Long size
    
    # Position selection box over first item (back button) by default
    current_selection = 0
    x, y = item_positions[current_selection]
    width, height = item_sizes[current_selection]
    selection_box.set_size(width, height)
    selection_box.set_pos(x, y)
    
    # Scroll offset to handle items that go beyond screen
    scroll_offset = 0
    max_visible_items = 5  # Number of items that can be fully visible (0-5)
    
    # Create a separate layer for dropdowns to ensure they appear on top
    dropdown_layer = lv.layer_top()
    
    # Dropdown state variables
    in_dropdown_selection = False
    current_dropdown_selection = 0
    current_dropdown_index = -1
    dropdown_item_labels = []
    dropdown_scroll_pos = 0  # Scroll position within dropdown list
    dropdown_open_upward = False  # Track if current dropdown opens upward
    
    # Dropdown item styles
    dropdown_item_style = lv.style_t()
    dropdown_item_style.init()
    dropdown_item_style.set_pad_ver(3)
    dropdown_item_style.set_pad_hor(10)
    dropdown_item_style.set_text_color(lv.color_hex(0xffffff))
    dropdown_item_style.set_bg_opa(lv.OPA.TRANSP)
    
    dropdown_selected_style = lv.style_t()
    dropdown_selected_style.init()
    dropdown_selected_style.set_pad_ver(3)
    dropdown_selected_style.set_pad_hor(10)
    dropdown_selected_style.set_text_color(lv.color_hex(0xffffff))
    dropdown_selected_style.set_bg_color(lv.color_hex(0x808080))
    dropdown_selected_style.set_bg_opa(lv.OPA.COVER)
    
    # Handle encoder input in setting page
    while True:
        key = encoder.update()
        
        if in_dropdown_selection:
            # Get current dropdown options
            options = dropdown_options_list[current_dropdown_index]
            
            # Handle selection within custom dropdown
            if key == "down":
                # Move selection down in dropdown
                old_selection = current_dropdown_selection
                current_dropdown_selection = (current_dropdown_selection + 1) % len(options)
                
                # Reset scroll when wrapping from last to first
                if old_selection == len(options) - 1 and current_dropdown_selection == 0:
                    dropdown_scroll_pos = 0
                # Auto-scroll: start scrolling when selection reaches 3rd item (index 2)
                elif current_dropdown_selection >= dropdown_max_visible - 1:
                    dropdown_scroll_pos = current_dropdown_selection - dropdown_max_visible + 2
                
                # Update styles for visible items
                for i, item_label in enumerate(dropdown_item_labels):
                    if i == current_dropdown_selection:
                        item_label.add_style(dropdown_selected_style, 0)
                    else:
                        item_label.remove_style(dropdown_selected_style, 0)
                
                # Update selection box position (relative to dropdown visible area)
                item_height = dropdown_item_height
                dropdown_y = dropdown_base_y_list[current_dropdown_index]
                adjusted_y = dropdown_y - scroll_offset
                visible_index = current_dropdown_selection - dropdown_scroll_pos
                
                if dropdown_open_upward:
                    dropdown_y = adjusted_y - dropdown_height + (visible_index * item_height)
                else:
                    dropdown_y = adjusted_y + 30 + (visible_index * item_height)
                
                dropdown_x = 275
                selection_box.set_pos(dropdown_x, dropdown_y)
                
                # Update dropdown item positions based on scroll
                for i, item_label in enumerate(dropdown_item_labels):
                    item_label.set_pos(5, i * item_height - (dropdown_scroll_pos * item_height))
                
                # Update display text
                dropdown_displays[current_dropdown_index].set_text(options[current_dropdown_selection])
                
            elif key == "up":
                # Move selection up in dropdown
                old_selection = current_dropdown_selection
                current_dropdown_selection = (current_dropdown_selection - 1) % len(options)
                
                # Auto-scroll: calculate new scroll position based on selection
                if current_dropdown_selection <= dropdown_max_visible - 2:
                    dropdown_scroll_pos = 0
                else:
                    dropdown_scroll_pos = current_dropdown_selection - dropdown_max_visible + 2
                
                # Update styles for visible items
                for i, item_label in enumerate(dropdown_item_labels):
                    if i == current_dropdown_selection:
                        item_label.add_style(dropdown_selected_style, 0)
                    else:
                        item_label.remove_style(dropdown_selected_style, 0)
                
                # Update selection box position (relative to dropdown visible area)
                item_height = dropdown_item_height
                dropdown_y = dropdown_base_y_list[current_dropdown_index]
                adjusted_y = dropdown_y - scroll_offset
                visible_index = current_dropdown_selection - dropdown_scroll_pos
                
                if dropdown_open_upward:
                    dropdown_y = adjusted_y - dropdown_height + (visible_index * item_height)
                else:
                    dropdown_y = adjusted_y + 30 + (visible_index * item_height)
                
                dropdown_x = 275
                selection_box.set_pos(dropdown_x, dropdown_y)
                
                # Update dropdown item positions based on scroll
                for i, item_label in enumerate(dropdown_item_labels):
                    item_label.set_pos(5, i * item_height - (dropdown_scroll_pos * item_height))
                
                # Update display text
                dropdown_displays[current_dropdown_index].set_text(options[current_dropdown_selection])
                
            elif key == "enter":
                # Confirm selection and exit dropdown mode
                selected_option = dropdown_options_list[current_dropdown_index][current_dropdown_selection]
                dropdown_displays[current_dropdown_index].set_text(selected_option)
                
                # Save selection state
                dropdown_selections[current_dropdown_index] = current_dropdown_selection
                
                # Hide dropdown list
                dropdown_lists[current_dropdown_index].set_height(0)
                dropdown_lists[current_dropdown_index].set_style_bg_opa(lv.OPA.TRANSP, 0)
                
                # Clear dropdown items
                for item_label in dropdown_item_labels:
                    item_label.delete()
                dropdown_item_labels = []
                
                # Exit dropdown selection mode
                in_dropdown_selection = False
                current_dropdown_index = -1
                
                # Restore selection box to item position
                x, y = item_positions[current_selection]
                width, height = item_sizes[current_selection]
                selection_box.set_size(width, height)
                selection_box.set_pos(x, y - scroll_offset)
        
        else:
            # Normal selection mode
            if key == "down":
                # Move selection down
                old_selection = current_selection
                current_selection = (current_selection + 1) % 10
                
                # Simple scroll logic: start scrolling when selection goes beyond visible items
                if current_selection >= max_visible_items:
                    scroll_offset = (current_selection - max_visible_items + 1) * 40
                elif old_selection > current_selection:  # Wrapped around to start
                    scroll_offset = 0  # Reset scroll when wrapping to beginning
                
                # Move and resize selection box to new position
                x, y = item_positions[current_selection]
                width, height = item_sizes[current_selection]
                selection_box.set_size(width, height)
                selection_box.set_pos(x, y - scroll_offset)
                
                # Update all item positions for scrolling
                update_item_positions(selection_items, scroll_offset, dropdown_displays=dropdown_displays, dropdown_lists=dropdown_lists, dropdown_arrows=dropdown_arrows, dropdown_x_positions=[235] * 9, dropdown_widths=[200] * 9)
                
            elif key == "up":
                # Move selection up
                old_selection = current_selection
                current_selection = (current_selection - 1) % 10
                
                # Simple scroll logic based on current selection
                if current_selection < max_visible_items:
                    scroll_offset = 0  # Top items are always visible
                else:
                    scroll_offset = (current_selection - max_visible_items + 1) * 40
                
                # Move and resize selection box to new position
                x, y = item_positions[current_selection]
                width, height = item_sizes[current_selection]
                selection_box.set_size(width, height)
                selection_box.set_pos(x, y - scroll_offset)
                
                # Update all item positions for scrolling
                update_item_positions(selection_items, scroll_offset, dropdown_displays=dropdown_displays, dropdown_lists=dropdown_lists, dropdown_arrows=dropdown_arrows, dropdown_x_positions=[235] * 9, dropdown_widths=[200] * 9)
                
            elif key == "enter":
                # Check if back button is selected
                if current_selection == 0:
                    break  # Exit the loop to return to main page
                
                # Check if a dropdown item is selected (items 1-16 have dropdowns)
                if current_selection >= 1 and current_selection <= 16:
                    # Open dropdown for current item
                    in_dropdown_selection = True
                    current_dropdown_index = current_selection - 1
                    current_dropdown_selection = 0  # Default to first option
                    dropdown_scroll_pos = 0  # Reset scroll position when opening dropdown
                    
                    # Get dropdown components
                    options = dropdown_options_list[current_dropdown_index]
                    dropdown_list = dropdown_lists[current_dropdown_index]
                    dropdown_display = dropdown_displays[current_dropdown_index]
                    
                    # Calculate dropdown position
                    dropdown_y = dropdown_base_y_list[current_dropdown_index]
                    dropdown_height = dropdown_max_visible * dropdown_item_height
                    dropdown_x = 270
                    adjusted_y = dropdown_y - scroll_offset
                    
                    # Items 1-2 (index 0-1) open downward, items 3+ (index 2+) open upward
                    if current_dropdown_index >= 2:
                        # Open upwards
                        dropdown_list.set_pos(dropdown_x, adjusted_y - dropdown_height)
                        dropdown_open_upward = True
                    else:
                        # Open downwards
                        dropdown_list.set_pos(dropdown_x, adjusted_y + 30)
                        dropdown_open_upward = False
                    
                    # Show dropdown list
                    dropdown_list.set_height(dropdown_height)
                    dropdown_list.set_style_bg_opa(lv.OPA.COVER, 0)
                    
                    # Clear previous dropdown items if any
                    for item_label in dropdown_item_labels:
                        item_label.delete()
                    dropdown_item_labels = []
                    
                    # Create dropdown option items
                    item_height = dropdown_item_height
                    for i, option in enumerate(options):
                        item_label = lv.label(dropdown_list)
                        item_label.set_text(option)
                        item_label.set_style_text_font(lv.font_montserrat_18, 0)
                        item_label.set_pos(5, i * item_height)
                        item_label.set_style_text_color(lv.color_hex(0xffffff), 0)
                        item_label.add_style(dropdown_item_style, 0)
                        
                        if i == current_dropdown_selection:
                            item_label.add_style(dropdown_selected_style, 0)
                        
                        dropdown_item_labels.append(item_label)
                    
                    # Position selection box over current dropdown option (smaller box for dropdown)
                    item_height = dropdown_item_height
                    
                    if dropdown_open_upward:
                        dropdown_y = adjusted_y - dropdown_height + (current_dropdown_selection * item_height)
                    else:
                        dropdown_y = adjusted_y + 30 + (current_dropdown_selection * item_height)
                    
                    dropdown_x = 275
                    selection_box.set_size(70, item_height - 10)  # Smaller size for dropdown options
                    selection_box.set_pos(dropdown_x, dropdown_y)
    
    # Close any open dropdown before returning
    if in_dropdown_selection:
        for i, dropdown_list in enumerate(dropdown_lists):
            dropdown_list.set_height(0)
            dropdown_list.set_style_bg_opa(lv.OPA.TRANSP, 0)
        for item_label in dropdown_item_labels:
            item_label.delete()
        dropdown_item_labels = []
    
    # Return to original page by recreating all elements
    if should_recreate:
        recreate_main_page()




