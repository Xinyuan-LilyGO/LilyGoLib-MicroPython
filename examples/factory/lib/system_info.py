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

# Global variables for real-time data display
system_data = {
    'mac': 'N/A',
    'wifi_ssid': 'N/A',
    'rtc_time': 'N/A',
    'ip_address': 'N/A',
    'rssi': 'N/A',
    'battery_voltage': 'N/A',
    'sd_card_size': 'N/A',
    'lvgl_version': 'N/A',
    'micropython_version': 'N/A',
    'build_time': 'N/A',
    'hash': 'N/A',
    'chip_id': 'N/A'
}

# Reference to text labels for updating
text_labels_ref = []

def set_references(recreate_func, encoder_obj, setting_func):
    global recreate_main_page, encoder, _setting
    recreate_main_page = recreate_func
    encoder = encoder_obj
    _setting = setting_func

def get_system_info():
    """获取所有系统信息并更新全局变量"""
    global system_data
    
    # 1. 获取MAC地址
    try:
        mac = ubinascii.hexlify(machine.unique_id()).decode()
        formatted_mac = ':'.join([mac[i:i+2] for i in range(0, len(mac), 2)])
        system_data['mac'] = formatted_mac
    except:
        system_data['mac'] = 'N/A'
    
    # 2. 获取WiFi信息
    try:
        sta_if = network.WLAN(network.STA_IF)
        if sta_if.isconnected():
            system_data['wifi_ssid'] = sta_if.config('ssid')
            system_data['ip_address'] = sta_if.ifconfig()[0]
            system_data['rssi'] = str(sta_if.status('rssi')) + ' dBm'
        else:
            system_data['wifi_ssid'] = 'N/A'
            system_data['ip_address'] = 'N/A'
            system_data['rssi'] = 'N/A'
    except:
        system_data['wifi_ssid'] = 'N/A'
        system_data['ip_address'] = 'N/A'
        system_data['rssi'] = 'N/A'
    
    # 3. 获取RTC时间
    try:
        # 尝试使用machine.RTC来获取时间 (这可能是硬件RTC的接口)
        try:
            # 检查machine模块是否有RTC类
            from machine import RTC
            rtc = RTC()
            # 读取时间并格式化
            datetime = rtc.datetime()
            # datetime格式: (year, month, day, weekday, hours, minutes, seconds, subseconds)
            formatted_time = "{:04d}/{:02d}/{:02d} {:02d}:{:02d}:{:02d}".format(
                datetime[0], datetime[1], datetime[2],
                datetime[4], datetime[5], datetime[6]
            )
            system_data['rtc_time'] = formatted_time
        except Exception as e:
            # 如果machine.RTC不可用，回退到系统时间
            print("RTC module not available, using system time:", e)
            current_time = time.localtime()
            formatted_time = "{:04d}/{:02d}/{:02d} {:02d}:{:02d}:{:02d}".format(
                current_time[0], current_time[1], current_time[2],
                current_time[3], current_time[4], current_time[5]
            )
            system_data['rtc_time'] = formatted_time
    except Exception as e:
        print("Error getting RTC time:", e)
        system_data['rtc_time'] = 'N/A'
    
    # 4. 获取电池电压
    try:
        # 尝试使用电池电量计BQ27220获取电池电压
        try:
            # 初始化I2C通信
            from machine import Pin, I2C
            i2c = I2C(0, scl=Pin(2), sda=Pin(3), freq=400000)
            
            # BQ27220的I2C地址
            BQ27220_ADDR = 0x55
            
            # 检查BQ27220是否可用
            devices = i2c.scan()
            if BQ27220_ADDR in devices:
                # 读取电池电压寄存器
                # BQ27220的电压寄存器地址为0x09 (高字节和低字节)
                i2c.writeto(BQ27220_ADDR, bytearray([0x09]))
                data = i2c.readfrom(BQ27220_ADDR, 2)
                
                # 解析电压数据 (单位: mV)
                voltage_raw = (data[0] << 8) | data[1]
                voltage = voltage_raw * 0.9765625  # BQ27220的分辨率
                
                system_data['battery_voltage'] = "{:.0f} mV".format(voltage)
            else:
                # 如果BQ27220不可用，尝试使用ADC读取GPIO9 (可用引脚)
                adc = machine.ADC(machine.Pin(9))  # 使用GPIO9作为电池电压检测引脚
                adc.atten(machine.ADC.ATTN_11DB)  # 设置衰减为满量程
                reading = adc.read() * (3.3 / 4095) * 1000  # 转换为mV
                system_data['battery_voltage'] = "{:.0f} mV".format(reading)
        except Exception as e:
            print("Battery voltage detection error:", e)
            # 如果所有方法都失败，使用默认ADC引脚GPIO1作为备用
            try:
                adc = machine.ADC(machine.Pin(1))  # 使用GPIO1作为备用ADC引脚
                adc.atten(machine.ADC.ATTN_11DB)  # 设置衰减为满量程
                reading = adc.read() * (3.3 / 4095) * 1000  # 转换为mV
                system_data['battery_voltage'] = "{:.0f} mV".format(reading)
            except:
                system_data['battery_voltage'] = 'N/A'
    except Exception as e:
        print("Battery voltage error:", e)
        system_data['battery_voltage'] = 'N/A'
    
    # 5. 获取SD卡大小
    try:
        # 尝试获取SD卡信息 (如果SD卡已挂载)
        if hasattr(os, 'statvfs'):  # 检查是否有statvfs函数
            try:
                # 先检查SD卡是否已挂载
                os.statvfs('/sd')
                stat = os.statvfs('/sd')
                total_size = stat[0] * stat[2] / (1024 * 1024)  # MB
                free_size = stat[0] * stat[3] / (1024 * 1024)  # MB
                system_data['sd_card_size'] = "{:.1f} MB / {:.1f} MB".format(free_size, total_size)
            except:
                # 如果SD卡未挂载或出现其他错误，尝试其他方法
                try:
                    # 尝试获取SD卡信息的其他方法
                    system_data['sd_card_size'] = 'Unknown'
                except:
                    system_data['sd_card_size'] = 'N/A'
        else:
            system_data['sd_card_size'] = 'N/A'
    except:
        system_data['sd_card_size'] = 'N/A'
    
    # 6. 获取LVGL版本
    try:
        # 获取LVGL版本信息
        lvgl_version = "8.3.0"  # 示例版本，实际项目中可能需要从LVGL库获取
        system_data['lvgl_version'] = lvgl_version
    except:
        system_data['lvgl_version'] = 'N/A'
    
    # 7. 获取MicroPython版本
    try:
        micropython_version = sys.version.split()[0]
        system_data['micropython_version'] = micropython_version
    except:
        system_data['micropython_version'] = 'N/A'
    
    # 8. 获取构建时间 (示例)
    try:
        # 这里使用当前时间作为构建时间的示例
        build_time = time.localtime()
        formatted_build_time = "{:04d}{:02d}{:02d}{:02d}{:02d}".format(
            build_time[0], build_time[1], build_time[2],
            build_time[3], build_time[4]
        )
        system_data['build_time'] = formatted_build_time
    except:
        system_data['build_time'] = 'N/A'
    
    # 9. 获取Hash (示例)
    try:
        # 这里使用MAC地址的一部分作为示例hash
        mac = machine.unique_id()
        hash_value = ubinascii.hexlify(mac).decode()[:8]
        system_data['hash'] = hash_value
    except:
        system_data['hash'] = 'N/A'
    
    # 10. 获取Chip ID
    try:
        chip_id = ubinascii.hexlify(machine.unique_id()).decode()
        system_data['chip_id'] = chip_id.upper()
    except:
        system_data['chip_id'] = 'N/A'

