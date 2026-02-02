import lvgl as lv
from machine import Pin, PWM
import time

recreate_main_page = None
encoder = None
_setting = None

# PWM objects for brightness control
display_pwm = None
keyboard_pwm = None

# Persistent brightness settings
saved_display_brightness = 100  # Default to max brightness
saved_keyboard_brightness = 30  # Default keyboard brightness

def set_references(recreate_func, encoder_obj, setting_func):
    global recreate_main_page, encoder, _setting
    recreate_main_page = recreate_func
    encoder = encoder_obj
    _setting = setting_func

def init_pwm_pins():
    """Initialize PWM pins for brightness control (only once)"""
    global display_pwm, keyboard_pwm
    
    # Only initialize if not already done
    if display_pwm is None:
        # Initialize display backlight PWM (pin 42)
        display_pin = Pin(42, Pin.OUT)
        display_pwm = PWM(display_pin)
        display_pwm.freq(1000)  # 1kHz frequency
        
        # Initialize keyboard brightness PWM (pin 46)
        keyboard_pin = Pin(46, Pin.OUT)
        keyboard_pwm = PWM(keyboard_pin)
        keyboard_pwm.freq(1000)  # 1kHz frequency
        
        # Set default brightness levels only on first initialization
        set_display_brightness(saved_display_brightness)
        set_keyboard_brightness(saved_keyboard_brightness)

def set_display_brightness(percentage):
    """Set display backlight brightness (0-100%)"""
    if display_pwm:
        # Convert percentage to duty cycle (0-65535)
        duty = int((percentage / 100) * 65535)
        display_pwm.duty_u16(duty)

def set_keyboard_brightness(percentage):
    """Set keyboard brightness (0-100%)"""
    if keyboard_pwm:
        # Convert percentage to duty cycle (0-65535)
        duty = int((percentage / 100) * 65535)
        keyboard_pwm.duty_u16(duty)

