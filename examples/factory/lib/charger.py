import lvgl as lv
from machine import I2C, Pin
import time

recreate_main_page = None
encoder = None
_setting = None

# Hardware control variables
otg_enabled = False
charger_enabled = False
charger_current = 1000  # Default 1000mA

# I2C setup for BQ25896
i2c = None
xl9555 = None
otg_pin = None

def set_references(recreate_func, encoder_obj, setting_func):
    global recreate_main_page, encoder, _setting
    recreate_main_page = recreate_func
    encoder = encoder_obj
    _setting = setting_func

def init_hardware():
    """Initialize hardware components"""
    global i2c, xl9555, otg_pin
    
    if i2c is None:
        # Initialize I2C bus (GPIO3=SDA, GPIO2=SCL)
        i2c = I2C(1, scl=Pin(2), sda=Pin(3), freq=400000)
        
        try:
            # Import XL9555 driver if available
            import sys
            sys.path.append('/1')
            try:
                from xl9555 import XL9555
                xl9555 = XL9555(i2c, 0x20)
                
                # Configure XL9555 pins for charger control
                # GPIO11 (External 12-Pin socket) for OTG control
                xl9555.configure(11, 0)  # Set as output
                # GPIO10 for Keyboard power supply (alternative control)
                xl9555.configure(10, 0)  # Set as output
            except Exception as import_error:
                xl9555 = None
                # Fallback to direct GPIO control
                try:
                    otg_pin = Pin(9, Pin.OUT)  # Use GPIO9 as fallback for OTG control
                except Exception as gpio_error:
                    otg_pin = None
                
        except Exception as e:
            xl9555 = None
            # Fallback to direct GPIO control
            try:
                otg_pin = Pin(9, Pin.OUT)  # Use GPIO9 as fallback for OTG control
            except Exception as gpio_error:
                otg_pin = None

def set_otg_enable(enabled):
    """Control OTG Enable via XL9555 or direct GPIO"""
    global otg_enabled
    otg_enabled = enabled
    
    if xl9555:
        try:
            # Use GPIO11 for OTG control
            xl9555.set_pin(11, 1 if enabled else 0)
        except Exception as e:
            pass
    elif otg_pin:
        try:
            # Fallback to direct GPIO control
            otg_pin.value(1 if enabled else 0)
        except Exception as e:
            pass
    else:
        # Simulate the operation if no hardware available
        pass

def set_charger_enable(enabled):
    """Control Charger Enable via BQ25896 I2C commands"""
    global charger_enabled
    charger_enabled = enabled
    
    if i2c:
        try:
            # BQ25896 Control Register (0x03)
            if enabled:
                # Enable charging (disable HIZ mode)
                control_reg = i2c.readfrom_mem(0x6B, 0x03, 1)[0]
                control_reg &= ~0x80  # Clear HIZ bit
                i2c.writeto_mem(0x6B, 0x03, bytes([control_reg]))
            else:
                # Enable HIZ mode to disable charging
                control_reg = i2c.readfrom_mem(0x6B, 0x03, 1)[0]
                control_reg |= 0x80  # Set HIZ bit
                i2c.writeto_mem(0x6B, 0x03, bytes([control_reg]))
        except Exception as e:
            pass

def set_charger_current(current_ma):
    """Set charger current via BQ25896 I2C commands"""
    global charger_current
    charger_current = current_ma
    
    if i2c:
        try:
            # BQ25896 Input Current Limit register (0x00)
            # Convert mA to register value
            if current_ma <= 500:
                reg_value = 0x00
            elif current_ma <= 900:
                reg_value = 0x01
            elif current_ma <= 1200:
                reg_value = 0x02
            elif current_ma <= 1500:
                reg_value = 0x03
            elif current_ma <= 2000:
                reg_value = 0x04
            elif current_ma <= 3000:
                reg_value = 0x05
            else:
                reg_value = 0x06  # Max current
            
            i2c.writeto_mem(0x6B, 0x00, bytes([reg_value]))
        except Exception as e:
            pass

