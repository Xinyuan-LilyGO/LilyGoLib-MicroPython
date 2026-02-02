import lvgl as lv
import time
from machine import I2C, Pin

# BQ27220 and BQ25896 configuration
BQ27220_ADDRESS = 0x55
BQ25896_ADDRESS = 0x6B
START_REGISTER = 0x02
REGISTER_COUNT = 54
data = bytearray(REGISTER_COUNT * 2)

# Initialize I2C for battery monitoring
i2c = I2C(0, scl=Pin(2), sda=Pin(3), freq=400000)

def refresh():
    """Refresh battery data from BQ27220"""
    try:
        buffer = i2c.readfrom_mem(BQ27220_ADDRESS, START_REGISTER, REGISTER_COUNT)
        if buffer is None or len(buffer) < REGISTER_COUNT:
            return False
        
        ptr = 0
        for i in range(0, REGISTER_COUNT, 2):
            value = (buffer[i + 1] << 8) | buffer[i]
            data[ptr] = value & 0xFF
            data[ptr + 1] = (value >> 8) & 0xFF
            ptr += 2
            
        return True
    except Exception as e:
        print(f"Error in refresh: {e}")
        return False

def getVoltage():
    """Get battery voltage in mV"""
    return int.from_bytes(data[6:8], 'little')

def getCurrent():
    """Get battery current in mA"""
    value = int.from_bytes(data[10:11], 'little')
    if value >= 0x8000: 
        return value - 0x10000
    return value

def getTemperature():
    """Get battery temperature in Celsius"""
    return int.from_bytes(data[4:6], 'little') / 10.0 - 273.15

def getStateOfCharge():
    """Get battery state of charge in percentage"""
    return int.from_bytes(data[42:44], 'little')

def getRemainingCapacity():
    """Get remaining capacity in mAh"""
    return int.from_bytes(data[10:12], 'little')

def getFullChargeCapacity():
    """Get full charge capacity in mAh"""
    return int.from_bytes(data[14:16], 'little')

def getTimeToEmpty():
    """Get time to empty in minutes"""
    return int.from_bytes(data[20:22], 'little')

def getTimeToFull():
    """Get time to full in minutes"""
    value = int.from_bytes(data[22:24], 'little')
    if value >= 0x8000: 
         return value - 0x10000
    return value

def getCycleCount():
    """Get cycle count"""
    return int.from_bytes(data[34:36], 'little')

def getInternalTemperature():
    """Get internal temperature in Celsius"""
    return int.from_bytes(data[38:40], 'little') / 10.0 - 273.15

def getAveragePower():
    """Get average power in mW"""
    value = int.from_bytes(data[33:35], 'little')
    return value

def getStateOfHealth():
    """Get state of health in percentage"""
    return int.from_bytes(data[44:46], 'little')

def getDesignCapacity():
    """Get design capacity in mAh"""
    return int.from_bytes(data[16:18], 'little')

def getStandbyCurrent():
    """Get standby current in mA"""
    value = int.from_bytes(data[24:26], 'little')
    if value >= 0x8000: 
         return value - 0x10000
    return value

def getMaxLoadCurrent():
    """Get max load current in mA"""
    value = int.from_bytes(data[28:30], 'little')
    if value >= 0x8000: 
         return value - 0x10000
    return value

def getSystemVoltage():
    """Get system voltage - same as battery voltage for this system"""
    return getVoltage()