def display_backlight():
    # Initialize PWM pins for brightness control
    init_pwm_pins()
    
    # Declare global variables at function start
    global saved_display_brightness, saved_keyboard_brightness
    
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
    
    # Create text labels for slider values
    slider_value_labels = []
    
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
    symbol_set_label1.set_pos(20, 115)
    
    text_set_label1 = lv.label(scr)
    text_set_label1.set_text("Display Backlight")
    text_set_label1.set_style_text_font(lv.font_montserrat_20, 0)
    text_set_label1.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    text_set_label1.set_pos(20, 85)  # Position next to symbol
    
    # Create slider for Display Backlight
    slider1 = lv.slider(scr)
    slider1.set_range(0, 100)
    slider1.set_value(saved_display_brightness, 0)  # Use saved brightness value
    slider1.set_size(300, 10)  # Smaller size for slider
    slider1.set_pos(50, 120)  # Position on the right side
    
    # 设置滑块为黑色
    slider1.set_style_bg_color(lv.color_hex(0xffffff), lv.PART.MAIN)  # 滑块背景黑色
    slider1.set_style_bg_opa(lv.OPA.COVER, lv.PART.MAIN)  # 背景不透明度
    slider1.set_style_bg_color(lv.color_hex(0xffffff), lv.PART.INDICATOR)  # 已填充部分为深灰色
    slider1.set_style_bg_opa(lv.OPA.COVER, lv.PART.INDICATOR)  # 指示器不透明度
    slider1.set_style_bg_color(lv.color_hex(0xffffff), lv.PART.KNOB)  # 滑块旋钮为浅灰色
    slider1.set_style_bg_opa(lv.OPA.COVER, lv.PART.KNOB)  # 旋钮不透明度
    slider1.set_style_outline_color(lv.color_hex(0xffffff), lv.PART.KNOB)  # 旋钮轮廓为白色
    slider1.set_style_outline_width(1, lv.PART.KNOB)  # 轮廓宽度1像素
    slider1.set_style_outline_opa(lv.OPA.COVER, lv.PART.KNOB)  # 轮廓不透明度
    
    # Add value label for Display Backlight slider
    value_label1 = lv.label(scr)
    value_label1.set_text(f"{saved_display_brightness}%")  # Display saved brightness value
    value_label1.set_style_text_font(lv.font_montserrat_20, 0)
    value_label1.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    value_label1.set_pos(360, 115)  # Position to the right of slider
    
    # Create callback for Display Backlight slider
    def slider1_callback(event):
        if event.get_code() == lv.EVENT.VALUE_CHANGED:
            value = slider1.get_value()
            value_label1.set_text(f"{value}%")
            set_display_brightness(value)  # Control actual hardware
            global saved_display_brightness
            saved_display_brightness = value  # Save to persistent storage
    
    slider1.add_event_cb(slider1_callback, lv.EVENT.VALUE_CHANGED, None)
    
    selection_items.append(text_set_label1)  # Use symbol as reference for selection
    item_positions.append((15, 110))  # Adjusted position: left 3px total, up 4px total
    item_sizes.append((440, 30))  # Long size for other items
    slider_value_labels.append(value_label1)
    
    # Item 2: System Info
    symbol_set_label2 = lv.label(scr)
    symbol_set_label2.set_text(lv.SYMBOL.SETTINGS)
    symbol_set_label2.set_style_text_font(lv.font_montserrat_20, 0)
    symbol_set_label2.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    symbol_set_label2.set_pos(20, 175)
    
    text_set_label2 = lv.label(scr)
    text_set_label2.set_text("Keyboard Brightness")
    text_set_label2.set_style_text_font(lv.font_montserrat_20, 0)
    text_set_label2.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    text_set_label2.set_pos(20, 145)
    
    # Create slider for Keyboard Brightness
    slider2 = lv.slider(scr)
    slider2.set_range(0, 100)
    slider2.set_value(saved_keyboard_brightness, 0)  # Use saved keyboard brightness value
    slider2.set_size(300, 10)  # Smaller size for slider
    slider2.set_pos(50, 180)  # Position on the right side
    
    # 设置滑块为黑色
    slider2.set_style_bg_color(lv.color_hex(0xffffff), lv.PART.MAIN)  # 滑块背景黑色
    slider2.set_style_bg_opa(lv.OPA.COVER, lv.PART.MAIN)  # 背景不透明度
    slider2.set_style_bg_color(lv.color_hex(0xffffff), lv.PART.INDICATOR)  # 已填充部分为深灰色
    slider2.set_style_bg_opa(lv.OPA.COVER, lv.PART.INDICATOR)  # 指示器不透明度
    slider2.set_style_bg_color(lv.color_hex(0xffffff), lv.PART.KNOB)  # 滑块旋钮为浅灰色
    slider2.set_style_bg_opa(lv.OPA.COVER, lv.PART.KNOB)  # 旋钮不透明度
    slider2.set_style_outline_color(lv.color_hex(0xffffff), lv.PART.KNOB)  # 旋钮轮廓为白色
    slider2.set_style_outline_width(1, lv.PART.KNOB)  # 轮廓宽度1像素
    slider2.set_style_outline_opa(lv.OPA.COVER, lv.PART.KNOB)  # 轮廓不透明度
    
    # Add value label for Keyboard Brightness slider
    value_label2 = lv.label(scr)
    value_label2.set_text(f"{saved_keyboard_brightness}%")  # Display saved keyboard brightness value
    value_label2.set_style_text_font(lv.font_montserrat_20, 0)
    value_label2.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    value_label2.set_pos(360, 175)  # Position to the right of slider
    
    # Create callback for Keyboard Brightness slider
    def slider2_callback(event):
        if event.get_code() == lv.EVENT.VALUE_CHANGED:
            value = slider2.get_value()
            value_label2.set_text(f"{value}%")
            set_keyboard_brightness(value)  # Control actual hardware
            global saved_keyboard_brightness
            saved_keyboard_brightness = value  # Save to persistent storage
    
    slider2.add_event_cb(slider2_callback, lv.EVENT.VALUE_CHANGED, None)
    
    # Sync current slider values to hardware (if PWM already initialized)
    if display_pwm is not None:
        set_display_brightness(slider1.get_value())
    if keyboard_pwm is not None:
        set_keyboard_brightness(slider2.get_value())
    
    selection_items.append(text_set_label2)
    item_positions.append((15, 170))  # Adjusted position: left 3px total, up 4px total
    item_sizes.append((440, 30))  # Long size
    slider_value_labels.append(value_label2)
    
    # Item 3: Devices status
    symbol_set_label3 = lv.label(scr)
    symbol_set_label3.set_text(lv.SYMBOL.SETTINGS)
    symbol_set_label3.set_style_text_font(lv.font_montserrat_20, 0)
    symbol_set_label3.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    symbol_set_label3.set_pos(20, 235)
    
    text_set_label3 = lv.label(scr)
    text_set_label3.set_text("Display Timeout")
    text_set_label3.set_style_text_font(lv.font_montserrat_20, 0)
    text_set_label3.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    text_set_label3.set_pos(20, 205)
    
    # Create slider for Display Timeout
    slider3 = lv.slider(scr)
    slider3.set_range(0, 180)  # Timeout values in seconds (5-60 seconds)
    slider3.set_value(30, 0)  # Default 30 seconds
    slider3.set_size(300, 10)  # Smaller size for slider
    slider3.set_pos(50, 240)  # Position on the right side
    
    # 设置滑块为黑色
    slider3.set_style_bg_color(lv.color_hex(0xffffff), lv.PART.MAIN)  # 滑块背景黑色
    slider3.set_style_bg_opa(lv.OPA.COVER, lv.PART.MAIN)  # 背景不透明度
    slider3.set_style_bg_color(lv.color_hex(0xffffff), lv.PART.INDICATOR)  # 已填充部分为深灰色
    slider3.set_style_bg_opa(lv.OPA.COVER, lv.PART.INDICATOR)  # 指示器不透明度
    slider3.set_style_bg_color(lv.color_hex(0xffffff), lv.PART.KNOB)  # 滑块旋钮为浅灰色
    slider3.set_style_bg_opa(lv.OPA.COVER, lv.PART.KNOB)  # 旋钮不透明度
    slider3.set_style_outline_color(lv.color_hex(0xffffff), lv.PART.KNOB)  # 旋钮轮廓为白色
    slider3.set_style_outline_width(1, lv.PART.KNOB)  # 轮廓宽度1像素
    slider3.set_style_outline_opa(lv.OPA.COVER, lv.PART.KNOB)  # 轮廓不透明度
    
    # Add value label for Display Timeout slider
    value_label3 = lv.label(scr)
    value_label3.set_text("30s")
    value_label3.set_style_text_font(lv.font_montserrat_20, 0)
    value_label3.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    value_label3.set_pos(360, 235)  # Position to the right of slider
    
    # Create callback for Display Timeout slider
    def slider3_callback(event):
        if event.get_code() == lv.EVENT.VALUE_CHANGED:
            value = slider3.get_value()
            value_label3.set_text(f"{value}s")
    
    slider3.add_event_cb(slider3_callback, lv.EVENT.VALUE_CHANGED, None)
    
    selection_items.append(text_set_label3)
    item_positions.append((15, 230))  # Adjusted position: left 3px total, up 4px total
    item_sizes.append((440, 30))  # Long size
    slider_value_labels.append(value_label3)
    
    # Position selection box over first item (back button) by default
    current_selection = 0
    x, y = item_positions[current_selection]
    width, height = item_sizes[current_selection]
    selection_box.set_size(width, height)
    selection_box.set_pos(x, y)
    
    # State: 0 = selection mode, 1 = slider adjustment mode
    adjustment_mode = 0
    current_slider = None
    
    while True:
        key = encoder.update()
        
        if adjustment_mode == 0:
            # Selection mode
            if key == "down":
                # Move selection down
                current_selection = (current_selection + 1) % 4
                # Move and resize selection box to new position
                x, y = item_positions[current_selection]
                width, height = item_sizes[current_selection]
                selection_box.set_size(width, height)
                selection_box.set_pos(x, y)
                
            elif key == "up":
                # Move selection up
                current_selection = (current_selection - 1) % 4
                # Move and resize selection box to new position
                x, y = item_positions[current_selection]
                width, height = item_sizes[current_selection]
                selection_box.set_size(width, height)
                selection_box.set_pos(x, y)
                
            elif key == "enter":
                # Check if back button is selected
                if current_selection == 0:
                    break  # Exit the loop to return to main page
                elif current_selection in [1, 2, 3]:
                    # Enter slider adjustment mode
                    adjustment_mode = 1
                    if current_selection == 1:
                        current_slider = slider1
                    elif current_selection == 2:
                        current_slider = slider2
                    elif current_selection == 3:
                        current_slider = slider3
                        
        elif adjustment_mode == 1:
            # Slider adjustment mode
            if key == "down":
                # Decrease slider value
                current_value = current_slider.get_value()
                new_value = max(current_value - 1, current_slider.get_min_value())
                current_slider.set_value(new_value, 0)
                
                # Update corresponding text label and hardware control
                if current_selection == 1:  # Display Backlight
                    value_label1.set_text(f"{new_value}%")
                    set_display_brightness(new_value)  # Control actual hardware
                    global saved_display_brightness
                    saved_display_brightness = new_value  # Save to persistent storage
                elif current_selection == 2:  # Keyboard Brightness
                    value_label2.set_text(f"{new_value}%")
                    set_keyboard_brightness(new_value)  # Control actual hardware
                    global saved_keyboard_brightness
                    saved_keyboard_brightness = new_value  # Save to persistent storage
                elif current_selection == 3:  # Display Timeout
                    value_label3.set_text(f"{new_value}s")
                
            elif key == "up":
                # Increase slider value
                current_value = current_slider.get_value()
                new_value = min(current_value + 1, current_slider.get_max_value())
                current_slider.set_value(new_value, 0)
                
                # Update corresponding text label and hardware control
                if current_selection == 1:  # Display Backlight
                    value_label1.set_text(f"{new_value}%")
                    set_display_brightness(new_value)  # Control actual hardware
                    global saved_display_brightness
                    saved_display_brightness = new_value  # Save to persistent storage
                elif current_selection == 2:  # Keyboard Brightness
                    value_label2.set_text(f"{new_value}%")
                    set_keyboard_brightness(new_value)  # Control actual hardware
                    global saved_keyboard_brightness
                    saved_keyboard_brightness = new_value  # Save to persistent storage
                elif current_selection == 3:  # Display Timeout
                    value_label3.set_text(f"{new_value}s")
                
            elif key == "enter":
                # Exit slider adjustment mode
                adjustment_mode = 0
                current_slider = None
    
    # Save current brightness settings before exiting
    global saved_display_brightness, saved_keyboard_brightness
    saved_display_brightness = slider1.get_value()
    saved_keyboard_brightness = slider2.get_value()
    
    # Keep PWM objects alive but don't deinit them
    # This ensures the brightness settings persist after exiting
    
    # Return to original page by recreating all elements
    return

