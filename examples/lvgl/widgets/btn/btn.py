'''
 * @file      btn.py
 * @license   MIT
 * @copyright Copyright (c) 2025  Shenzhen Xinyuan Electronic Technology Co., Ltd
 * @date      2025-10-10
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

def event_handler(e):
    code = e.get_code()
    if code == lv.EVENT.CLICKED:
        print("Clicked")
    elif code == lv.EVENT.VALUE_CHANGED:
        print("Toggled")

btn1 = lv.button(scrn)
btn1.add_event_cb(event_handler, lv.EVENT.ALL, None)
btn1.align(lv.ALIGN.CENTER, 0, -40)
btn1.set_width(80)
btn1.set_height(40)

label1 = lv.label(btn1)
label1.set_text("Button")
label1.set_style_text_color(lv.color_hex(0x000000), 0)
label1.center()

btn2 = lv.button(scrn)
btn2.add_event_cb(event_handler, lv.EVENT.ALL, None)
btn2.align(lv.ALIGN.CENTER, 0, 40)
btn2.add_flag(lv.obj.FLAG.CHECKABLE)
btn2.set_width(80)
btn2.set_height(40)

label2 = lv.label(btn2)
label2.set_text("Toggle")
label2.set_style_text_color(lv.color_hex(0x000000), 0)
label2.center()

import task_handler
task_handler.TaskHandler(33)