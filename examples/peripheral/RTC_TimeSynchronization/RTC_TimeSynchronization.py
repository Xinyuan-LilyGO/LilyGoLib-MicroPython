'''
 * @file      RTC_TimeSynchronization.py
 * @license   MIT
 * @copyright Copyright (c) 2025  Shenzhen Xin Yuan Electronic Technology Co., Ltd
 * @date      2025-10-29
'''
from machine import SPI, Pin, I2C, RTC
import sys
import lcd_bus
import st7796
import lvgl as lv
from micropython import const
import vibration
import _thread
import time
import network
import ntptime

ssid = "LilyGo-AABB"
password = "xinyuandianzi"

i2c = I2C(0, scl=Pin(2), sda=Pin(3), freq=400000)
vb = vibration.vibrationMotor(i2c)
def vibrate_motor():
    vb.vibrate(1, 200)

lv.init()
try:
    spi_bus = SPI.Bus(host = 1, mosi=34, miso=33, sck=35)
    display_bus = lcd_bus.SPIBus(
        spi_bus=spi_bus,
        dc=37,
        cs=38,
        freq=80000000
    )

    display = st7796.ST7796(
        data_bus=display_bus,
        display_width=320,
        display_height=480,
        reset_state=st7796.STATE_LOW,
        color_space=lv.COLOR_FORMAT.RGB565,
        color_byte_order=st7796.BYTE_ORDER_RGB,
        rgb565_byte_swap=True
    )

    display.set_power(True)
    display.init()
    display.set_rotation(lv.DISPLAY_ROTATION._90)
except:
    pass

_thread.start_new_thread(vibrate_motor, ())
backlight_pin = Pin(42, Pin.OUT)
backlight_pin.value(1)

scrn = lv.screen_active()
scrn.set_style_bg_color(lv.color_hex(0x000000), 0)  

cont = lv.obj(scrn)
cont.set_flex_flow(lv.FLEX_FLOW.COLUMN)
cont.set_scroll_dir(lv.DIR.VER)
cont.set_size(lv.pct(100), lv.pct(100))
cont.set_style_pad_top(60,0)
cont.center()

label1 = lv.label(cont)
label1.set_width(lv.pct(90))
label2 = lv.label(cont)
label2.set_width(lv.pct(90))
label3 = lv.label(cont)
label3.set_width(lv.pct(90))

last_millis = 0
wifi_connected = False
time_synced = False

weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
months = ["January", "February", "March", "April", "May", "June", 
          "July", "August", "September", "October", "November", "December"]

def format_time(now):
    # "%A, %B %d %Y %H:%M:%S"
    weekday = weekdays[now[6]]
    month = months[now[1] - 1]
    return "{}, {} {:02d} {:04d} {:02d}:{:02d}:{:02d}".format(
        weekday, month, now[2], now[0], now[3], now[4], now[5])

def sync_ntp_time():
    global time_synced
    max_retries = 3
    for attempt in range(max_retries):
        try:
            ntptime.host = "pool.ntp.org"
            ntptime.settime()
            time_synced = True
            print("Time synchronized via NTP (attempt {})".format(attempt + 1))
            return True
        except Exception as e:
            print("NTP sync attempt {} failed: {}".format(attempt + 1, e))
            if attempt < max_retries - 1:
                time.sleep(2)
    return False

def get_system_time():
    if time_synced:
        utc_time = time.time()
        beijing_time = utc_time + 8 * 3600
        return time.localtime(beijing_time)
    else:
        return None

def connect_wifi():
    global wifi_connected
    
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    label1.set_text("Connecting to {}".format(ssid))
    print("Connecting to {} ".format(ssid), end="")
    
    wlan.connect(ssid, password)
    
    while not wlan.isconnected():
        time.sleep_ms(5)
        lv.task_handler()
    
    wifi_connected = True
    print(" CONNECTED")
    label1.set_text("{} Connected".format(ssid))
    
    if sync_ntp_time():
        print("NTP time synchronization successful")
    else:
        print("NTP time synchronization failed, using local time")
        time_synced = True

connect_wifi()

def update_time_display():
    global last_millis
    current_millis = time.ticks_ms()
    
    if time.ticks_diff(current_millis, last_millis) > 1000:
        last_millis = current_millis

        hw_time = time.localtime()
        hw_time_str = format_time(hw_time)
        
        print("Hardware clock :{}".format(hw_time_str))
        label2.set_text("HW Clock:{}".format(hw_time_str))
        
        if time_synced:
            system_time = get_system_time()
            if system_time:
                sys_time_str = format_time(system_time)
                print("System   clock :{}".format(sys_time_str))
                print()
                label3.set_text("SYS Clock:{}".format(sys_time_str))
            else:
                label3.set_text("No time available (yet)")
        else:
            label3.set_text("No time available (yet)")

import task_handler
task_handler.TaskHandler(33)

while True:
    update_time_display()
    lv.task_handler()
    time.sleep_ms(5)