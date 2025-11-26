'''
 * @file      scroll.py
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

panel = lv.obj(scrn)
panel.set_style_bg_color(lv.color_hex(0x000000), 0)
panel.set_size(200, 200)
panel.center()

child1 = lv.obj(panel)
child1.set_pos(0, 0)
child1.set_size(70, 70)
label1 = lv.label(child1)
label1.set_text("Zero")
label1.center()

child2 = lv.obj(panel)
child2.set_pos(160, 80)
child2.set_size(80, 80)

child2_btn = lv.button(child2)
child2_btn.set_size(100, 50)

label2 = lv.label(child2_btn)
label2.set_text("Right")
label2.center()

child3 = lv.obj(panel)
child3.set_pos(40, 160)
child3.set_size(100, 70)
label3 = lv.label(child3)
label3.set_text("Bottom")
label3.center()

import task_handler
task_handler.TaskHandler(33)