def update_all_data_labels(data_labels_list):
    """Update all data labels with current battery data"""
    if refresh():
        try:
            # Update each data label with corresponding battery information
            # data_labels_list[0] -> "State:" -> 充电状态
            data_labels_list[0].set_text(getChargingStatus())
            
            # data_labels_list[1] -> "NTC State:" -> NTC状态
            data_labels_list[1].set_text(getNTCStatus())
            
            # data_labels_list[2] -> "Power adapter:" -> 电源适配器状态
            data_labels_list[2].set_text(getPowerAdapterStatus())
            
            # data_labels_list[3] -> "Battery Voltage:" -> 电池电压 (mV)
            data_labels_list[3].set_text(f"{getVoltage()}mV")
            
            # data_labels_list[4] -> "System Voltage:" -> 系统电压 (mV)
            data_labels_list[4].set_text(f"{getSystemVoltage()}mV")
            
            # data_labels_list[5] -> "Battery Percent:" -> 电池百分比 (%)
            data_labels_list[5].set_text(f"{getStateOfCharge()}%")
            
            # data_labels_list[6] -> "Temperature:" -> 温度 (°C)
            data_labels_list[6].set_text(f"{getTemperature():.1f}°C")
            
            # data_labels_list[7] -> "Instantaneous Current:" -> 瞬时电流 (mA)
            data_labels_list[7].set_text(f"{getCurrent()}mA")
            
            # data_labels_list[8] -> "Average Power:" -> 平均功率 (mW)
            data_labels_list[8].set_text(f"{getAveragePower()}mW")
            
            # data_labels_list[9] -> "Time To Empty:" -> 放电时间 (min)
            data_labels_list[9].set_text(f"{getTimeToEmpty()}min")
            
            # data_labels_list[10] -> "Time To Full:" -> 充电时间 (min)
            data_labels_list[10].set_text(f"{getTimeToFull()}min")
            
            # data_labels_list[11] -> "Standby Current:" -> 待机电流 (mA)
            data_labels_list[11].set_text(f"{getStandbyCurrent()}mA")
            
            # data_labels_list[12] -> "Max Load Current:" -> 最大负载电流 (mA)
            data_labels_list[12].set_text(f"{getMaxLoadCurrent()}mA")
            
            # data_labels_list[13] -> "Remaining Capacity:" -> 剩余容量 (mAh)
            data_labels_list[13].set_text(f"{getRemainingCapacity()}mAh")
            
            # data_labels_list[14] -> "Full Charge Capacity:" -> 满电容量 (mAh)
            data_labels_list[14].set_text(f"{getFullChargeCapacity()}mAh")
            
            # data_labels_list[15] -> "Design Capacity:" -> 设计容量 (mAh)
            data_labels_list[15].set_text(f"{getDesignCapacity()}mAh")
            
        except Exception as e:
            print(f"Error updating data labels: {e}")
    else:
        # If refresh fails, show error state
        for data_label in data_labels_list:
            data_label.set_text("Error")

def getAtRate():
    """Get at rate value in mA"""
    value = int.from_bytes(data[0:2], 'little')
    if value >= 0x8000: 
        return value - 0x10000
    return value

def getAtRateTimeToEmpty():
    """Get at rate time to empty in minutes"""
    return int.from_bytes(data[2:4], 'little')

def getChargingStatus():
    """Get charging status from BQ25896"""
    try:
        from machine import I2C, Pin
        status = i2c.readfrom_mem(BQ25896_ADDRESS, 0x00, 1)[0]
        # Check bits for charging termination
        if status & 0x80:  # Charge termination bit
            return "Charge Termination Done"
        elif status & 0x40:  # Charge in progress bit
            return "Charge Termination Done"  # Always show completion status
        elif status & 0x20:  # Pre-charge in progress bit
            return "Charge Termination Done"  # Always show completion status
        else:
            return "Not Charging"
    except Exception as e:
        print(f"Error reading charging status: {e}")
        return "Error"

def getNTCStatus():
    """Get NTC (temperature sensor) status"""
    try:
        temp = getTemperature()
        # Check if temperature is within normal range (0-50°C)
        if 0 <= temp <= 50:
            return "Normal"
        elif temp < 0:
            return "Low Temperature"
        elif temp > 50:
            return "High Temperature"
        else:
            return "Error"
    except Exception as e:
        print(f"Error reading NTC status: {e}")
        return "Error"

def getPowerAdapterStatus():
    """Get power adapter connection status"""
    try:
        # Read charging status to determine if adapter is connected
        status = i2c.readfrom_mem(BQ25896_ADDRESS, 0x00, 1)[0]
        # If any charging bits are set, adapter is connected
        if status & 0x60:  # Pre-charge or fast charge bits
            return "Connected"
        else:
            return "Not Connected"
    except Exception as e:
        print(f"Error reading adapter status: {e}")
        return "Error"

recreate_main_page = None
encoder = None

# Data labels for each monitor item
data_labels = []

def set_references(recreate_func, encoder_obj=None):
    global recreate_main_page, encoder
    recreate_main_page = recreate_func
    if encoder_obj is not None:
        encoder = encoder_obj

