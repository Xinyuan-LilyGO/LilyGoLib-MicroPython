import lvgl as lv
import time
import network

recreate_main_page = None
encoder = None

def set_references(recreate_func, encoder_obj=None):
    global recreate_main_page, encoder
    recreate_main_page = recreate_func
    if encoder_obj is not None:
        encoder = encoder_obj

def wireless():
    # Clear all current screen elements
    scr = lv.screen_active()
    # Remove all children from the screen
    while True:
        child = scr.get_child(0)
        if child is None:
            break
        child.delete()
    
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

    # Password
    symbol_set_label1 = lv.label(scr)
    symbol_set_label1.set_text(lv.SYMBOL.WIFI)
    symbol_set_label1.set_style_text_font(lv.font_montserrat_20, 0)
    symbol_set_label1.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    symbol_set_label1.set_pos(30, 110)

    text_set_label1 = lv.label(scr)
    text_set_label1.set_text("Password: ")
    text_set_label1.set_style_text_font(lv.font_montserrat_20, 0)
    text_set_label1.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    text_set_label1.set_pos(60, 110)  # Position next to symbol

    # Add password input box
    password_input = lv.textarea(scr)
    password_input.set_size(250, 35)
    password_input.set_pos(170, 105)
    password_input.set_placeholder_text("password")
    password_input.set_style_text_color(lv.color_hex(0xffffff), 0)
    password_input.set_style_border_color(lv.color_hex(0xffffff), 0)
    password_input.set_style_border_width(1, 0)
    password_input.set_style_border_opa(lv.OPA.COVER, 0)
    password_input.set_style_radius(3, 0)
    password_input.set_one_line(True)

    # Initialize saved credentials variables
    saved_password = ""
    saved_ssid = ""

    # Set initial password display (show asterisks if password exists)
    if saved_password:
        password_input.set_text('*' * len(saved_password))

    # Set initial SSID display if exists
    if saved_ssid:
        ssid_input.set_text(saved_ssid)

    selection_items.append(symbol_set_label1)  # Use symbol as reference for selection
    item_positions.append((168, 102))  # Adjusted position: left 3px total, up 4px total
    item_sizes.append((255, 40))  # Long size for password field

    # SSID
    symbol_set_label2 = lv.label(scr)
    symbol_set_label2.set_text(lv.SYMBOL.WIFI)
    symbol_set_label2.set_style_text_font(lv.font_montserrat_20, 0)
    symbol_set_label2.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    symbol_set_label2.set_pos(30, 170)

    text_set_label2 = lv.label(scr)
    text_set_label2.set_text("SSID: ")
    text_set_label2.set_style_text_font(lv.font_montserrat_20, 0)
    text_set_label2.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    text_set_label2.set_pos(60, 170)

    # Create a custom dropdown-like interface

    # 1. Create a text input field that looks like a dropdown
    ssid_input = lv.textarea(scr)
    ssid_input.set_size(250, 35)
    ssid_input.set_pos(170, 165)
    ssid_input.set_placeholder_text("SSID")
    ssid_input.set_one_line(True)
    ssid_input.set_style_text_color(lv.color_hex(0xffffff), 0)
    ssid_input.set_style_border_color(lv.color_hex(0xffffff), 0)
    ssid_input.set_style_border_width(1, 0)
    ssid_input.set_style_border_opa(lv.OPA.COVER, 0)
    ssid_input.set_style_radius(3, 0)
    ssid_input.set_style_bg_opa(lv.OPA.TRANSP, 0)

    # 2. Create a down arrow symbol next to the input
    arrow_symbol = lv.label(scr)
    arrow_symbol.set_text(lv.SYMBOL.DOWN)
    arrow_symbol.set_style_text_font(lv.font_montserrat_20, 0)
    arrow_symbol.set_style_text_color(lv.color_hex(0xffffff), 0)
    arrow_symbol.set_pos(170 + 230, 170)

    # 4. Create styles for dropdown items
    dropdown_item_style = lv.style_t()
    dropdown_item_style.init()
    dropdown_item_style.set_pad_ver(5)
    dropdown_item_style.set_pad_hor(10)
    dropdown_item_style.set_text_color(lv.color_hex(0xffffff))
    dropdown_item_style.set_bg_opa(lv.OPA.TRANSP)

    # 5. Create style for selected dropdown item
    dropdown_selected_style = lv.style_t()
    dropdown_selected_style.init()
    dropdown_selected_style.set_pad_ver(5)
    dropdown_selected_style.set_pad_hor(10)
    dropdown_selected_style.set_text_color(lv.color_hex(0xffffff))
    dropdown_selected_style.set_bg_color(lv.color_hex(0x808080))  # Gray background
    dropdown_selected_style.set_bg_opa(lv.OPA.COVER)

    # Add state variables for dropdown selection mode
    in_dropdown_selection = False
    current_dropdown_selection = 0
    dropdown_options = []

    # Global variable to store password persistently
    saved_password = ''
    dropdown_items = []

    # Simplified approach - use LVGL's built-in direction setting
    # This is more reliable than manual positioning in most cases

    selection_items.append(symbol_set_label2)
    item_positions.append((168, 162))  # Adjusted position: left 3px total, up 4px total
    item_sizes.append((255, 40))  # Long size for SSID field (same as password)

    # Add Refresh button as circular button at bottom middle
    refresh_btn = lv.button(scr)
    refresh_btn.set_size(50, 50)
    refresh_btn.set_pos(170, 215)  # Bottom center position
    refresh_btn.set_style_bg_color(lv.color_hex(0xffffff), 0)  # Black background
    refresh_btn.set_style_border_color(lv.color_hex(0xffffff), 0)
    refresh_btn.set_style_border_width(1, 0)
    refresh_btn.set_style_radius(25, 0)  # Circular button

    refresh_label = lv.label(refresh_btn)
    refresh_label.set_text(lv.SYMBOL.REFRESH)
    refresh_label.set_style_text_font(lv.font_montserrat_20, 0)
    refresh_label.set_style_text_color(lv.color_hex(0x000000), 0)  # White icon
    refresh_label.center()  # Center the label within the button

    # Add Refresh button to selection items
    selection_items.append(refresh_btn)
    item_positions.append((170, 215))  # Same position as refresh button
    item_sizes.append((50, 50))  # Same size as refresh button (50x50 circular)

    # Add OK button as circular button at bottom middle
    ok_btn = lv.button(scr)
    ok_btn.set_size(50, 50)
    ok_btn.set_pos(260, 215)  # Bottom center position, right of refresh button
    ok_btn.set_style_bg_color(lv.color_hex(0xffffff), 0)  # Black background
    ok_btn.set_style_border_color(lv.color_hex(0xffffff), 0)
    ok_btn.set_style_border_width(1, 0)
    ok_btn.set_style_radius(25, 0)  # Circular button

    ok_label = lv.label(ok_btn)
    ok_label.set_text(lv.SYMBOL.OK)
    ok_label.set_style_text_font(lv.font_montserrat_20, 0)
    ok_label.set_style_text_color(lv.color_hex(0x000000), 0)  # White icon
    ok_label.center()  # Center the label within the button

    # Add OK button to selection items
    selection_items.append(ok_btn)
    item_positions.append((260, 215))  # Same position as OK button
    item_sizes.append((50, 50))  # Same size as OK button (50x50 circular)

    # 3. Create a custom dropdown list container (initially hidden) - created after buttons to ensure it appears on top
    dropdown_list_container = lv.obj(scr)
    dropdown_list_container.set_size(250, 0)  # Start with 0 height
    dropdown_list_container.set_pos(170, 165 + 35 + 2)
    dropdown_list_container.set_style_border_width(1, 0)
    dropdown_list_container.set_style_border_color(lv.color_hex(0xffffff), 0)
    dropdown_list_container.set_style_bg_color(lv.color_hex(0x000000), 0)
    dropdown_list_container.set_style_radius(3, 0)
    dropdown_list_container.set_style_clip_corner(True, 0)
    dropdown_list_container.set_style_bg_opa(lv.OPA.TRANSP, 0)  # Initially transparent

    # Position selection box over first item (back button) by default
    current_selection = 0
    x, y = item_positions[current_selection]
    width, height = item_sizes[current_selection]
    selection_box.set_size(width, height)
    selection_box.set_pos(x, y)

    # Add state variables for dropdown selection mode
    in_dropdown_selection = False
    current_dropdown_selection = 0
    dropdown_options = []

    # Create WiFi scanning progress page (initially hidden)
    scanning_page = lv.obj(scr)
    scanning_page.set_size(480, 320)
    scanning_page.set_pos(0, 0)
    scanning_page.set_style_bg_color(lv.color_hex(0x000000), 0)  # White background
    scanning_page.set_style_bg_opa(lv.OPA.COVER, 0)
    scanning_page.set_style_border_width(0, 0)
    scanning_page.set_style_opa(lv.OPA.TRANSP, 0)  # Initially hidden (transparent)

    # Create progress bar
    progress_bar = lv.bar(scanning_page)
    progress_bar.set_size(200, 10)
    progress_bar.set_pos(130, 150)
    progress_bar.set_style_bg_color(lv.color_hex(0xe0e0e0), 0)  # Light gray background
    progress_bar.set_style_bg_opa(lv.OPA.COVER, 0)
    progress_bar.set_style_border_width(0, 0)
    progress_bar.set_style_radius(5, 0)

    # Style for progress indicator
    progress_style = lv.style_t()
    progress_style.init()
    progress_style.set_bg_color(lv.color_hex(0x00bfff))  # Blue progress color
    progress_style.set_bg_opa(lv.OPA.COVER)
    progress_style.set_radius(5)
    progress_bar.add_style(progress_style, lv.PART.INDICATOR)

    # Create scanning text
    scanning_text = lv.label(scanning_page)
    scanning_text.set_text("WiFi Scanning...")
    scanning_text.set_style_text_font(lv.font_montserrat_20, 0)
    scanning_text.set_style_text_color(lv.color_hex(0xffffff), 0)  # Black text
    scanning_text.set_pos(150, 180)

    # Create WiFi connection result page (initially hidden)
    connection_result_page = lv.obj(scr)
    connection_result_page.set_size(480, 320)
    connection_result_page.set_pos(0, 0)
    connection_result_page.set_style_bg_color(lv.color_hex(0x000000), 0)  # Black background
    connection_result_page.set_style_bg_opa(lv.OPA.COVER, 0)
    connection_result_page.set_style_border_width(0, 0)
    connection_result_page.set_style_opa(lv.OPA.TRANSP, 0)  # Initially hidden (transparent)

    # Create connection status text
    connection_text = lv.label(connection_result_page)
    connection_text.set_text("Connected ")  # Initial text, will be updated
    connection_text.set_style_text_font(lv.font_montserrat_20, 0)
    connection_text.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    connection_text.set_pos(50, 100)

    # Create Close button
    close_button = lv.button(connection_result_page)
    close_button.set_size(100, 40)
    close_button.set_pos(190, 180)

    # Style Close button
    close_button.set_style_bg_color(lv.color_hex(0x333333), 0)  # Dark gray background
    close_button.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    close_button.set_style_border_width(1, 0)
    close_button.set_style_border_color(lv.color_hex(0xffffff), 0)
    close_button.set_style_radius(5, 0)

    # Add text to Close button
    close_button_label = lv.label(close_button)
    close_button_label.set_text("Close")
    close_button_label.center()

    # Handle encoder input in setting page
    while True:
        key = encoder.update()
        
        if in_dropdown_selection:
            # Handle selection within custom dropdown
            if key == "down":
                # Move selection down in dropdown
                if dropdown_options:
                    # Store previous selection to update styles later
                    prev_selection = current_dropdown_selection
                    
                    # Update current selection
                    current_dropdown_selection = (current_dropdown_selection + 1) % len(dropdown_options)
                    item_height = 30
                    max_height = 150
                    
                    # Update styles for all items
                    for i, item in enumerate(dropdown_items):
                        if i == current_dropdown_selection:
                            item.add_style(dropdown_selected_style, 0)
                        else:
                            item.remove_style(dropdown_selected_style, 0)
                    
                    # Calculate scroll offset - selected item always at position 0
                    scroll_offset = current_dropdown_selection
                    
                    # Update dropdown items positions to create scroll effect
                    # Only non-selected items scroll, selected item stays at top
                    for i, item in enumerate(dropdown_items):
                        if i == current_dropdown_selection:
                            item.set_pos(0, 0)  # Selected item always at first position
                        else:
                            item.set_pos(0, (i - scroll_offset) * item_height)
                    
                    # Update selection box position - always at the first visible position
                    dropdown_x = dropdown_list_container.get_x() + 5
                    dropdown_y = dropdown_list_container.get_y() + 5
                    selection_box.set_size(dropdown_list_container.get_width() - 10, item_height - 10)
                    selection_box.set_pos(dropdown_x, dropdown_y)
                    
                    # Update input box to show current selection
                    ssid_input.set_text(dropdown_options[current_dropdown_selection])

            
            elif key == "up":
                # Move selection up in dropdown
                if dropdown_options:
                    # Store previous selection to update styles later
                    prev_selection = current_dropdown_selection
                    
                    # Update current selection
                    current_dropdown_selection = (current_dropdown_selection - 1) % len(dropdown_options)
                    item_height = 30
                    max_height = 150
                    
                    # Update styles for all items
                    for i, item in enumerate(dropdown_items):
                        if i == current_dropdown_selection:
                            item.add_style(dropdown_selected_style, 0)
                        else:
                            item.remove_style(dropdown_selected_style, 0)
                    
                    # Calculate scroll offset - selected item always at position 0
                    scroll_offset = current_dropdown_selection
                    
                    # Update dropdown items positions to create scroll effect
                    # Only non-selected items scroll, selected item stays at top
                    for i, item in enumerate(dropdown_items):
                        if i == current_dropdown_selection:
                            item.set_pos(0, 0)  # Selected item always at first position
                        else:
                            item.set_pos(0, (i - scroll_offset) * item_height)
                    
                    # Update selection box position - always at the first visible position
                    dropdown_x = dropdown_list_container.get_x() + 5
                    dropdown_y = dropdown_list_container.get_y() + 5
                    selection_box.set_size(dropdown_list_container.get_width() - 10, item_height - 10)
                    selection_box.set_pos(dropdown_x, dropdown_y)
                    
                    # Update input box to show current selection
                    ssid_input.set_text(dropdown_options[current_dropdown_selection])
        
            
            elif key == "enter":
                # Confirm selection and exit dropdown mode
                if dropdown_options:
                    # Set selected value to input box
                    selected_value = dropdown_options[current_dropdown_selection]
                    ssid_input.set_text(selected_value)
                    # Save selected SSID
                    saved_ssid = selected_value
                
                # Close dropdown and exit selection mode
                dropdown_list_container.set_height(0)
                dropdown_list_container.set_style_bg_opa(lv.OPA.TRANSP, 0)  # Hide container
                in_dropdown_selection = False
                
                # Restore original selection box position
                x, y = item_positions[current_selection]
                width, height = item_sizes[current_selection]
                selection_box.set_size(width, height)
                selection_box.set_pos(x, y)
        
        else:
            # Normal selection mode
            if key == "down": 
                # Move selection down
                current_selection = (current_selection + 1) % 5  # Now 5 items instead of 3
                # Move and resize selection box to new position
                x, y = item_positions[current_selection]
                width, height = item_sizes[current_selection]
                selection_box.set_size(width, height)
                selection_box.set_pos(x, y)
                
                
            elif key == "up":
                # Move selection up
                current_selection = (current_selection - 1) % 5  # Now 5 items instead of 3
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
                    # Enter password input mode
                    import time
                    
                    # Initialize keypad if not already initialized
                    if 'kb' not in globals():
                        # Reuse existing I2C if possible
                        if 'i2c' not in globals():
                            from machine import Pin, I2C
                            i2c = I2C(0, scl=Pin(2), sda=Pin(3), freq=400000)
                        import keypad
                        kb = keypad.TCA8418(i2c)
                        kb.setup_keypad()
                    
                    # Use the saved password if it exists
                    actual_password = saved_password
                    # Display asterisks for the saved password
                    password_input.set_text('*' * len(actual_password))
                    
                    # Enter keyboard input loop
                    while True:
                        key = kb.get_key()
                        if key is not None:
                            if key == 'enter':
                                # Save the password before exiting
                                saved_password = actual_password
                                break
                            elif key == 'backspace' or key == '\b':
                                # Handle backspace (both string and character representations)
                                if actual_password:
                                    actual_password = actual_password[:-1]
                                    # Update display with all asterisks
                                    password_input.set_text('*' * len(actual_password))
                                    time.sleep(0.5)
                            elif key == '\n':
                                # Save the password before exiting
                                saved_password = actual_password
                                break
                            else:
                                # Handle regular character input
                                actual_password += key
                                # Show the actual character temporarily
                                password_input.set_text(actual_password)
                                # Small delay to show the character
                                time.sleep(0.5)
                                # Replace with asterisks
                                password_input.set_text('*' * len(actual_password))
                        
                        # Check for encoder enter to exit (in case keyboard enter doesn't work)
                        encoder_key = encoder.update()
                        if encoder_key == 'enter':
                            # Save the password before exiting
                            saved_password = actual_password
                            break
                    
                    
                # Handle SSID dropdown selection
                if current_selection == 2:
                    if in_dropdown_selection:
                        # Close the custom dropdown
                        dropdown_list_container.set_height(0)
                        dropdown_list_container.set_style_bg_opa(lv.OPA.TRANSP, 0)  # Hide container
                        in_dropdown_selection = False
                        
                        # Restore original selection box position
                        x, y = item_positions[current_selection]
                        width, height = item_sizes[current_selection]
                        selection_box.set_size(width, height)
                        selection_box.set_pos(x, y)
                    else:
                        # Get current dropdown options first
                        options_text = ssid_input.get_text()
                        # Get SSID list from options (this should be updated when scan button is pressed)
                        
                        # Clear existing dropdown items
                        for item in dropdown_items:
                            item.delete()
                        dropdown_items.clear()
                        
                        if dropdown_options:
                            # Calculate appropriate height
                            max_height = 150  # Reduced height to avoid overlapping with bottom buttons
                            item_height = 30
                            total_height = min(len(dropdown_options) * item_height, max_height)
                            visible_items = max_height // item_height
                            
                            # Configure dropdown container
                            dropdown_list_container.set_height(total_height)
                            dropdown_list_container.set_style_bg_opa(lv.OPA.COVER, 0)  # Show container
                            
                            # Create dropdown items
                            for i, ssid in enumerate(dropdown_options):
                                item = lv.label(dropdown_list_container)
                                item.set_text(ssid)
                                item.set_style_text_font(lv.font_montserrat_18, 0)
                                item.add_style(dropdown_item_style, 0)
                                
                                # Apply selected style to current selection
                                if i == current_dropdown_selection:
                                    item.add_style(dropdown_selected_style, 0)
                                else:
                                    item.remove_style(dropdown_selected_style, 0)
                                    
                                item.set_pos(0, i * item_height)
                                dropdown_items.append(item)
                            
                            current_dropdown_selection = 0
                            in_dropdown_selection = True
                            
                            # Update selection box position for first item
                            dropdown_x = dropdown_list_container.get_x() + 5
                            dropdown_y = dropdown_list_container.get_y() + 5
                            selection_box.set_size(dropdown_list_container.get_width() - 10, item_height - 10)
                            selection_box.set_pos(dropdown_x, dropdown_y)
                            
                            # Set initial selection text
                            ssid_input.set_text(dropdown_options[current_dropdown_selection])
                    
                # Handle Refresh button selection
                elif current_selection == 3:
                    # Show scanning page and set text to "Scanning"
                    scanning_text.set_text("WiFi Scanning...")
                    scanning_page.set_style_opa(lv.OPA.COVER, 0)
                    
                    # Reset progress bar
                    progress_bar.set_value(0,0)
                    
                    # Simple animation for progress bar (simulate scanning progress)
                    for progress_value in range(0, 101, 10):
                        progress_bar.set_value(progress_value,0)
                        # Small delay to show progress
                        import time
                        time.sleep(0.2)
                    
                    # Scan for available WiFi networks
                    sta_if = network.WLAN(network.STA_IF)
                    sta_if.active(True)
                    available_networks = sta_if.scan()
                    
                    # Update progress bar to 100% when scan is complete
                    progress_bar.set_value(100,0)
                    
                    # Small delay to show full progress
                    import time
                    time.sleep(0.3)
                    
                    # Extract SSIDs from scan results and update dropdown
                    ssid_list = [net[0].decode('utf-8') for net in available_networks]
                    if ssid_list:
                        # Store SSIDs for custom dropdown
                        dropdown_options = ssid_list
                        # Set first SSID as initial value
                        if dropdown_options:
                            ssid_input.set_text(dropdown_options[0])
                    else:
                        # If no networks found, show a message
                        dropdown_options = ['No WiFi networks found']
                        ssid_input.set_text(dropdown_options[0])
                    
                    # Hide scanning page and return to main page
                    scanning_page.set_style_opa(lv.OPA.TRANSP, 0)
                    
                # Handle OK button selection
                elif current_selection == 4:
                    # Get current SSID and password from input fields
                    current_ssid = ssid_input.get_text()
                    current_password = saved_password
                    
                    # Save current credentials
                    saved_ssid = current_ssid
                    
                    # Show scanning page as connection progress, but update text to "Connecting"
                    scanning_text.set_text("WiFi Connecting...")
                    scanning_page.set_style_opa(lv.OPA.COVER, 0)
                    
                    # Reset progress bar
                    progress_bar.set_value(0,0)
                    
                    # Simple animation for connection progress
                    import time
                    for progress_value in range(0, 101, 10):
                        progress_bar.set_value(progress_value,0)
                        time.sleep(0.2)
                    
                    # Connect to WiFi with retry mechanism but keep same UI
                    try:
                        # Initialize WiFi station
                        sta_if = network.WLAN(network.STA_IF)
                        sta_if.active(True)
                        
                        # Connection parameters - improved but not shown in UI
                        max_retries = 3
                        timeout = 30
                        connected = False
                        connection_error = None
                        
                        # Attempt to connect with retries
                        for attempt in range(max_retries):
                            # Reset connection state
                            if sta_if.isconnected():
                                sta_if.disconnect()
                                time.sleep(1)
                            
                            # Keep UI simple - just show "Connecting" without retry count
                            scanning_text.set_text("WiFi Connecting...")
                            progress_bar.set_value(0, 0)
                            
                            # Try to connect
                            sta_if.connect(current_ssid, current_password)
                            
                            # Monitor connection progress
                            start_time = time.time()
                            
                            while (time.time() - start_time) < timeout:
                                # Update progress bar
                                elapsed = time.time() - start_time
                                progress = min(int((elapsed / timeout) * 100), 100)
                                progress_bar.set_value(progress, 0)
                                
                                # Check if connected
                                if sta_if.isconnected():
                                    connected = True
                                    break
                                
                                # Small delay to avoid excessive polling
                                time.sleep(0.5)
                            
                            # If connected, break out of retry loop
                            if connected:
                                break
                            else:
                                # Check connection status for more detailed error (but don't show in UI)
                                status = sta_if.status()
                                if status == network.STAT_WRONG_PASSWORD:
                                    connection_error = "Wrong password"
                                elif status == network.STAT_NO_AP_FOUND:
                                    connection_error = "Network not found"
                                elif status == network.STAT_CONNECT_FAIL:
                                    connection_error = "Connection failed"
                                
                                # Wait before next retry (with exponential backoff)
                                if attempt < max_retries - 1:  # Don't delay after last attempt
                                    time.sleep(2 * (attempt + 1))
                        
                        # Process connection result
                        if connected:
                            # Update progress bar to 100%
                            progress_bar.set_value(100,0)
                            time.sleep(0.3)
                            
                            # Get connection info
                            ip_info = sta_if.ifconfig()
                            ip_address = ip_info[0]
                            
                            # Keep the same UI as before
                            connection_text.set_text("Connected %s,IP:%s" % (current_ssid, ip_address))
                            
                            # Hide scanning page and show result page
                            scanning_page.set_style_opa(lv.OPA.TRANSP, 0)
                            connection_result_page.set_style_opa(lv.OPA.COVER, 0)
                            
                            # Wait for user to press enter to close
                            while True:
                                key = encoder.update()
                                if key == "enter":
                                    break
                                time.sleep(0.1)
                            
                            # Hide result page
                            connection_result_page.set_style_opa(lv.OPA.TRANSP, 0)
                            # Reset scanning page text for future use
                            scanning_text.set_text("WiFi Scanning...")
                        else:
                            # Handle connection failure - keep same UI as before
                            connection_text.set_text("Failed to connect %s" % current_ssid)
                            scanning_page.set_style_opa(lv.OPA.TRANSP, 0)
                            connection_result_page.set_style_opa(lv.OPA.COVER, 0)
                            
                            # Wait for user to press enter to close
                            while True:
                                key = encoder.update()
                                if key == "enter":
                                    break
                                time.sleep(0.1)
                            
                            # Hide result page
                            connection_result_page.set_style_opa(lv.OPA.TRANSP, 0)
                            # Reset scanning page text for future use
                            scanning_text.set_text("WiFi Scanning...")
                    except Exception as e:
                        # Handle any errors
                        connection_text.set_text("Error: %s" % str(e))
                        scanning_page.set_style_opa(lv.OPA.TRANSP, 0)
                        connection_result_page.set_style_opa(lv.OPA.COVER, 0)
                        
                        # Wait for user to press enter to close
                        while True:
                            key = encoder.update()
                            if key == "enter":
                                break
                            time.sleep(0.1)
                        
                        # Hide result page
                        connection_result_page.set_style_opa(lv.OPA.TRANSP, 0)
    
    
    
    # Clear the screen again to prepare for returning to original page
    scr = lv.screen_active()
    while True:
        child = scr.get_child(0)
        if child is None:
            break
        child.delete()
    
    # Return to original page by recreating all elements
    recreate_main_page()



