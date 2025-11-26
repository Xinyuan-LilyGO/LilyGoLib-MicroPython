'''
 * @file      spinbox.py
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

spinbox = lv.spinbox(scrn)
spinbox.set_style_bg_color(lv.color_hex(0x000000), 0)
lv.spinbox.set_range(spinbox, -1000, 25000)
lv.spinbox.set_digit_format(spinbox, 5, 2)
lv.spinbox.step_prev(spinbox)
spinbox.set_width(100)
spinbox.center()

h = spinbox.get_height()

btn_plus = lv.button(scrn)
btn_plus.set_size(h, h)
btn_plus.align_to(spinbox, lv.ALIGN.OUT_RIGHT_MID, 5, 0)

label_plus = lv.label(btn_plus)
label_plus.set_text(lv.SYMBOL.PLUS)
label_plus.center()

def spinbox_increment_event_cb(e):
    code = e.get_code()
    if code == lv.EVENT.SHORT_CLICKED or code == lv.EVENT.LONG_PRESSED_REPEAT:
        lv.spinbox.increment(spinbox)

btn_plus.add_event_cb(spinbox_increment_event_cb, lv.EVENT.ALL, None)

btn_minus = lv.button(scrn)
btn_minus.set_size(h, h)
btn_minus.align_to(spinbox, lv.ALIGN.OUT_LEFT_MID, -5, 0)

label_minus = lv.label(btn_minus)
label_minus.set_text(lv.SYMBOL.MINUS)
label_minus.center()

def spinbox_decrement_event_cb(e):
    code = e.get_code()
    if code == lv.EVENT.SHORT_CLICKED or code == lv.EVENT.LONG_PRESSED_REPEAT:
        lv.spinbox.decrement(spinbox)

btn_minus.add_event_cb(spinbox_decrement_event_cb, lv.EVENT.ALL, None)

import task_handler
task_handler.TaskHandler(33)