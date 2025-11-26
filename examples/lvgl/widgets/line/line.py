'''
 * @file      line.py
 * @license   MIT
 * @copyright Copyright (c) 2025  Shenzhen Xinyuan Electronic Technology Co., Ltd
 * @date      2025-10-14
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
scrn.set_style_bg_color(lv.color_hex(0x000000), 0)

# Create an array for the points of the line
line_points = [
    {"x": 5, "y": 5},
    {"x": 70, "y": 70}, 
    {"x": 120, "y": 10},
    {"x": 180, "y": 60},
    {"x": 240, "y": 10}
]

# Create style
style_line = lv.style_t()
style_line.init()
style_line.set_line_width(8)
style_line.set_line_color(lv.palette_main(lv.PALETTE.BLUE))
style_line.set_line_rounded(True)

# Create a line and apply the new style
line1 = lv.line(scrn)
line1.set_points(line_points, 5)  # Set the points
line1.add_style(style_line, 0)
line1.center()

import task_handler
task_handler.TaskHandler(33)