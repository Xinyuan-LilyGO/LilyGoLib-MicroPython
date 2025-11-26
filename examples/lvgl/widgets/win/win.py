'''
 * @file      win.py
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
    spi_bus = SPI.Bus(host=1, mosi=34, miso=33, sck=35)
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
    obj = e.get_target_obj()
    print(f"Button {obj.get_index()} clicked")

win = lv.win(scrn)
win.set_height(320)
win.set_pos(0,46)

btn_left = lv.win.add_button(win, lv.SYMBOL.LEFT, 40)
btn_left.add_event_cb(event_handler, lv.EVENT.CLICKED, None)

lv.win.add_title(win, "A title")
btn_right = lv.win.add_button(win, lv.SYMBOL.RIGHT, 40)
btn_right.add_event_cb(event_handler, lv.EVENT.CLICKED, None)
btn_close = lv.win.add_button(win, lv.SYMBOL.CLOSE, 60)
btn_close.add_event_cb(event_handler, lv.EVENT.CLICKED, None)

cont = lv.win.get_content(win)
# cont.set_style_bg_color(lv.color_hex(0x000000), 0)
label = lv.label(cont)
label.set_text("This is\n"
               "a pretty\n"
               "long text\n"
               "to see how\n"
               "the window\n"
               "becomes\n"
               "scrollable.\n"
               "\n"
               "\n"
               "Some more\n"
               "text to be\n"
               "sure it\n"
               "overflows. :)")

label.set_width(lv.pct(100))

import task_handler
task_handler.TaskHandler(33)