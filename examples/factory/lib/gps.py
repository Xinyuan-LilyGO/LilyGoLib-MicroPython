import lvgl as lv
import time
from machine import UART, Pin

recreate_main_page = None
encoder = None

# GPS-related configuration
GPS_TX = 4
GPS_RX = 12
GPS_PPS = 13

# GPS data storage
gps_data = {
    "lat": None,
    "lng": None,
    "sats": 0,
    "hdop": 0.0,
    "alt": 0.0,
    "speed": 0.0,
    "date": (0, 0, 0),
    "time": (0, 0, 0),
    "valid": False,
}

# Performance optimization related variables
last_gps_update = 0
last_gps_data_str = ""
GPS_UPDATE_INTERVAL = 500  # GPS data update interval (ms)
is_scrolling = False  # Scroll state flag

# Initialize UART
uart = UART(1, baudrate=9600, tx=Pin(GPS_RX), rx=Pin(GPS_TX))
pps = Pin(GPS_PPS, Pin.IN)
rx_chars = 0
last_fix_time = time.ticks_ms()
buffer = b""

def parse_latlng(v, d):
    """Parse latitude/longitude string"""
    if v == "":
        return None
    deg = int(v[:2])
    mins = float(v[2:])
    sign = -1 if d in ("S", "W") else 1
    return sign * (deg + mins / 60)

def parse_nmea(line):
    """Parse NMEA sentence"""
    global gps_data, last_fix_time
    
    parts = line.split(",")
    if line.startswith("$GPGGA"):
        if len(parts[1]) >= 6:
            hh = int(parts[1][0:2])
            mm = int(parts[1][2:4])
            ss = int(parts[1][4:6])
            gps_data["time"] = (hh, mm, ss)
        
        gps_data["lat"] = parse_latlng(parts[2], parts[3])
        gps_data["lng"] = parse_latlng(parts[4], parts[5])
        gps_data["sats"] = int(parts[7] or 0)
        gps_data["hdop"] = float(parts[8] or 0)
        gps_data["alt"] = float(parts[9] or 0)
        
        gps_data["valid"] = gps_data["sats"] >= 3
        if gps_data["valid"]:
            last_fix_time = time.ticks_ms()
    
    elif line.startswith("$GPRMC"):
        if parts[2] == "A":
            gps_data["valid"] = True
            last_fix_time = time.ticks_ms()
        
        if len(parts[9]) == 6:
            dd = int(parts[9][0:2])
            mm = int(parts[9][2:4])
            yy = int(parts[9][4:6]) + 2000
            gps_data["date"] = (yy, mm, dd)
        
        gps_data["lat"] = parse_latlng(parts[3], parts[4])
        gps_data["lng"] = parse_latlng(parts[5], parts[6])
        gps_data["speed"] = float(parts[7] or 0) * 1.852

def update_gps_display_labels(data_labels):
    """Update GPS data display labels"""
    global gps_data, rx_chars
    
    data_label1, data_label2, data_label3, data_label4, data_label5, data_label6, data_label7, data_label8, data_label9, data_label10 = data_labels
    
    # Update visible satellite count
    data_label4.set_text(str(gps_data["sats"]))
    
    # Update latitude
    lat = gps_data["lat"]
    if lat is not None:
        data_label5.set_text(f"{lat:.5f}")
    else:
        data_label5.set_text("0.00000")
    
    # Update longitude
    lng = gps_data["lng"]
    if lng is not None:
        data_label6.set_text(f"{lng:.5f}")
    else:
        data_label6.set_text("0.00000")
    
    # Update date/time
    year, month, day = gps_data["date"]
    hh, mm, ss = gps_data["time"]
    data_label7.set_text(f"{year:04d}/{month:02d}/{day:02d} {hh:02d}:{mm:02d}:{ss:02d}")
    
    # Update speed
    speed = gps_data["speed"]
    data_label8.set_text(f"{speed:.2f} km/h")
    
    # Update RX character count
    data_label9.set_text(str(rx_chars))
    
    # Update other status
    data_label2.set_text("Active" if gps_data["valid"] else "Inactive")
    data_label3.set_text("Enabled" if gps_data["valid"] else "Disabled")
    data_label10.set_text("Enabled" if gps_data["valid"] else "Disabled")

def update_gps_data():
    """Update GPS data"""
    global gps_data, rx_chars, last_fix_time, buffer, uart
    
    if uart.any():
        b = uart.read(1)
        
        if b:
            rx_chars += 1
            
            if b == b'\n':
                try:
                    line = buffer.decode("latin-1").strip()
                    
                    if line.startswith("$"):
                        parse_nmea(line)
                        
                except:
                    pass
                
                buffer = b""
            else:
                buffer += b