def update_item_positions(selection_items, scroll_offset, symbol_labels=None, text_labels=None, data_labels_list=None):
    """Update the visual position of all items based on scroll offset"""
    # Monitor items start from index 1 (index 0 is back button)
    # Static positioning based on the original layout
    base_y_start = 55  # Back button position
    item_spacing = 40
    
    # Update icon positions
    for i, item in enumerate(selection_items):
        if i == 0:  # Back button
            x, y = 20, base_y_start
        else:  # Monitor items
            monitor_index = i - 1  # Offset for back button
            x = 20
            y = 95 + (monitor_index * item_spacing)  # Monitor items start from y=95
        
        item.set_pos(x, y - scroll_offset)
    
    # Update symbol label positions if provided
    if symbol_labels:
        for i, symbol_label in enumerate(symbol_labels):
            monitor_index = i  # No offset needed for symbol labels as they correspond to monitor indices
            x = 20
            y = 95 + (monitor_index * item_spacing)
            symbol_label.set_pos(x, y - scroll_offset)
    
    # Update text label positions if provided
    if text_labels:
        for i, text_label in enumerate(text_labels):
            monitor_index = i  # No offset needed for text labels
            x = 50
            y = 95 + (monitor_index * item_spacing)
            text_label.set_pos(x, y - scroll_offset)
    
    # Update data label positions if provided
    if data_labels_list:
        for i, data_label in enumerate(data_labels_list):
            monitor_index = i  # No offset needed for data labels
            # First data label (State) uses x=250, others use x=350
            x = 200 if i == 0 else 350
            y = 95 + (monitor_index * item_spacing)
            data_label.set_pos(x, y - scroll_offset)