def charger():
    # Declare global variables
    global otg_enabled, charger_enabled, charger_current
    
    # Initialize hardware components
    init_hardware()
    
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
    
    # Create switches and sliders
    switch1 = None
    switch2 = None
    slider3 = None
    slider3_value_label = None
    
    # Item 0: Back button (lv.SYMBOL.LEFT)
    symbol_left_label = lv.label(scr)
    symbol_left_label.set_text(lv.SYMBOL.LEFT)
    symbol_left_label.set_style_text_font(lv.font_montserrat_20, 0)
    symbol_left_label.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    symbol_left_label.set_pos(20, 55)
    selection_items.append(symbol_left_label)
    item_positions.append((12, 50))  # Adjusted position: left 3px total, up 4px total
    item_sizes.append((30, 30))  # Smaller size for back button
    
    # Item 1: OTG Enable
    symbol_set_label1 = lv.label(scr)
    symbol_set_label1.set_text(lv.SYMBOL.POWER)
    symbol_set_label1.set_style_text_font(lv.font_montserrat_20, 0)
    symbol_set_label1.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    symbol_set_label1.set_pos(20, 100)
    
    text_set_label1 = lv.label(scr)
    text_set_label1.set_text("OTG Enable")
    text_set_label1.set_style_text_font(lv.font_montserrat_20, 0)
    text_set_label1.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    text_set_label1.set_pos(50, 100)  # Position next to symbol
    
    # Create switch for OTG Enable
    switch1 = lv.switch(scr)
    switch1.set_pos(400, 98)  # Position on the right side
    switch1.set_size(50, 25)  # Standard switch size
    if otg_enabled:
        switch1.add_state(lv.STATE.CHECKED)
    # Switch styles for better visibility
    switch1.set_style_bg_color(lv.color_hex(0x444444), lv.PART.MAIN)  # Inactive background
    switch1.set_style_bg_color(lv.color_hex(0x00ff00), lv.PART.INDICATOR | lv.STATE.CHECKED)  # Active indicator
    switch1.set_style_bg_color(lv.color_hex(0x666666), lv.PART.KNOB)  # Knob color inactive
    switch1.set_style_bg_color(lv.color_hex(0x00ff00), lv.PART.KNOB | lv.STATE.CHECKED)  # Knob color active
    
    selection_items.append(text_set_label1)  # Use symbol as reference for selection
    item_positions.append((15, 95))  # Adjusted position: left 3px total, up 4px total
    item_sizes.append((440, 30))  # Long size for other items
    
    # Item 2: Charger Enable
    symbol_set_label2 = lv.label(scr)
    symbol_set_label2.set_text(lv.SYMBOL.POWER)
    symbol_set_label2.set_style_text_font(lv.font_montserrat_20, 0)
    symbol_set_label2.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    symbol_set_label2.set_pos(20, 160)
    
    text_set_label2 = lv.label(scr)
    text_set_label2.set_text("Charger Enable")
    text_set_label2.set_style_text_font(lv.font_montserrat_20, 0)
    text_set_label2.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    text_set_label2.set_pos(50, 160)
    
    # Create switch for Charger Enable
    switch2 = lv.switch(scr)
    switch2.set_pos(400, 158)  # Position on the right side
    switch2.set_size(50, 25)  # Standard switch size
    if charger_enabled:
        switch2.add_state(lv.STATE.CHECKED)
    # Switch styles for better visibility
    switch2.set_style_bg_color(lv.color_hex(0x444444), lv.PART.MAIN)  # Inactive background
    switch2.set_style_bg_color(lv.color_hex(0x00ff00), lv.PART.INDICATOR | lv.STATE.CHECKED)  # Active indicator
    switch2.set_style_bg_color(lv.color_hex(0x666666), lv.PART.KNOB)  # Knob color inactive
    switch2.set_style_bg_color(lv.color_hex(0x00ff00), lv.PART.KNOB | lv.STATE.CHECKED)  # Knob color active
    
    selection_items.append(text_set_label2)
    item_positions.append((15, 155))  # Adjusted position: left 3px total, up 4px total
    item_sizes.append((440, 30))  # Long size
    
    # Item 3: Charger current
    symbol_set_label3 = lv.label(scr)
    symbol_set_label3.set_text(lv.SYMBOL.POWER)
    symbol_set_label3.set_style_text_font(lv.font_montserrat_20, 0)
    symbol_set_label3.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    symbol_set_label3.set_pos(20, 235)
    
    text_set_label3 = lv.label(scr)
    text_set_label3.set_text("Charger current")
    text_set_label3.set_style_text_font(lv.font_montserrat_20, 0)
    text_set_label3.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    text_set_label3.set_pos(20, 205)
    
    # Create slider for Charger current
    slider3 = lv.slider(scr)
    slider3.set_range(500, 3000)  # Current range: 500mA to 3000mA
    slider3.set_value(charger_current, 0)  # Use current saved value
    slider3.set_size(200, 10)  # Smaller size for slider
    slider3.set_pos(100, 240)  # Position in the middle
    
    # 设置滑块为白色主题
    slider3.set_style_bg_color(lv.color_hex(0x333333), lv.PART.MAIN)  # 滑块背景
    slider3.set_style_bg_opa(lv.OPA.COVER, lv.PART.MAIN)  # 背景不透明度
    slider3.set_style_bg_color(lv.color_hex(0xffffff), lv.PART.INDICATOR)  # 已填充部分
    slider3.set_style_bg_opa(lv.OPA.COVER, lv.PART.INDICATOR)  # 指示器不透明度
    slider3.set_style_bg_color(lv.color_hex(0xffffff), lv.PART.KNOB)  # 滑块旋钮
    slider3.set_style_bg_opa(lv.OPA.COVER, lv.PART.KNOB)  # 旋钮不透明度
    slider3.set_style_outline_color(lv.color_hex(0xffffff), lv.PART.KNOB)  # 旋钮轮廓
    slider3.set_style_outline_width(1, lv.PART.KNOB)  # 轮廓宽度1像素
    slider3.set_style_outline_opa(lv.OPA.COVER, lv.PART.KNOB)  # 轮廓不透明度
    
    # Add value label for Charger current slider
    slider3_value_label = lv.label(scr)
    slider3_value_label.set_text(f"{charger_current}mA")
    slider3_value_label.set_style_text_font(lv.font_montserrat_20, 0)
    slider3_value_label.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    slider3_value_label.set_pos(310, 235)  # Position to the right of slider
    
    selection_items.append(text_set_label3)
    item_positions.append((15, 230))  # Adjusted position: left 3px total, up 4px total
    item_sizes.append((440, 30))  # Long size
    
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
                elif current_selection == 1:
                    # Toggle OTG Enable switch
                    otg_enabled = not otg_enabled
                    if otg_enabled:
                        switch1.add_state(lv.STATE.CHECKED)
                    else:
                        switch1.remove_state(lv.STATE.CHECKED)
                    # Force screen refresh
                    lv.timer_handler()
                    set_otg_enable(otg_enabled)
                elif current_selection == 2:
                    # Toggle Charger Enable switch
                    charger_enabled = not charger_enabled
                    if charger_enabled:
                        switch2.add_state(lv.STATE.CHECKED)
                    else:
                        switch2.remove_state(lv.STATE.CHECKED)
                    # Force screen refresh
                    lv.timer_handler()
                    set_charger_enable(charger_enabled)
                elif current_selection == 3:
                    # Enter slider adjustment mode
                    adjustment_mode = 1
                    current_slider = slider3
                    
        elif adjustment_mode == 1:
            # Slider adjustment mode
            if key == "down":
                # Decrease slider value
                current_value = current_slider.get_value()
                new_value = max(current_value - 100, current_slider.get_min_value())  # Step by 100mA
                current_slider.set_value(new_value, 0)
                
                # Update label and hardware control
                slider3_value_label.set_text(f"{new_value}mA")
                set_charger_current(new_value)
                
            elif key == "up":
                # Increase slider value
                current_value = current_slider.get_value()
                new_value = min(current_value + 100, current_slider.get_max_value())  # Step by 100mA
                current_slider.set_value(new_value, 0)
                
                # Update label and hardware control
                slider3_value_label.set_text(f"{new_value}mA")
                set_charger_current(new_value)
                
            elif key == "enter":
                # Exit slider adjustment mode
                adjustment_mode = 0
                current_slider = None
    
    # Return to original page by recreating all elements
    return


