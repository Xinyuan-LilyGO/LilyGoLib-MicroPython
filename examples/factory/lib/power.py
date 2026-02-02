import lvgl as lv
import time
import machine

recreate_main_page = None
encoder = None

def set_references(recreate_func, encoder_obj=None):
    global recreate_main_page, encoder
    recreate_main_page = recreate_func
    if encoder_obj is not None:
        encoder = encoder_obj

def power():
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
    
    text_set_label1 = lv.label(scr)
    text_set_label1.set_text("Seiect a shutdown method:")
    text_set_label1.set_style_text_font(lv.font_montserrat_16, 0)
    text_set_label1.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    text_set_label1.set_pos(150, 85)  # Position next to symbol
    
    text_set_label2 = lv.label(scr)
    text_set_label2.set_text("1. Sleep: Set to sleep mode and\npress the Boot button to wake up.")
    text_set_label2.set_style_text_font(lv.font_montserrat_16, 0)
    text_set_label2.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    text_set_label2.set_pos(35, 103)
    
    text_set_label3 = lv.label(scr)
    text_set_label3.set_text("2. Shutdown: Turn off the device\n(requires removing the USB-C port).")
    text_set_label3.set_style_text_font(lv.font_montserrat_16, 0)
    text_set_label3.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    text_set_label3.set_pos(35, 138)
    
    text_set_label4 = lv.label(scr)
    text_set_label4.set_text("After shutting down, press and hold the Power button\nor plug in a USB-C port to activate the device.")
    text_set_label4.set_style_text_font(lv.font_montserrat_16, 0)
    text_set_label4.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    text_set_label4.set_pos(35, 173)
    
    # Item 1: Display & Backlight
    btn1 = lv.button(scr)
    btn1.set_size(100, 40) 
    btn1.set_pos(20, 220)
    btn1.set_style_bg_color(lv.color_hex(0xffffff), 0)  # Black background
    btn_label1 = lv.label(btn1)
    btn_label1.set_text("Shutdown")
    btn_label1.set_style_text_font(lv.font_montserrat_16,0)
    btn_label1.set_style_text_color(lv.color_hex(0x000000), 0)  # White text
    btn_label1.center()
    
    selection_items.append(btn1)  # Use symbol as reference for selection
    item_positions.append((15, 215))  # Adjusted position: left 3px total, up 4px total
    item_sizes.append((110, 50))  # Long size for other items
    
    # Item 2: 
    
    btn2 = lv.button(scr)
    btn2.set_size(100, 40) 
    btn2.set_pos(190, 220)
    btn2.set_style_bg_color(lv.color_hex(0xffffff), 0)  # Black background
    btn_label2 = lv.label(btn2)
    btn_label2.set_text("Sleep")
    btn_label2.set_style_text_font(lv.font_montserrat_16,0)
    btn_label2.set_style_text_color(lv.color_hex(0x000000), 0)  # White text
    btn_label2.center()
    
    selection_items.append(btn2)
    item_positions.append((185, 215))  # Adjusted position: left 3px total, up 4px total
    item_sizes.append((110, 50))  # Long size
    
    # Item 3: 
    btn3 = lv.button(scr)
    btn3.set_size(100, 40) 
    btn3.set_pos(360, 220)
    btn3.set_style_bg_color(lv.color_hex(0xffffff), 0)  # Black background
    btn_label3 = lv.label(btn3)
    btn_label3.set_text("Close")
    btn_label3.set_style_text_font(lv.font_montserrat_16,0)
    btn_label3.set_style_text_color(lv.color_hex(0x000000), 0)  # White text
    btn_label3.center()
    
    selection_items.append(btn3)
    item_positions.append((355, 215))  # Adjusted position: left 3px total, up 4px total
    item_sizes.append((110, 50))  # Long size
    
    
    
    # Position selection box over first item (back button) by default
    current_selection = 0
    x, y = item_positions[current_selection]
    width, height = item_sizes[current_selection]
    selection_box.set_size(width, height)
    selection_box.set_pos(x, y)
    
    # Scroll offset to handle items that go beyond screen
    scroll_offset = 0
    max_visible_items = 4  # Number of items that can be fully visible (0-5)
    
    # Handle encoder input in setting page
    while True:
        key = encoder.update()
        
        if key == "down":
            # Move selection down
            old_selection = current_selection
            current_selection = (current_selection + 1) % 4
            
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
            
        elif key == "up":
            # Move selection up
            old_selection = current_selection
            current_selection = (current_selection - 1) % 4
            
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
            

        elif key == "enter":
            # Check if back button is selected
            if current_selection == 0:
                break  # Exit the loop to return to main page
            # For other selections, you can add specific handling here
            elif current_selection == 1:
                # Shutdown mode: Turn off the device
                try:
                    # Turn off screen backlight first - more robust method
                    try:
                        from machine import Pin, PWM
                        
                        # Ensure pin is configured as output
                        display_pin = Pin(42, Pin.OUT)
                        
                        # Create PWM with frequency and set duty to 0
                        display_pwm = PWM(display_pin, freq=1000, duty=0)
                        
                        # Alternative method - direct pin control if PWM fails
                        display_pin.value(0)
                        
                        print("Display backlight turned off")
                    except Exception as backlight_error:
                        print("Display backlight control failed:", backlight_error)
                        # Fallback: try direct pin control
                        try:
                            display_pin = Pin(42, Pin.OUT)
                            display_pin.value(0)
                        except:
                            pass
                    
                    # Wait a moment for display to turn off
                    time.sleep_ms(500)
                    
                    # Simple shutdown using machine reset
                    machine.reset()
                except Exception as e:
                    print("Shutdown error:", e)
                    pass
            
            elif current_selection == 2:
                # Sleep mode: Enter sleep mode and wait for BOOT button (GPIO0)
                try:
                    # Turn off screen backlight first - more robust method
                    try:
                        from machine import Pin, PWM
                        
                        # Ensure pin is configured as output
                        display_pin = Pin(42, Pin.OUT)
                        
                        # Create PWM with frequency and set duty to 0
                        display_pwm = PWM(display_pin, freq=1000, duty=0)
                        
                        # Alternative method - direct pin control if PWM fails
                        display_pin.value(0)
                        
                        print("Display backlight turned off")
                    except Exception as backlight_error:
                        print("Display backlight control failed:", backlight_error)
                        # Fallback: try direct pin control
                        try:
                            display_pin = Pin(42, Pin.OUT)
                            display_pin.value(0)
                        except:
                            pass
                    
                    # Configure GPIO0 (BOOT button) as interrupt source
                    boot_pin = Pin(0, Pin.IN, Pin.PULL_UP)
                    
                    # Clear any previous interrupts
                    boot_pin.irq(handler=None)
                    
                    # Create a simple sleep state that waits for GPIO0 press
                    sleep_active = True
                    
                    def boot_button_callback(pin):
                        nonlocal sleep_active
                        sleep_active = False
                    
                    # Set up interrupt on GPIO0 (falling edge = button press)
                    boot_pin.irq(trigger=Pin.IRQ_FALLING, handler=boot_button_callback)
                    
                    print("Entering sleep mode... Press BOOT button to wake up")
                    
                    # Simple sleep loop that waits for button press
                    while sleep_active:
                        # Check if we should exit (button pressed)
                        time.sleep_ms(100)  # Check every 100ms
                    
                    # Button pressed - wake up!
                    print("Waking up from sleep mode...")
                    
                    # Turn on screen backlight - more robust method
                    try:
                        from machine import Pin, PWM
                        
                        # Ensure pin is configured as output
                        display_pin = Pin(42, Pin.OUT)
                        
                        # Create PWM with frequency and set duty to 50% (32768)
                        display_pwm = PWM(display_pin, freq=1000, duty=32768)
                        
                        # Alternative method - direct pin control if PWM fails
                        display_pin.value(1)
                        
                        print("Display backlight turned on")
                    except Exception as backlight_error:
                        print("Display backlight control failed:", backlight_error)
                        # Fallback: try direct pin control
                        try:
                            display_pin = Pin(42, Pin.OUT)
                            display_pin.value(1)
                        except:
                            pass
                    
                    # Clear interrupt handler
                    boot_pin.irq(handler=None)
                    
                except Exception as e:
                    print("Sleep mode error:", e)
                    pass
            
            elif current_selection == 3:
                break
            
                
    # Return to original page by recreating all elements
    recreate_main_page()