def update_display_labels():
    """更新所有文本标签的显示"""
    global text_labels_ref
    
    # 更新各个标签的文本
    label_keys = ['mac', 'wifi_ssid', 'rtc_time', 'ip_address', 'rssi', 
                  'battery_voltage', 'sd_card_size', 'lvgl_version', 
                  'micropython_version', 'build_time', 'hash', 'chip_id']
    
    for i, key in enumerate(label_keys):
        if i < len(text_labels_ref):
            text_labels_ref[i].set_text(system_data[key])

def update_item_positions(selection_items, scroll_offset, text_labels=None, value_labels=None):
    """Update the visual position of all items based on scroll offset"""
    base_positions = [(20, 55), (20, 80), (20, 110), (20, 140), (20, 170), (20, 200), (20, 230), (20, 260), (20, 290), (20, 320), (20, 350), (20, 380), (20, 410)]
    text_base_positions = [(60, 80), (60, 110), (60, 140), (60, 170), (60, 200), (60, 230), (60, 260), (60, 290), (60, 320), (60, 350), (60, 380), (60, 410)]
    value_base_positions = [(200, 80), (200, 110), (200, 140), (200, 170), (200, 200), (200, 230), (200, 260), (200, 290), (200, 320), (200, 350), (200, 380), (200, 410)]
    
    # Update icon positions
    for i, item in enumerate(selection_items):
        if i < len(base_positions):
            x, y = base_positions[i]
            item.set_pos(x, y - scroll_offset)
    
    # Update text label positions if provided
    if text_labels:
        for i, text_label in enumerate(text_labels):
            if i < len(text_base_positions):
                x, y = text_base_positions[i]
                text_label.set_pos(x, y - scroll_offset)
    
    # Update value label positions (the new text boxes) if provided
    if value_labels:
        for i, value_label in enumerate(value_labels):
            if i < len(value_base_positions):
                x, y = value_base_positions[i]
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
    
    # Reference to original text labels for scrolling
    original_text_labels_ref = []
    
    # Item 0: Back button (lv.SYMBOL.LEFT)
    symbol_left_label = lv.label(scr)
    symbol_left_label.set_text(lv.SYMBOL.LEFT)
    symbol_left_label.set_style_text_font(lv.font_montserrat_20, 0)
    symbol_left_label.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    symbol_left_label.set_pos(20, 55)
    selection_items.append(symbol_left_label)
    item_positions.append((12, 50))  # Adjusted position: left 3px total, up 4px total
    item_sizes.append((30, 30))  # Smaller size for back button
    
    # Item 1: MAC
    symbol_set_label1 = lv.label(scr)
    symbol_set_label1.set_text(lv.SYMBOL.SETTINGS)
    symbol_set_label1.set_style_text_font(lv.font_montserrat_20, 0)
    symbol_set_label1.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    symbol_set_label1.set_pos(20, 80)
    
    # Original text label for MAC (preserved)
    mac_text_label = lv.label(scr)
    mac_text_label.set_text("MAC:")
    mac_text_label.set_style_text_font(lv.font_montserrat_16, 0)
    mac_text_label.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    mac_text_label.set_pos(60, 80)
    
    # Add to original text labels for scrolling
    original_text_labels_ref.append(mac_text_label)
    
    # New text box for MAC value on the right
    mac_value_label = lv.label(scr)
    mac_value_label.set_text(system_data['mac'])
    mac_value_label.set_style_text_font(lv.font_montserrat_16, 0)
    mac_value_label.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    mac_value_label.set_pos(200, 80)  # Position to the right of original text
    text_labels_ref.append(mac_value_label)  # Add to text labels list for updates
    
    selection_items.append(symbol_set_label1)  # Use symbol as reference for selection
    item_positions.append((15, 75))  # Adjusted position: left 3px total, up 4px total
    item_sizes.append((440, 30))  # Long size for other items
    
    # Item 2: WIFI
    symbol_set_label2 = lv.label(scr)
    symbol_set_label2.set_text(lv.SYMBOL.WIFI)
    symbol_set_label2.set_style_text_font(lv.font_montserrat_20, 0)
    symbol_set_label2.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    symbol_set_label2.set_pos(20, 110)
    
    # Original text label for WIFI SSID (preserved)
    wifi_text_label = lv.label(scr)
    wifi_text_label.set_text("WIFI:")
    wifi_text_label.set_style_text_font(lv.font_montserrat_16, 0)
    wifi_text_label.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    wifi_text_label.set_pos(60, 110)
    
    # Add to original text labels for scrolling
    original_text_labels_ref.append(wifi_text_label)
    
    # New text box for WIFI SSID value on the right
    wifi_value_label = lv.label(scr)
    wifi_value_label.set_text(system_data['wifi_ssid'])
    wifi_value_label.set_style_text_font(lv.font_montserrat_16, 0)
    wifi_value_label.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    wifi_value_label.set_pos(200, 110)  # Position to the right of original text
    text_labels_ref.append(wifi_value_label)  # Add to text labels list for updates
    
    selection_items.append(symbol_set_label2)
    item_positions.append((15, 105))  # Adjusted position: left 3px total, up 4px total
    item_sizes.append((440, 30))  # Long size
    
    # Item 3: RTC DATETIME
    symbol_set_label3 = lv.label(scr)
    symbol_set_label3.set_text(lv.SYMBOL.BELL)
    symbol_set_label3.set_style_text_font(lv.font_montserrat_20, 0)
    symbol_set_label3.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    symbol_set_label3.set_pos(20, 140)
    
    # Original text label for RTC Datetime (preserved)
    rtc_text_label = lv.label(scr)
    rtc_text_label.set_text("RTC:")
    rtc_text_label.set_style_text_font(lv.font_montserrat_16, 0)
    rtc_text_label.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    rtc_text_label.set_pos(60, 140)
    
    # Add to original text labels for scrolling
    original_text_labels_ref.append(rtc_text_label)
    
    # New text box for RTC Datetime value on the right
    rtc_value_label = lv.label(scr)
    rtc_value_label.set_text(system_data['rtc_time'])
    rtc_value_label.set_style_text_font(lv.font_montserrat_16, 0)
    rtc_value_label.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    rtc_value_label.set_pos(200, 140)  # Position to the right of original text
    text_labels_ref.append(rtc_value_label)  # Add to text labels list for updates
    
    selection_items.append(symbol_set_label3)
    item_positions.append((15, 135))  # Adjusted position: left 3px total, up 4px total
    item_sizes.append((440, 30))  # Long size
    
    # Item 4: IP
    symbol_set_label4 = lv.label(scr)
    symbol_set_label4.set_text(lv.SYMBOL.WIFI)
    symbol_set_label4.set_style_text_font(lv.font_montserrat_20, 0)
    symbol_set_label4.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    symbol_set_label4.set_pos(20, 170)
    
    # Original text label for IP (preserved)
    ip_text_label = lv.label(scr)
    ip_text_label.set_text("IP:")
    ip_text_label.set_style_text_font(lv.font_montserrat_16, 0)
    ip_text_label.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    ip_text_label.set_pos(60, 170)
    
    # Add to original text labels for scrolling
    original_text_labels_ref.append(ip_text_label)
    
    # New text box for IP value on the right
    ip_value_label = lv.label(scr)
    ip_value_label.set_text(system_data['ip_address'])
    ip_value_label.set_style_text_font(lv.font_montserrat_16, 0)
    ip_value_label.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    ip_value_label.set_pos(200, 170)  # Position to the right of original text
    text_labels_ref.append(ip_value_label)  # Add to text labels list for updates
    
    selection_items.append(symbol_set_label4)
    item_positions.append((15, 165))
    item_sizes.append((440, 30))
    
    # Item 5: RSSI
    symbol_set_label5 = lv.label(scr)
    symbol_set_label5.set_text(lv.SYMBOL.WIFI)
    symbol_set_label5.set_style_text_font(lv.font_montserrat_20, 0)
    symbol_set_label5.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    symbol_set_label5.set_pos(20, 200)
    
    # Original text label for RSSI (preserved)
    rssi_text_label = lv.label(scr)
    rssi_text_label.set_text("RSSI:")
    rssi_text_label.set_style_text_font(lv.font_montserrat_16, 0)
    rssi_text_label.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    rssi_text_label.set_pos(60, 200)
    
    # Add to original text labels for scrolling
    original_text_labels_ref.append(rssi_text_label)
    
    # New text box for RSSI value on the right
    rssi_value_label = lv.label(scr)
    rssi_value_label.set_text(system_data['rssi'])
    rssi_value_label.set_style_text_font(lv.font_montserrat_16, 0)
    rssi_value_label.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    rssi_value_label.set_pos(200, 200)  # Position to the right of original text
    text_labels_ref.append(rssi_value_label)  # Add to text labels list for updates
    
    selection_items.append(symbol_set_label5)
    item_positions.append((15, 195))
    item_sizes.append((440, 30))
    
    # Item 6: Voltage
    symbol_set_label6 = lv.label(scr)
    symbol_set_label6.set_text(lv.SYMBOL.BATTERY_FULL)
    symbol_set_label6.set_style_text_font(lv.font_montserrat_20, 0)
    symbol_set_label6.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    symbol_set_label6.set_pos(20, 230)
    
    # Original text label for Voltage (preserved)
    voltage_text_label = lv.label(scr)
    voltage_text_label.set_text("Voltage:")
    voltage_text_label.set_style_text_font(lv.font_montserrat_16, 0)
    voltage_text_label.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    voltage_text_label.set_pos(60, 230)
    
    # Add to original text labels for scrolling
    original_text_labels_ref.append(voltage_text_label)
    
    # New text box for Voltage value on the right
    voltage_value_label = lv.label(scr)
    voltage_value_label.set_text(system_data['battery_voltage'])
    voltage_value_label.set_style_text_font(lv.font_montserrat_16, 0)
    voltage_value_label.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    voltage_value_label.set_pos(200, 230)  # Position to the right of original text
    text_labels_ref.append(voltage_value_label)  # Add to text labels list for updates
    
    selection_items.append(symbol_set_label6)
    item_positions.append((15, 225))
    item_sizes.append((440, 30))
    
    # Item 7: SD Card
    symbol_set_label7 = lv.label(scr)
    symbol_set_label7.set_text(lv.SYMBOL.SD_CARD)
    symbol_set_label7.set_style_text_font(lv.font_montserrat_20, 0)
    symbol_set_label7.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    symbol_set_label7.set_pos(20, 260)
    
    # Original text label for SD Card (preserved)
    sdcard_text_label = lv.label(scr)
    sdcard_text_label.set_text("SD Card:")
    sdcard_text_label.set_style_text_font(lv.font_montserrat_16, 0)
    sdcard_text_label.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    sdcard_text_label.set_pos(60, 260)
    
    # Add to original text labels for scrolling
    original_text_labels_ref.append(sdcard_text_label)
    
    # New text box for SD Card value on the right
    sdcard_value_label = lv.label(scr)
    sdcard_value_label.set_text(system_data['sd_card_size'])
    sdcard_value_label.set_style_text_font(lv.font_montserrat_16, 0)
    sdcard_value_label.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    sdcard_value_label.set_pos(200, 260)  # Position to the right of original text
    text_labels_ref.append(sdcard_value_label)  # Add to text labels list for updates
    
    selection_items.append(symbol_set_label7)
    item_positions.append((15, 255))
    item_sizes.append((440, 30))
    
    # Item 8: LVGL Version
    symbol_set_label8 = lv.label(scr)
    symbol_set_label8.set_text(lv.SYMBOL.EYE_OPEN)
    symbol_set_label8.set_style_text_font(lv.font_montserrat_20, 0)
    symbol_set_label8.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    symbol_set_label8.set_pos(20, 290)
    
    # Original text label for LVGL Version (preserved)
    lvgl_text_label = lv.label(scr)
    lvgl_text_label.set_text("LVGL:")
    lvgl_text_label.set_style_text_font(lv.font_montserrat_16, 0)
    lvgl_text_label.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    lvgl_text_label.set_pos(60, 290)
    
    # Add to original text labels for scrolling
    original_text_labels_ref.append(lvgl_text_label)
    
    # New text box for LVGL Version value on the right
    lvgl_value_label = lv.label(scr)
    lvgl_value_label.set_text(system_data['lvgl_version'])
    lvgl_value_label.set_style_text_font(lv.font_montserrat_16, 0)
    lvgl_value_label.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    lvgl_value_label.set_pos(200, 290)  # Position to the right of original text
    text_labels_ref.append(lvgl_value_label)  # Add to text labels list for updates
    
    selection_items.append(symbol_set_label8)
    item_positions.append((15, 285))
    item_sizes.append((440, 30))
    
    # Item 9: micropython Core
    symbol_set_label9 = lv.label(scr)
    symbol_set_label9.set_text(lv.SYMBOL.EYE_OPEN)
    symbol_set_label9.set_style_text_font(lv.font_montserrat_20, 0)
    symbol_set_label9.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    symbol_set_label9.set_pos(20, 320)
    
    # Original text label for Micropython Core (preserved)
    micropython_text_label = lv.label(scr)
    micropython_text_label.set_text("MicroPython:")
    micropython_text_label.set_style_text_font(lv.font_montserrat_16, 0)
    micropython_text_label.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    micropython_text_label.set_pos(60, 320)
    
    # Add to original text labels for scrolling
    original_text_labels_ref.append(micropython_text_label)
    
    # New text box for MicroPython Core value on the right
    micropython_value_label = lv.label(scr)
    micropython_value_label.set_text(system_data['micropython_version'])
    micropython_value_label.set_style_text_font(lv.font_montserrat_16, 0)
    micropython_value_label.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    micropython_value_label.set_pos(200, 320)  # Position to the right of original text
    text_labels_ref.append(micropython_value_label)  # Add to text labels list for updates
    
    selection_items.append(symbol_set_label9)
    item_positions.append((15, 315))
    item_sizes.append((440, 30))
    
    # Item 10: Build Time
    symbol_set_label10 = lv.label(scr)
    symbol_set_label10.set_text(lv.SYMBOL.EYE_OPEN)
    symbol_set_label10.set_style_text_font(lv.font_montserrat_20, 0)
    symbol_set_label10.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    symbol_set_label10.set_pos(20, 350)
    
    # Original text label for Build Time (preserved)
    buildtime_text_label = lv.label(scr)
    buildtime_text_label.set_text("Build:")
    buildtime_text_label.set_style_text_font(lv.font_montserrat_16, 0)
    buildtime_text_label.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    buildtime_text_label.set_pos(60, 350)
    
    # Add to original text labels for scrolling
    original_text_labels_ref.append(buildtime_text_label)
    
    # New text box for Build Time value on the right
    buildtime_value_label = lv.label(scr)
    buildtime_value_label.set_text(system_data['build_time'])
    buildtime_value_label.set_style_text_font(lv.font_montserrat_16, 0)
    buildtime_value_label.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    buildtime_value_label.set_pos(200, 350)  # Position to the right of original text
    text_labels_ref.append(buildtime_value_label)  # Add to text labels list for updates
    
    selection_items.append(symbol_set_label10)
    item_positions.append((15, 345))
    item_sizes.append((440, 30))
    
    # Item 11: Hash
    symbol_set_label11 = lv.label(scr)
    symbol_set_label11.set_text(lv.SYMBOL.EYE_OPEN)
    symbol_set_label11.set_style_text_font(lv.font_montserrat_20, 0)
    symbol_set_label11.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    symbol_set_label11.set_pos(20, 380)
    
    # Original text label for Hash (preserved)
    hash_text_label = lv.label(scr)
    hash_text_label.set_text("Hash:")
    hash_text_label.set_style_text_font(lv.font_montserrat_16, 0)
    hash_text_label.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    hash_text_label.set_pos(60, 380)
    
    # Add to original text labels for scrolling
    original_text_labels_ref.append(hash_text_label)
    
    # New text box for Hash value on the right
    hash_value_label = lv.label(scr)
    hash_value_label.set_text(system_data['hash'])
    hash_value_label.set_style_text_font(lv.font_montserrat_16, 0)
    hash_value_label.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    hash_value_label.set_pos(200, 380)  # Position to the right of original text
    text_labels_ref.append(hash_value_label)  # Add to text labels list for updates
    
    selection_items.append(symbol_set_label11)
    item_positions.append((15, 375))
    item_sizes.append((440, 30))
    
    # Item 12: Chip ID
    symbol_set_label12 = lv.label(scr)
    symbol_set_label12.set_text(lv.SYMBOL.EYE_OPEN)
    symbol_set_label12.set_style_text_font(lv.font_montserrat_20, 0)
    symbol_set_label12.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    symbol_set_label12.set_pos(20, 410)
    
    # Original text label for Chip ID (preserved)
    chipid_text_label = lv.label(scr)
    chipid_text_label.set_text("Chip ID:")
    chipid_text_label.set_style_text_font(lv.font_montserrat_16, 0)
    chipid_text_label.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    chipid_text_label.set_pos(60, 410)
    
    # Add to original text labels for scrolling
    original_text_labels_ref.append(chipid_text_label)
    
    # New text box for Chip ID value on the right
    chipid_value_label = lv.label(scr)
    chipid_value_label.set_text(system_data['chip_id'])
    chipid_value_label.set_style_text_font(lv.font_montserrat_16, 0)
    chipid_value_label.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    chipid_value_label.set_pos(200, 410)  # Position to the right of original text
    text_labels_ref.append(chipid_value_label)  # Add to text labels list for updates
    
    selection_items.append(symbol_set_label12)
    item_positions.append((15, 405))
    item_sizes.append((440, 30))
    
    # Position selection box over first item (back button) by default
    current_selection = 0
    x, y = item_positions[current_selection]
    width, height = item_sizes[current_selection]
    selection_box.set_size(width, height)
    selection_box.set_pos(x, y)
    
    # 获取并更新系统信息（仅在页面加载时执行一次）
    get_system_info()
    update_display_labels()
    
    # 添加更新RTC时间的函数
    def update_rtc_time():
        try:
            # 尝试使用machine.RTC来获取时间
            try:
                # 检查machine模块是否有RTC类
                from machine import RTC
                rtc = RTC()
                # 读取时间并格式化
                datetime = rtc.datetime()
                # datetime格式: (year, month, day, weekday, hours, minutes, seconds, subseconds)
                formatted_time = "{:04d}/{:02d}/{:02d} {:02d}:{:02d}:{:02d}".format(
                    datetime[0], datetime[1], datetime[2],
                    datetime[4], datetime[5], datetime[6]
                )
                system_data['rtc_time'] = formatted_time
            except Exception as e:
                # 如果machine.RTC不可用，回退到系统时间
                print("RTC module not available, using system time:", e)
                current_time = time.localtime()
                formatted_time = "{:04d}/{:02d}/{:02d} {:02d}:{:02d}:{:02d}".format(
                    current_time[0], current_time[1], current_time[2],
                    current_time[3], current_time[4], current_time[5]
                )
                system_data['rtc_time'] = formatted_time
            
            # 更新RTC时间标签
            rtc_value_label.set_text(system_data['rtc_time'])
        except Exception as e:
            print("Error updating RTC time:", e)
    
    # Scroll offset to handle items that go beyond screen
    scroll_offset = 0
    max_visible_items = 7  # Number of items that can be fully visible (0-5)
    
    # 计时器用于更新RTC时间
    last_update_time = time.time()
    update_interval = 1  # 每秒更新一次
    
    while True:
        key = encoder.update()
        
        # 检查是否需要更新RTC时间
        current_time = time.time()
        if current_time - last_update_time >= update_interval:
            update_rtc_time()
            last_update_time = current_time
        
        if key == "down":
            # Move selection down
            old_selection = current_selection
            current_selection = (current_selection + 1) % 13  # Now 13 items total
            
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
            update_item_positions(selection_items, scroll_offset, original_text_labels_ref, text_labels_ref)
            
        elif key == "up":
            # Move selection up
            old_selection = current_selection
            current_selection = (current_selection - 1) % 13  # Now 13 items total
            
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
            update_item_positions(selection_items, scroll_offset, original_text_labels_ref, text_labels_ref)
            
        elif key == "enter":
            # Check if back button is selected
            if current_selection == 0:
                break  # Exit the loop to return to main page
    
    # Return to original page by recreating all elements
    return

