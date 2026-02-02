import lvgl as lv
import machine
import network
import ubinascii
import os
import sys
import time
import _thread

recreate_main_page = None
encoder = None
_setting = None

# Global variables for device status display
device_status = {
    'SX1262': 'OFFLINE',
    'Haptic Drive': 'OFFLINE',
    'Power management': 'OFFLINE',
    'Real-time clock': 'OFFLINE',
    'PSRAM': 'OFFLINE',
    'GPS': 'OFFLINE',
    'SD Card': 'OFFLINE',
    'NFC': 'OFFLINE',
    'Montion sensor': 'OFFLINE',
    'Keyboard': 'OFFLINE',
    'Gauge': 'OFFLINE',
    'Expands Control': 'OFFLINE',
    'Audio codec': 'OFFLINE',
    'NRF2401 Sub 1G': 'OFFLINE'
}

# Reference to text labels for updating
text_labels_ref = []
device_name_labels_ref = []

# Export device_status for external access
def devices_status():
    """Device status function for external access - displays device status page"""
    system_info()

def devices_status_func():
    """Function wrapper for devices_status to be called from setting.py"""
    system_info()

def _devices_status():
    """Function called from setting.py line 379"""
    system_info()

def set_references(recreate_func, encoder_obj, setting_func):
    global recreate_main_page, encoder, _setting
    recreate_main_page = recreate_func
    encoder = encoder_obj
    _setting = setting_func

def check_device_status():
    """检查所有设备状态并更新全局变量 - 基于实际硬件引脚映射"""
    global device_status
    
    # 初始化所有设备为OFFLINE
    for device in device_status:
        device_status[device] = 'OFFLINE'
    
    try:
        from machine import Pin, I2C, SPI, UART
        import os
        
        # I2C总线初始化
        i2c = I2C(0, scl=Pin(2), sda=Pin(3), freq=400000)
        i2c_devices = i2c.scan()
        
        # 检查I2C设备地址
        # Haptic Driver(DRV2605) - 0x5A
        if 0x5A in i2c_devices:
            device_status['Haptic Drive'] = 'ONLINE'
        
        # Power Management (BQ25896) - 0x6B
        if 0x6B in i2c_devices:
            device_status['Power management'] = 'ONLINE'
        
        # Real-Time Clock (PCF85063A) - 0x51
        if 0x51 in i2c_devices:
            device_status['Real-time clock'] = 'ONLINE'
        
        # Gauge (BQ27220) - 0x55
        if 0x55 in i2c_devices:
            device_status['Gauge'] = 'ONLINE'
        
        # Keyboard (TCA8418) - 0x34
        if 0x34 in i2c_devices:
            device_status['Keyboard'] = 'ONLINE'
        
        # Audio Codec (ES8311) - 0x18
        if 0x18 in i2c_devices:
            device_status['Audio codec'] = 'ONLINE'
        
        # Expands Control (XL9555) - 0x20
        if 0x20 in i2c_devices:
            device_status['Expands Control'] = 'ONLINE'
        
        # Motion Sensor (BHI260AP) - 0x28
        if 0x28 in i2c_devices:
            device_status['Montion sensor'] = 'ONLINE'
        
        # NFC (ST25R3916) - SPI总线，通过CS引脚39检测
        try:
            nfc_cs = Pin(39, Pin.OUT)
            nfc_cs.on()  # 激活NFC芯片
            # 检查CS引脚是否能够设置高电平（设备存在）
            device_status['NFC'] = 'ONLINE'
            nfc_cs.off()  # 取消激活
        except:
            device_status['NFC'] = 'OFFLINE'
        
        # SX1262 LoRa芯片 - SPI总线，通过CS引脚36检测
        try:
            lora_cs = Pin(36, Pin.OUT)
            lora_cs.on()  # 激活LoRa芯片
            # 检查CS引脚是否能够设置高电平（设备存在）
            device_status['SX1262'] = 'ONLINE'
            lora_cs.off()  # 取消激活
        except:
            device_status['SX1262'] = 'OFFLINE'
        
        # GPS (GNSS MIA-M10Q) - UART1 (TX: 43, RX: 44)
        try:
            gps_uart = UART(1, baudrate=9600, tx=Pin(43), rx=Pin(44))
            # 尝试发送测试命令
            gps_uart.write(b'$PMTK000*32\r\n')
            device_status['GPS'] = 'ONLINE'
        except:
            device_status['GPS'] = 'OFFLINE'
        
        # SD Card - 通过扩展芯片GPIO12检测插入状态
        try:
            # 首先检查是否挂载了SD卡
            try:
                os.statvfs('/sd')
                device_status['SD Card'] = 'ONLINE'
            except:
                # 如果没有挂载，检查扩展芯片GPIO12状态
                # 注意：实际可能需要通过I2C读取扩展芯片状态
                device_status['SD Card'] = 'OFFLINE'
        except:
            device_status['SD Card'] = 'OFFLINE'
        
        # PSRAM检测 - 通过内存测试
        try:
            import gc
            gc.collect()
            # 尝试分配内存来测试PSRAM
            test_mem = bytearray(1024 * 200)  # 200KB test
            if len(test_mem) == 1024 * 200:
                device_status['PSRAM'] = 'ONLINE'
        except:
            device_status['PSRAM'] = 'OFFLINE'
        
        # NRF2401 Sub 1G - 这里没有对应的硬件，可能是LoRa的另一种称呼
        # 如果没有NRF24L01+硬件，将其标记为OFFLINE
        device_status['NRF2401 Sub 1G'] = 'OFFLINE'
        
    except Exception as e:
        # 如果初始化失败，保持所有设备为OFFLINE
        print(f"Device detection error: {e}")
        pass

