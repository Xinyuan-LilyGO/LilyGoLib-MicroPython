'''
 * @file      keyboard.py
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

def ta_event_cb(e, kb):
    code = e.get_code()
    ta = e.get_target()
    
    if code == lv.EVENT.FOCUSED:
        kb.set_textarea(ta)
        kb.clear_state(lv.STATE.HIDDEN)

try:
    kb = lv.keyboard(scrn)
except Exception as e:
    print("error:", e)
    kb = None

ta1 = lv.textarea(scrn)
ta1.set_pos(5, 55)
ta1.set_size(140, 80)
ta1.set_placeholder_text("Hello")
ta1.add_event_cb(lambda e: ta_event_cb(e, kb), lv.EVENT.ALL, None)

ta2 = lv.textarea(scrn)
ta2.set_pos(335, 55)
ta2.set_size(140, 80)
ta2.add_event_cb(lambda e: ta_event_cb(e, kb), lv.EVENT.ALL, None)

if kb:
    kb.set_pos(0, -50)
    kb.set_size(480, 100)
    kb.set_textarea(ta2)
    
    style_default = lv.style_t()
    style_default.init()
    style_default.set_radius(8)
    
    # style_pressed = lv.style_t()
    # style_pressed.init()
    # style_pressed.set_radius(6)
    # style_pressed.set_bg_color(lv.color_hex(0x000000)) 
    
    kb.add_style(style_default, lv.PART.ITEMS | lv.STATE.DEFAULT)
    #kb.add_style(style_pressed, lv.PART.ITEMS | lv.STATE.PRESSED)

import task_handler
task_handler.TaskHandler(33)