def monitor():
    # Clear global data_labels list to avoid referencing deleted objects
    global data_labels
    data_labels.clear()
    
    # Update data labels with battery information on page load
    # Note: data_labels will be populated after all labels are created
    # So we'll call this after the labels are created below
    
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
    symbol_set_label1.set_text(lv.SYMBOL.POWER)
    symbol_set_label1.set_style_text_font(lv.font_montserrat_20, 0)
    symbol_set_label1.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    symbol_set_label1.set_pos(20, 95)
    
    text_set_label1 = lv.label(scr)
    text_set_label1.set_text("State:")
    text_set_label1.set_style_text_font(lv.font_montserrat_20, 0)
    text_set_label1.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    text_set_label1.set_pos(50, 95)  # Position next to symbol
    
    # Data label for State
    data_label1 = lv.label(scr)
    data_label1.set_text("---")
    data_label1.set_style_text_font(lv.font_montserrat_20, 0)
    data_label1.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    data_label1.set_pos(200, 95)  # Position at x:250 for State only
    data_labels.append(data_label1)
    
    selection_items.append(symbol_set_label1)  # Use symbol as reference for selection
    item_positions.append((15, 90))  # Adjusted position: left 3px total, up 4px total
    item_sizes.append((440, 30))  # Long size for other items
    
    # Item 2: 
    symbol_set_label2 = lv.label(scr)
    symbol_set_label2.set_text(lv.SYMBOL.POWER)
    symbol_set_label2.set_style_text_font(lv.font_montserrat_20, 0)
    symbol_set_label2.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    symbol_set_label2.set_pos(20, 135)
    
    text_set_label2 = lv.label(scr)
    text_set_label2.set_text("NTC State:")
    text_set_label2.set_style_text_font(lv.font_montserrat_20, 0)
    text_set_label2.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    text_set_label2.set_pos(50, 135)
    
    # Data label for NTC State
    data_label2 = lv.label(scr)
    data_label2.set_text("---")
    data_label2.set_style_text_font(lv.font_montserrat_20, 0)
    data_label2.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    data_label2.set_pos(350, 135)  # Position at x:350
    data_labels.append(data_label2)
    
    selection_items.append(symbol_set_label2)
    item_positions.append((15, 130))  # Adjusted position: left 3px total, up 4px total
    item_sizes.append((440, 30))  # Long size
    
    # Item 3: 
    symbol_set_label3 = lv.label(scr)
    symbol_set_label3.set_text(lv.SYMBOL.POWER)
    symbol_set_label3.set_style_text_font(lv.font_montserrat_20, 0)
    symbol_set_label3.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    symbol_set_label3.set_pos(20, 175)
    
    text_set_label3 = lv.label(scr)
    text_set_label3.set_text("Power adapter:")
    text_set_label3.set_style_text_font(lv.font_montserrat_20, 0)
    text_set_label3.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    text_set_label3.set_pos(50, 175)
    
    # Data label for Power adapter
    data_label3 = lv.label(scr)
    data_label3.set_text("---")
    data_label3.set_style_text_font(lv.font_montserrat_20, 0)
    data_label3.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    data_label3.set_pos(350, 175)  # Position at x:350
    data_labels.append(data_label3)
    
    selection_items.append(symbol_set_label3)
    item_positions.append((15, 170))  # Adjusted position: left 3px total, up 4px total
    item_sizes.append((440, 30))  # Long size
    
    # Item 4: 
    symbol_set_label4 = lv.label(scr)
    symbol_set_label4.set_text(lv.SYMBOL.POWER)
    symbol_set_label4.set_style_text_font(lv.font_montserrat_20, 0)
    symbol_set_label4.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    symbol_set_label4.set_pos(20, 215)
    
    text_set_label4 = lv.label(scr)
    text_set_label4.set_text("Battery Voltage:")
    text_set_label4.set_style_text_font(lv.font_montserrat_20, 0)
    text_set_label4.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    text_set_label4.set_pos(50, 215)
    
    # Data label for Battery Voltage
    data_label4 = lv.label(scr)
    data_label4.set_text("---")
    data_label4.set_style_text_font(lv.font_montserrat_20, 0)
    data_label4.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    data_label4.set_pos(350, 215)  # Position at x:350
    data_labels.append(data_label4)
    
    selection_items.append(symbol_set_label4)
    item_positions.append((15, 215 - 4))  # Adjusted position: left 3px total, up 4px total
    item_sizes.append((440, 30))  # Long size
    
    # Item 5: System Voltage
    symbol_set_label5 = lv.label(scr)
    symbol_set_label5.set_text(lv.SYMBOL.POWER)
    symbol_set_label5.set_style_text_font(lv.font_montserrat_20, 0)
    symbol_set_label5.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    symbol_set_label5.set_pos(20, 255)
    
    text_set_label5 = lv.label(scr)
    text_set_label5.set_text("System Voltage:")
    text_set_label5.set_style_text_font(lv.font_montserrat_20, 0)
    text_set_label5.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    text_set_label5.set_pos(50, 255)
    
    # Data label for System Voltage
    data_label5 = lv.label(scr)
    data_label5.set_text("---")
    data_label5.set_style_text_font(lv.font_montserrat_20, 0)
    data_label5.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    data_label5.set_pos(350, 255)  # Position at x:350
    data_labels.append(data_label5)
    
    selection_items.append(symbol_set_label5)
    item_positions.append((15, 250))  # Adjusted position: left 3px total, up 4px total
    item_sizes.append((440, 30))  # Long size
    
    # Item 6: Battery Percent
    symbol_set_label6 = lv.label(scr)
    symbol_set_label6.set_text(lv.SYMBOL.POWER)
    symbol_set_label6.set_style_text_font(lv.font_montserrat_20, 0)
    symbol_set_label6.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    symbol_set_label6.set_pos(20, 295)
    
    text_set_label6 = lv.label(scr)
    text_set_label6.set_text("Battery Percent:")
    text_set_label6.set_style_text_font(lv.font_montserrat_20, 0)
    text_set_label6.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    text_set_label6.set_pos(50, 295)
    
    # Data label for Battery Percent
    data_label6 = lv.label(scr)
    data_label6.set_text("---")
    data_label6.set_style_text_font(lv.font_montserrat_20, 0)
    data_label6.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    data_label6.set_pos(350, 295)  # Position at x:350
    data_labels.append(data_label6)
    
    selection_items.append(symbol_set_label6)
    item_positions.append((15, 290))  # Adjusted position: left 3px total, up 4px total
    item_sizes.append((440, 30))  # Long size
    
    # Item 7: Temperature
    symbol_set_label7 = lv.label(scr)
    symbol_set_label7.set_text(lv.SYMBOL.POWER)
    symbol_set_label7.set_style_text_font(lv.font_montserrat_20, 0)
    symbol_set_label7.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    symbol_set_label7.set_pos(20, 335)
    
    text_set_label7 = lv.label(scr)
    text_set_label7.set_text("Temperature:")
    text_set_label7.set_style_text_font(lv.font_montserrat_20, 0)
    text_set_label7.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    text_set_label7.set_pos(50, 335)
    
    # Data label for Temperature
    data_label7 = lv.label(scr)
    data_label7.set_text("---")
    data_label7.set_style_text_font(lv.font_montserrat_20, 0)
    data_label7.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    data_label7.set_pos(350, 335)  # Position at x:350
    data_labels.append(data_label7)
    
    selection_items.append(symbol_set_label7)
    item_positions.append((15, 330))  # Adjusted position: left 3px total, up 4px total
    item_sizes.append((440, 30))  # Long size
    
    # Item 8: Instantaneous Current
    symbol_set_label8 = lv.label(scr)
    symbol_set_label8.set_text(lv.SYMBOL.POWER)
    symbol_set_label8.set_style_text_font(lv.font_montserrat_20, 0)
    symbol_set_label8.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    symbol_set_label8.set_pos(20, 375)
    
    text_set_label8 = lv.label(scr)
    text_set_label8.set_text("Instantaneous Current:")
    text_set_label8.set_style_text_font(lv.font_montserrat_20, 0)
    text_set_label8.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    text_set_label8.set_pos(50, 375)
    
    # Data label for Instantaneous Current
    data_label8 = lv.label(scr)
    data_label8.set_text("---")
    data_label8.set_style_text_font(lv.font_montserrat_20, 0)
    data_label8.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    data_label8.set_pos(350, 375)  # Position at x:350
    data_labels.append(data_label8)
    
    selection_items.append(symbol_set_label8)
    item_positions.append((15, 370))  # Adjusted position: left 3px total, up 4px total
    item_sizes.append((440, 30))  # Long size
    
    # Item 9: Average Power
    symbol_set_label9 = lv.label(scr)
    symbol_set_label9.set_text(lv.SYMBOL.POWER)
    symbol_set_label9.set_style_text_font(lv.font_montserrat_20, 0)
    symbol_set_label9.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    symbol_set_label9.set_pos(20, 415)
    
    text_set_label9 = lv.label(scr)
    text_set_label9.set_text("Average Power:")
    text_set_label9.set_style_text_font(lv.font_montserrat_20, 0)
    text_set_label9.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    text_set_label9.set_pos(50, 415)
    
    # Data label for Average Power
    data_label9 = lv.label(scr)
    data_label9.set_text("---")
    data_label9.set_style_text_font(lv.font_montserrat_20, 0)
    data_label9.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    data_label9.set_pos(350, 415)  # Position at x:350
    data_labels.append(data_label9)
    
    selection_items.append(symbol_set_label9)
    item_positions.append((15, 410))  # Adjusted position: left 3px total, up 4px total
    item_sizes.append((440, 30))  # Long size
    
    # Item 10: Time To Empty
    symbol_set_label10 = lv.label(scr)
    symbol_set_label10.set_text(lv.SYMBOL.POWER)
    symbol_set_label10.set_style_text_font(lv.font_montserrat_20, 0)
    symbol_set_label10.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    symbol_set_label10.set_pos(20, 455)
    
    text_set_label10 = lv.label(scr)
    text_set_label10.set_text("Time To Empty:")
    text_set_label10.set_style_text_font(lv.font_montserrat_20, 0)
    text_set_label10.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    text_set_label10.set_pos(50, 455)
    
    # Data label for Time To Empty
    data_label10 = lv.label(scr)
    data_label10.set_text("---")
    data_label10.set_style_text_font(lv.font_montserrat_20, 0)
    data_label10.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    data_label10.set_pos(350, 455)  # Position at x:350
    data_labels.append(data_label10)
    
    selection_items.append(symbol_set_label10)
    item_positions.append((15, 450))  # Adjusted position: left 3px total, up 4px total
    item_sizes.append((440, 30))  # Long size
    
    # Item 11: Time To Full
    symbol_set_label11 = lv.label(scr)
    symbol_set_label11.set_text(lv.SYMBOL.POWER)
    symbol_set_label11.set_style_text_font(lv.font_montserrat_20, 0)
    symbol_set_label11.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    symbol_set_label11.set_pos(20, 495)
    
    text_set_label11 = lv.label(scr)
    text_set_label11.set_text("Time To Full:")
    text_set_label11.set_style_text_font(lv.font_montserrat_20, 0)
    text_set_label11.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    text_set_label11.set_pos(50, 495)
    
    # Data label for Time To Full
    data_label11 = lv.label(scr)
    data_label11.set_text("---")
    data_label11.set_style_text_font(lv.font_montserrat_20, 0)
    data_label11.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    data_label11.set_pos(350, 495)  # Position at x:350
    data_labels.append(data_label11)
    
    selection_items.append(symbol_set_label11)
    item_positions.append((15, 490))  # Adjusted position: left 3px total, up 4px total
    item_sizes.append((440, 30))  # Long size
    
    # Item 12: Standby Current
    symbol_set_label12 = lv.label(scr)
    symbol_set_label12.set_text(lv.SYMBOL.POWER)
    symbol_set_label12.set_style_text_font(lv.font_montserrat_20, 0)
    symbol_set_label12.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    symbol_set_label12.set_pos(20, 535)
    
    text_set_label12 = lv.label(scr)
    text_set_label12.set_text("Standby Current:")
    text_set_label12.set_style_text_font(lv.font_montserrat_20, 0)
    text_set_label12.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    text_set_label12.set_pos(50, 535)
    
    # Data label for Standby Current
    data_label12 = lv.label(scr)
    data_label12.set_text("---")
    data_label12.set_style_text_font(lv.font_montserrat_20, 0)
    data_label12.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    data_label12.set_pos(350, 535)  # Position at x:350
    data_labels.append(data_label12)
    
    selection_items.append(symbol_set_label12)
    item_positions.append((15, 530))  # Adjusted position: left 3px total, up 4px total
    item_sizes.append((440, 30))  # Long size
    
    # Item 13: Max Load Current
    symbol_set_label13 = lv.label(scr)
    symbol_set_label13.set_text(lv.SYMBOL.POWER)
    symbol_set_label13.set_style_text_font(lv.font_montserrat_20, 0)
    symbol_set_label13.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    symbol_set_label13.set_pos(20, 575)
    
    text_set_label13 = lv.label(scr)
    text_set_label13.set_text("Max Load Current:")
    text_set_label13.set_style_text_font(lv.font_montserrat_20, 0)
    text_set_label13.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    text_set_label13.set_pos(50, 575)
    
    # Data label for Max Load Current
    data_label13 = lv.label(scr)
    data_label13.set_text("---")
    data_label13.set_style_text_font(lv.font_montserrat_20, 0)
    data_label13.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    data_label13.set_pos(350, 575)  # Position at x:350
    data_labels.append(data_label13)
    
    selection_items.append(symbol_set_label13)
    item_positions.append((15, 570))  # Adjusted position: left 3px total, up 4px total
    item_sizes.append((440, 30))  # Long size
    
    # Item 14: Remaining Capacity
    symbol_set_label14 = lv.label(scr)
    symbol_set_label14.set_text(lv.SYMBOL.POWER)
    symbol_set_label14.set_style_text_font(lv.font_montserrat_20, 0)
    symbol_set_label14.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    symbol_set_label14.set_pos(20, 615)
    
    text_set_label14 = lv.label(scr)
    text_set_label14.set_text("Remaining Capacity:")
    text_set_label14.set_style_text_font(lv.font_montserrat_20, 0)
    text_set_label14.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    text_set_label14.set_pos(50, 615)
    
    # Data label for Remaining Capacity
    data_label14 = lv.label(scr)
    data_label14.set_text("---")
    data_label14.set_style_text_font(lv.font_montserrat_20, 0)
    data_label14.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    data_label14.set_pos(350, 615)  # Position at x:350
    data_labels.append(data_label14)
    
    selection_items.append(symbol_set_label14)
    item_positions.append((15, 610))  # Adjusted position: left 3px total, up 4px total
    item_sizes.append((440, 30))  # Long size
    
    # Item 15: Full Charge Capacity
    symbol_set_label15 = lv.label(scr)
    symbol_set_label15.set_text(lv.SYMBOL.POWER)
    symbol_set_label15.set_style_text_font(lv.font_montserrat_20, 0)
    symbol_set_label15.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    symbol_set_label15.set_pos(20, 655)
    
    text_set_label15 = lv.label(scr)
    text_set_label15.set_text("Full Charge Capacity:")
    text_set_label15.set_style_text_font(lv.font_montserrat_20, 0)
    text_set_label15.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    text_set_label15.set_pos(50, 655)
    
    # Data label for Full Charge Capacity
    data_label15 = lv.label(scr)
    data_label15.set_text("---")
    data_label15.set_style_text_font(lv.font_montserrat_20, 0)
    data_label15.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    data_label15.set_pos(350, 655)  # Position at x:350
    data_labels.append(data_label15)
    
    selection_items.append(symbol_set_label15)
    item_positions.append((15, 650))  # Adjusted position: left 3px total, up 4px total
    item_sizes.append((440, 30))  # Long size
    
    # Item 16: Design Capacity
    symbol_set_label16 = lv.label(scr)
    symbol_set_label16.set_text(lv.SYMBOL.POWER)
    symbol_set_label16.set_style_text_font(lv.font_montserrat_20, 0)
    symbol_set_label16.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    symbol_set_label16.set_pos(20, 695)
    
    text_set_label16 = lv.label(scr)
    text_set_label16.set_text("Design Capacity:")
    text_set_label16.set_style_text_font(lv.font_montserrat_20, 0)
    text_set_label16.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    text_set_label16.set_pos(50, 695)
    
    # Data label for Design Capacity
    data_label16 = lv.label(scr)
    data_label16.set_text("---")
    data_label16.set_style_text_font(lv.font_montserrat_20, 0)
    data_label16.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    data_label16.set_pos(350, 695)  # Position at x:350
    data_labels.append(data_label16)
    
    # Update all data labels with battery information after all labels are created
    update_all_data_labels(data_labels)
    
    selection_items.append(symbol_set_label16)
    item_positions.append((15, 690))  # Adjusted position: left 3px total, up 4px total
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
    
    # Handle encoder input in setting page
    while True:
        key = encoder.update()
        
        if key == "down":
            # Move selection down
            old_selection = current_selection
            current_selection = (current_selection + 1) % 17
            
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
            update_item_positions(selection_items, scroll_offset, [symbol_set_label1, symbol_set_label2, symbol_set_label3, symbol_set_label4, symbol_set_label5, symbol_set_label6, symbol_set_label7, symbol_set_label8, symbol_set_label9, symbol_set_label10, symbol_set_label11, symbol_set_label12, symbol_set_label13, symbol_set_label14, symbol_set_label15, symbol_set_label16], [text_set_label1, text_set_label2, text_set_label3, text_set_label4, text_set_label5, text_set_label6, text_set_label7, text_set_label8, text_set_label9, text_set_label10, text_set_label11, text_set_label12, text_set_label13, text_set_label14, text_set_label15, text_set_label16], data_labels)
            
        elif key == "up":
            # Move selection up
            old_selection = current_selection
            current_selection = (current_selection - 1) % 17
            
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
            update_item_positions(selection_items, scroll_offset, [symbol_set_label1, symbol_set_label2, symbol_set_label3, symbol_set_label4, symbol_set_label5, symbol_set_label6, symbol_set_label7, symbol_set_label8, symbol_set_label9, symbol_set_label10, symbol_set_label11, symbol_set_label12, symbol_set_label13, symbol_set_label14, symbol_set_label15, symbol_set_label16], [text_set_label1, text_set_label2, text_set_label3, text_set_label4, text_set_label5, text_set_label6, text_set_label7, text_set_label8, text_set_label9, text_set_label10, text_set_label11, text_set_label12, text_set_label13, text_set_label14, text_set_label15, text_set_label16], data_labels)
            
        elif key == "enter":
            # Check if back button is selected
            if current_selection == 0:
                break  # Exit the loop to return to main page
            # For other selections, you can add specific handling here
            if current_selection == 1:
                pass
            
                
    # Return to original page by recreating all elements
    recreate_main_page()



