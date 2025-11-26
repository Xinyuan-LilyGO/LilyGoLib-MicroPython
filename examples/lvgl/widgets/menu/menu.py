'''
 * @file      menu.py
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

# Create a menu object
menu = lv.menu(lv.screen_active())
menu.set_size(480, 320)
menu.set_pos(0, 48)

# Create a sub page
sub_page = lv.menu_page(menu, None)

cont = lv.menu_cont(sub_page)
label = lv.label(cont)
label.set_text("Hello, I am hiding here")

# Create a main page  
main_page = lv.menu_page(menu, None)

cont = lv.menu_cont(main_page)
label = lv.label(cont)
label.set_text("Item 1")

cont = lv.menu_cont(main_page)
label = lv.label(cont)
label.set_text("Item 2")

cont = lv.menu_cont(main_page)
label = lv.label(cont)
label.set_text("Item 3 (Click me!)")
menu.set_load_page_event(cont, sub_page)

menu.set_page(main_page)

import task_handler
task_handler.TaskHandler(33)