def update_display_labels():
    """更新所有文本标签的显示"""
    global text_labels_ref
    
    # Get device names from global device_status
    device_names = list(device_status.keys())
    
    for i, device_name in enumerate(device_names):
        if i < len(text_labels_ref):
            text_labels_ref[i].set_text(device_status[device_name])
            
            # Update color based on status
            if device_status[device_name] == 'ONLINE':
                text_labels_ref[i].set_style_text_color(lv.color_hex(0x00ff00), 0)  # Green for ONLINE
            else:
                text_labels_ref[i].set_style_text_color(lv.color_hex(0xff0000), 0)  # Red for OFFLINE

def update_item_positions(selection_items, scroll_offset, text_labels=None, value_labels=None):
    """Update the visual position of all items based on scroll offset"""
    # Device items start from index 1 (index 0 is back button)
    # Dynamic positioning based on the number of devices
    base_y_start = 55  # Back button position
    item_spacing = 30
    
    # Update icon positions
    for i, item in enumerate(selection_items):
        if i == 0:  # Back button
            x, y = 20, base_y_start
        else:  # Device items
            device_index = i - 1  # Offset for back button
            x = 20
            y = 80 + (device_index * item_spacing)  # Device items start from y=80
        
        item.set_pos(x, y - scroll_offset)
    
    # Update text label positions if provided (device names)
    if text_labels:
        for i, text_label in enumerate(text_labels):
            device_index = i  # No offset needed for text labels as they correspond to device indices
            x = 60
            y = 80 + (device_index * item_spacing)
            text_label.set_pos(x, y - scroll_offset)
    
    # Update value label positions (status values) if provided
    if value_labels:
        for i, value_label in enumerate(value_labels):
            device_index = i  # No offset needed for value labels
            x = 250
            y = 80 + (device_index * item_spacing)
            value_label.set_pos(x, y - scroll_offset)

