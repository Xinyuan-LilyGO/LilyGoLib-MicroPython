'''
 * @file      tileview.py
 * @license   MIT
 * @copyright Copyright (c) 2025  Shenzhen Xinyuan Electronic Technology Co., Ltd
 * @date      2025-10-16
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

tv = lv.tileview(scrn)

tile1 = tv.add_tile(0, 0, lv.DIR.BOTTOM)
label1 = lv.label(tile1)
label1.set_text("Scroll down")
label1.center()

tile2 = tv.add_tile(0, 1, lv.DIR.TOP | lv.DIR.RIGHT)

btn = lv.button(tile2)
btn.set_size(lv.SIZE_CONTENT, lv.SIZE_CONTENT)
btn.center()

label2 = lv.label(btn)
label2.set_text("Scroll up or right")
label2.center()

tile3 = tv.add_tile(1, 1, lv.DIR.LEFT)
list1 = lv.list(tile3)
list1.set_size(lv.pct(100), lv.pct(100))

list1.add_button(None, "One")
list1.add_button(None, "Two")
list1.add_button(None, "Three")
list1.add_button(None, "Four")
list1.add_button(None, "Five")
list1.add_button(None, "Six")
list1.add_button(None, "Seven")
list1.add_button(None, "Eight")
list1.add_button(None, "Nine")
list1.add_button(None, "Ten")

import task_handler
task_handler.TaskHandler(33)