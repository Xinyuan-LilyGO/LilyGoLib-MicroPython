'''
 * @file      roller.py
 * @license   MIT
 * @copyright Copyright (c) 2025  Shenzhen Xinyuan Electronic Technology Co., Ltd
 * @date      2025-10-15
'''
from machine import SPI, Pin, I2C
import sys
import lcd_bus
import st7796
import lvgl as lv
from micropython import const
import vibration
import _thread

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

def event_handler(e):
    code = e.get_code()
    obj = e.get_target()
    if code == lv.EVENT.VALUE_CHANGED:
        buf = bytearray(32)
        obj.get_selected_str(buf, len(buf))
        print("Selected month:", buf.decode('utf-8'))

roller1 = lv.roller(scrn)
roller1.set_style_bg_color(lv.color_hex(0x000000), 0)
roller1.set_options(
    "January\n"
    "February\n"
    "March\n"
    "April\n"
    "May\n"
    "June\n"
    "July\n"
    "August\n"
    "September\n"
    "October\n"
    "November\n"
    "December",
    lv.roller.MODE.INFINITE
)

roller1.set_visible_row_count(4)
roller1.center()
roller1.add_event_cb(event_handler, lv.EVENT.ALL, None)

import task_handler
task_handler.TaskHandler(33)