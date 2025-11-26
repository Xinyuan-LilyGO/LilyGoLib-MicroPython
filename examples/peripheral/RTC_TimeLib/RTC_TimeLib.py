'''
 * @file      RTC_TimeLib.py
 * @license   MIT
 * @copyright Copyright (c) 2025  Shenzhen Xinyuan Electronic Technology Co., Ltd
 * @date      2025-10-29
'''
from machine import SPI, Pin, I2C
import sys
import lcd_bus
import st7796
import lvgl as lv
from micropython import const
import vibration
import _thread
import time

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
cont.set_style_pad_top(60,0)
cont.set_size(lv.pct(100), lv.pct(100))
cont.center()

label1 = lv.label(cont)
label1.set_width(lv.pct(90))
label2 = lv.label(cont)
label2.set_width(lv.pct(90))
label3 = lv.label(cont)
label3.set_width(lv.pct(90))

last_millis = 0

weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
months = ["January", "February", "March", "April", "May", "June", 
          "July", "August", "September", "October", "November", "December"]
months_short = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
                "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

# Format the output using the strftime function
# For more formats, please refer to :
# https://man7.org/linux/man-pages/man3/strftime.3.html      
def format_time_1(now):
    # "%A, %B %d %Y %H:%M:%S"
    weekday = weekdays[now[6]]
    month = months[now[1] - 1]
    return "{}, {} {:02d} {:04d} {:02d}:{:02d}:{:02d}".format(
        weekday, month, now[2], now[0], now[3], now[4], now[5])

def format_time_2(now):
    # "%b %d %Y %H:%M:%S"
    month = months_short[now[1] - 1]
    return "{} {:02d} {:04d} {:02d}:{:02d}:{:02d}".format(
        month, now[2], now[0], now[3], now[4], now[5])

def format_time_3(now):
    # "%A, %d. %B %Y %I:%M:%S %p"
    weekday = weekdays[now[6]]
    month = months[now[1] - 1]
    hour = now[3]
    am_pm = "AM" if hour < 12 else "PM"
    hour_12 = hour % 12
    if hour_12 == 0:
        hour_12 = 12
    return "{}, {:02d}. {} {:04d} {:02d}:{:02d}:{:02d} {}".format(
        weekday, now[2], month, now[0], hour_12, now[4], now[5], am_pm)

def update_time():
    global last_millis
    current_millis = time.ticks_ms()
    
    if time.ticks_diff(current_millis, last_millis) > 1000:
        last_millis = current_millis
        
        now = time.localtime()
        
        buf1 = format_time_1(now)
        label1.set_text(buf1)
        print(buf1)
        
        buf2 = format_time_2(now)
        label2.set_text(buf2)
        print(buf2)
        
        buf3 = format_time_3(now)
        label3.set_text(buf3)
        print(buf3)

import task_handler
task_handler.TaskHandler(33)

while True:
    update_time()
    lv.task_handler()
    time.sleep_ms(5)