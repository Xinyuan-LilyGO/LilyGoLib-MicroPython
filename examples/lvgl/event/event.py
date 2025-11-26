'''
 * @file      event.py
 * @license   MIT
 * @copyright Copyright (c) 2025  Shenzhen Xinyuan Electronic Technology Co., Ltd
 * @date      2025-10-20
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

def event_cb(e):
    print("Clicked")
    cnt = 1
    btn = lv.event.get_target_obj(e)
    label = btn.get_child(0)
    label.set_text(str(cnt))
    cnt += 1

btn = lv.button(scrn)
btn.set_size(100, 50)
btn.center()
btn.add_event_cb(event_cb, lv.EVENT.CLICKED, None)

label = lv.label(btn)
label.set_text("Click me!")
label.center()

import task_handler
task_handler.TaskHandler(33)