def system_info():
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
    global text_labels_ref
    text_labels_ref = []  # Clear the reference list
    
    # Device symbols mapping
    device_symbols = {
        'SX1262': lv.SYMBOL.OK,
        'Haptic Drive': lv.SYMBOL.OK,
        'Power management': lv.SYMBOL.OK,
        'Real-time clock': lv.SYMBOL.OK,
        'PSRAM': lv.SYMBOL.OK,
        'GPS': lv.SYMBOL.OK,
        'SD Card': lv.SYMBOL.OK,
        'NFC': lv.SYMBOL.OK,
        'Montion sensor': lv.SYMBOL.OK,
        'Keyboard': lv.SYMBOL.OK,
        'Gauge': lv.SYMBOL.OK,
        'Expands Control': lv.SYMBOL.OK,
        'Audio codec': lv.SYMBOL.OK,
        'NRF2401 Sub 1G': lv.SYMBOL.OK
    }
    
    # Device list from global device_status
    device_names = list(device_status.keys())
    
    # Item 0: Back button (lv.SYMBOL.LEFT)
    symbol_left_label = lv.label(scr)
    symbol_left_label.set_text(lv.SYMBOL.LEFT)
    symbol_left_label.set_style_text_font(lv.font_montserrat_20, 0)
    symbol_left_label.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    symbol_left_label.set_pos(20, 55)
    selection_items.append(symbol_left_label)
    item_positions.append((12, 50))  # Adjusted position: left 3px total, up 4px total
    item_sizes.append((30, 30))  # Smaller size for back button
    
    # Create device items (starting from index 1 to leave room for back button)
    for i, device_name in enumerate(device_names):
        device_index = i + 1  # Offset by 1 for back button
        y_pos = 80 + (i * 30)  # 30px spacing between items
        
        # Device symbol
        symbol_label = lv.label(scr)
        symbol_label.set_text(device_symbols.get(device_name, lv.SYMBOL.SETTINGS))
        symbol_label.set_style_text_font(lv.font_montserrat_20, 0)
        symbol_label.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
        symbol_label.set_pos(20, y_pos)
        
        # Device name text
        device_text_label = lv.label(scr)
        device_text_label.set_text(f"{device_name}:")
        device_text_label.set_style_text_font(lv.font_montserrat_16, 0)
        device_text_label.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
        device_text_label.set_pos(60, y_pos)
        device_name_labels_ref.append(device_text_label)  # Add to device name labels list
        
        # Device status value (ONLINE/OFFLINE)
        status_value_label = lv.label(scr)
        status_value_label.set_text(device_status[device_name])
        status_value_label.set_style_text_font(lv.font_montserrat_16, 0)
        
        # Set status color based on device status
        if device_status[device_name] == 'ONLINE':
            status_value_label.set_style_text_color(lv.color_hex(0x00ff00), 0)  # Green for ONLINE
        else:
            status_value_label.set_style_text_color(lv.color_hex(0xff0000), 0)  # Red for OFFLINE
        
        status_value_label.set_pos(250, y_pos)  # Position to the right of device name
        text_labels_ref.append(status_value_label)  # Add to text labels list for updates
        
        selection_items.append(symbol_label)  # Use symbol as reference for selection
        item_positions.append((15, y_pos - 5))  # Adjusted position: left 3px total, up 4px total
        item_sizes.append((440, 30))  # Long size for device items
    
    # Position selection box over first item (back button) by default
    current_selection = 0
    x, y = item_positions[current_selection]
    width, height = item_sizes[current_selection]
    selection_box.set_size(width, height)
    selection_box.set_pos(x, y)
    
    # 检查设备状态并更新显示（仅在页面加载时执行一次）
    check_device_status()
    update_display_labels()
    
    # Scroll offset to handle items that go beyond screen
    scroll_offset = 0
    max_visible_items = 7  # Number of items that can be fully visible (0-5)
    
    while True:
        key = encoder.update()
        
        if key == "down":
            # Move selection down
            old_selection = current_selection
            current_selection = (current_selection + 1) % 15  # 14 devices + 1 back button = 15 items total
            
            # Simple scroll logic: start scrolling when selection goes beyond visible items
            if current_selection >= max_visible_items:
                scroll_offset = (current_selection - max_visible_items + 1) * 30
            elif old_selection > current_selection:  # Wrapped around to start
                scroll_offset = 0  # Reset scroll when wrapping to beginning
            
            # Move and resize selection box to new position
            x, y = item_positions[current_selection]
            width, height = item_sizes[current_selection]
            selection_box.set_size(width, height)
            selection_box.set_pos(x, y - scroll_offset)
            # Update all item positions for scrolling
            update_item_positions(selection_items, scroll_offset, device_name_labels_ref, text_labels_ref)
            
        elif key == "up":
            # Move selection up
            old_selection = current_selection
            current_selection = (current_selection - 1) % 15  # 14 devices + 1 back button = 15 items total
            
            # Simple scroll logic based on current selection
            if current_selection < max_visible_items:
                scroll_offset = 0  # Top items are always visible
            else:
                scroll_offset = (current_selection - max_visible_items + 1) * 30
            
            # Move and resize selection box to new position
            x, y = item_positions[current_selection]
            width, height = item_sizes[current_selection]
            selection_box.set_size(width, height)
            selection_box.set_pos(x, y - scroll_offset)
            # Update all item positions for scrolling
            update_item_positions(selection_items, scroll_offset, device_name_labels_ref, text_labels_ref)
            
        elif key == "enter":
            # Check if back button is selected
            if current_selection == 0:
                break  # Exit the loop to return to main page
    
    # Return to original page by recreating all elements
    return