def set_references(recreate_func, encoder_obj=None):
    global recreate_main_page, encoder
    recreate_main_page = recreate_func
    if encoder_obj is not None:
        encoder = encoder_obj

def update_item_positions(selection_items, scroll_offset, symbol_labels=None, text_labels=None, data_labels=None):
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
    if data_labels:
        for i, data_label in enumerate(data_labels):
            monitor_index = i  # No offset needed for data labels
            x = 300  # Data label position
            y = 95 + (monitor_index * item_spacing)
            data_label.set_pos(x, y - scroll_offset)

def gps():
    # Declare all global variables that need to be modified
    global recreate_main_page, encoder
    global last_gps_update, last_gps_data_str, is_scrolling, gps_data, rx_chars, buffer, uart
    
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
    symbol_set_label1.set_text(lv.SYMBOL.GPS)
    symbol_set_label1.set_style_text_font(lv.font_montserrat_20, 0)
    symbol_set_label1.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    symbol_set_label1.set_pos(20, 95)
    
    text_set_label1 = lv.label(scr)
    text_set_label1.set_text("Model")
    text_set_label1.set_style_text_font(lv.font_montserrat_20, 0)
    text_set_label1.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    text_set_label1.set_pos(50, 95)  # Position next to symbol
    
    # GPS data label - Model
    data_label1 = lv.label(scr)
    data_label1.set_text("MIA-M10Q")
    data_label1.set_style_text_font(lv.font_montserrat_20, 0)
    data_label1.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    data_label1.set_pos(300, 95)  # Right side x:300 position
    
    selection_items.append(symbol_set_label1)  # Use symbol as reference for selection
    item_positions.append((15, 90))  # Adjusted position: left 3px total, up 4px total
    item_sizes.append((440, 30))  # Long size for other items
    
    # Item 2: 
    symbol_set_label2 = lv.label(scr)
    symbol_set_label2.set_text(lv.SYMBOL.GPS)
    symbol_set_label2.set_style_text_font(lv.font_montserrat_20, 0)
    symbol_set_label2.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    symbol_set_label2.set_pos(20, 135)
    
    text_set_label2 = lv.label(scr)
    text_set_label2.set_text("PPS Single")
    text_set_label2.set_style_text_font(lv.font_montserrat_20, 0)
    text_set_label2.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    text_set_label2.set_pos(50, 135)
    
    # GPS data label - PPS Single
    data_label2 = lv.label(scr)
    data_label2.set_text("Active")
    data_label2.set_style_text_font(lv.font_montserrat_20, 0)
    data_label2.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    data_label2.set_pos(300, 135)
    
    selection_items.append(symbol_set_label2)
    item_positions.append((15, 130))  # Adjusted position: left 3px total, up 4px total
    item_sizes.append((440, 30))  # Long size
    
    # Item 3: 
    symbol_set_label3 = lv.label(scr)
    symbol_set_label3.set_text(lv.SYMBOL.GPS)
    symbol_set_label3.set_style_text_font(lv.font_montserrat_20, 0)
    symbol_set_label3.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    symbol_set_label3.set_pos(20, 175)
    
    text_set_label3 = lv.label(scr)
    text_set_label3.set_text("USE Second")
    text_set_label3.set_style_text_font(lv.font_montserrat_20, 0)
    text_set_label3.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    text_set_label3.set_pos(50, 175)
    
    # GPS data label - USE Second
    data_label3 = lv.label(scr)
    data_label3.set_text("Enabled")
    data_label3.set_style_text_font(lv.font_montserrat_20, 0)
    data_label3.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    data_label3.set_pos(300, 175)
    
    selection_items.append(symbol_set_label3)
    item_positions.append((15, 170))  # Adjusted position: left 3px total, up 4px total
    item_sizes.append((440, 30))  # Long size
    
    # Item 4: 
    symbol_set_label4 = lv.label(scr)
    symbol_set_label4.set_text(lv.SYMBOL.GPS)
    symbol_set_label4.set_style_text_font(lv.font_montserrat_20, 0)
    symbol_set_label4.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    symbol_set_label4.set_pos(20, 215)
    
    text_set_label4 = lv.label(scr)
    text_set_label4.set_text("Visible satellite")
    text_set_label4.set_style_text_font(lv.font_montserrat_20, 0)
    text_set_label4.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    text_set_label4.set_pos(50, 215)
    
    # GPS data label - Visible satellite
    data_label4 = lv.label(scr)
    data_label4.set_text("0")
    data_label4.set_style_text_font(lv.font_montserrat_20, 0)
    data_label4.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    data_label4.set_pos(300, 215)
    
    selection_items.append(symbol_set_label4)
    item_positions.append((15, 215 - 4))  # Adjusted position: left 3px total, up 4px total
    item_sizes.append((440, 30))  # Long size
    
    # Item 5: System Voltage
    symbol_set_label5 = lv.label(scr)
    symbol_set_label5.set_text(lv.SYMBOL.GPS)
    symbol_set_label5.set_style_text_font(lv.font_montserrat_20, 0)
    symbol_set_label5.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    symbol_set_label5.set_pos(20, 255)
    
    text_set_label5 = lv.label(scr)
    text_set_label5.set_text("lat")
    text_set_label5.set_style_text_font(lv.font_montserrat_20, 0)
    text_set_label5.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    text_set_label5.set_pos(50, 255)
    
    # GPS data label - lat
    data_label5 = lv.label(scr)
    data_label5.set_text("0.00000")
    data_label5.set_style_text_font(lv.font_montserrat_20, 0)
    data_label5.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    data_label5.set_pos(300, 255)
    
    selection_items.append(symbol_set_label5)
    item_positions.append((15, 250))  # Adjusted position: left 3px total, up 4px total
    item_sizes.append((440, 30))  # Long size
    
    # Item 6: Battery Percent
    symbol_set_label6 = lv.label(scr)
    symbol_set_label6.set_text(lv.SYMBOL.GPS)
    symbol_set_label6.set_style_text_font(lv.font_montserrat_20, 0)
    symbol_set_label6.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    symbol_set_label6.set_pos(20, 295)
    
    text_set_label6 = lv.label(scr)
    text_set_label6.set_text("lng")
    text_set_label6.set_style_text_font(lv.font_montserrat_20, 0)
    text_set_label6.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    text_set_label6.set_pos(50, 295)
    
    # GPS data label - lng
    data_label6 = lv.label(scr)
    data_label6.set_text("0.00000")
    data_label6.set_style_text_font(lv.font_montserrat_20, 0)
    data_label6.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    data_label6.set_pos(300, 295)
    
    selection_items.append(symbol_set_label6)
    item_positions.append((15, 290))  # Adjusted position: left 3px total, up 4px total
    item_sizes.append((440, 30))  # Long size
    
    # Item 7: Temperature
    symbol_set_label7 = lv.label(scr)
    symbol_set_label7.set_text(lv.SYMBOL.GPS)
    symbol_set_label7.set_style_text_font(lv.font_montserrat_20, 0)
    symbol_set_label7.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    symbol_set_label7.set_pos(20, 335)
    
    text_set_label7 = lv.label(scr)
    text_set_label7.set_text("Datetime")
    text_set_label7.set_style_text_font(lv.font_montserrat_20, 0)
    text_set_label7.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    text_set_label7.set_pos(50, 335)
    
    # GPS data label - Datetime
    data_label7 = lv.label(scr)
    data_label7.set_text("2024/01/01 00:00:00")
    data_label7.set_style_text_font(lv.font_montserrat_20, 0)
    data_label7.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    data_label7.set_pos(300, 335)
    
    selection_items.append(symbol_set_label7)
    item_positions.append((15, 330))  # Adjusted position: left 3px total, up 4px total
    item_sizes.append((440, 30))  # Long size
    
    # Item 8: Instantaneous Current
    symbol_set_label8 = lv.label(scr)
    symbol_set_label8.set_text(lv.SYMBOL.GPS)
    symbol_set_label8.set_style_text_font(lv.font_montserrat_20, 0)
    symbol_set_label8.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    symbol_set_label8.set_pos(20, 375)
    
    text_set_label8 = lv.label(scr)
    text_set_label8.set_text("Speed")
    text_set_label8.set_style_text_font(lv.font_montserrat_20, 0)
    text_set_label8.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    text_set_label8.set_pos(50, 375)
    
    # GPS data label - Speed
    data_label8 = lv.label(scr)
    data_label8.set_text("0.00 km/h")
    data_label8.set_style_text_font(lv.font_montserrat_20, 0)
    data_label8.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    data_label8.set_pos(300, 375)
    
    selection_items.append(symbol_set_label8)
    item_positions.append((15, 370))  # Adjusted position: left 3px total, up 4px total
    item_sizes.append((440, 30))  # Long size
    
    # Item 9: Average Power
    symbol_set_label9 = lv.label(scr)
    symbol_set_label9.set_text(lv.SYMBOL.GPS)
    symbol_set_label9.set_style_text_font(lv.font_montserrat_20, 0)
    symbol_set_label9.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    symbol_set_label9.set_pos(20, 415)
    
    text_set_label9 = lv.label(scr)
    text_set_label9.set_text("RX Char")
    text_set_label9.set_style_text_font(lv.font_montserrat_20, 0)
    text_set_label9.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    text_set_label9.set_pos(50, 415)
    
    # GPS data label - RX Char
    data_label9 = lv.label(scr)
    data_label9.set_text("0")
    data_label9.set_style_text_font(lv.font_montserrat_20, 0)
    data_label9.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    data_label9.set_pos(300, 415)
    
    selection_items.append(symbol_set_label9)
    item_positions.append((15, 410))  # Adjusted position: left 3px total, up 4px total
    item_sizes.append((440, 30))  # Long size
    
    # Item 10: Time To Empty
    symbol_set_label10 = lv.label(scr)
    symbol_set_label10.set_text(lv.SYMBOL.GPS)
    symbol_set_label10.set_style_text_font(lv.font_montserrat_20, 0)
    symbol_set_label10.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    symbol_set_label10.set_pos(20, 455)
    
    text_set_label10 = lv.label(scr)
    text_set_label10.set_text("NMEA to Serial")
    text_set_label10.set_style_text_font(lv.font_montserrat_20, 0)
    text_set_label10.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    text_set_label10.set_pos(50, 455)
    
    # GPS data label - NMEA to Serial
    data_label10 = lv.label(scr)
    data_label10.set_text("Enabled")
    data_label10.set_style_text_font(lv.font_montserrat_20, 0)
    data_label10.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    data_label10.set_pos(300, 455)
    
    selection_items.append(symbol_set_label10)
    item_positions.append((15, 450))  # Adjusted position: left 3px total, up 4px total
    item_sizes.append((440, 30))  # Long size
    
    # Create data label list
    data_labels = [data_label1, data_label2, data_label3, data_label4, data_label5, 
                   data_label6, data_label7, data_label8, data_label9, data_label10]
    
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
        current_time = time.ticks_ms()
        
        # Only update GPS data when scrolling
        if is_scrolling or (current_time - last_gps_update > GPS_UPDATE_INTERVAL):
            update_gps_data()
            last_gps_update = current_time
        
        # Only update display labels when GPS data changes
        gps_data_str = f"{gps_data['sats']},{gps_data['lat']},{gps_data['lng']},{gps_data['time']},{gps_data['speed']},{rx_chars},{gps_data['valid']}"
        if gps_data_str != last_gps_data_str:
            update_gps_display_labels(data_labels)
            last_gps_data_str = gps_data_str
        
        key = encoder.update()
        
        if key == "down":
            # Set scroll state
            is_scrolling = True
            
            # Move selection down
            old_selection = current_selection
            current_selection = (current_selection + 1) % 11
            
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
            update_item_positions(selection_items, scroll_offset, [symbol_set_label1, symbol_set_label2, symbol_set_label3, symbol_set_label4, symbol_set_label5, symbol_set_label6, symbol_set_label7, symbol_set_label8, symbol_set_label9, symbol_set_label10], [text_set_label1, text_set_label2, text_set_label3, text_set_label4, text_set_label5, text_set_label6, text_set_label7, text_set_label8, text_set_label9, text_set_label10], data_labels)
            
        elif key == "up":
            # Set scroll state
            is_scrolling = True
            
            # Move selection up
            old_selection = current_selection
            current_selection = (current_selection - 1) % 11
            
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
            update_item_positions(selection_items, scroll_offset, [symbol_set_label1, symbol_set_label2, symbol_set_label3, symbol_set_label4, symbol_set_label5, symbol_set_label6, symbol_set_label7, symbol_set_label8, symbol_set_label9, symbol_set_label10], [text_set_label1, text_set_label2, text_set_label3, text_set_label4, text_set_label5, text_set_label6, text_set_label7, text_set_label8, text_set_label9, text_set_label10], data_labels)
            
        elif key == "enter":
            # Check if back button is selected
            if current_selection == 0:
                break  # Exit the loop to return to main page
            # For other selections, you can add specific handling here
            if current_selection == 1:
                pass
        
        # Reset state after scrolling ends
        is_scrolling = False
        
        # Brief sleep to reduce CPU usage
        time.sleep_ms(20)
            
                
    # Return to original page by recreating all elements
    recreate_main_page()



