'''
 * @file      grid.py
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

cont = lv.obj(scrn)
cont.set_style_bg_color(lv.color_hex(0x000000), 0)  
cont.set_size(300, 220)
cont.center()

rows = []
for row in range(3):
    row_cont = lv.obj(cont)
    row_cont.set_style_bg_color(lv.color_hex(0x000000), 0)  
    row_cont.set_size(260, 50)
    row_cont.set_y(row * 70)
    row_cont.set_flex_flow(lv.FLEX_FLOW.ROW)
    row_cont.set_flex_align(lv.FLEX_ALIGN.SPACE_EVENLY, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER)
    rows.append(row_cont)

for i in range(9):
    row = i // 3
    col = i % 3
    
    obj = lv.button(rows[row])
    obj.set_size(70, 50)
    
    label = lv.label(obj)
    label.set_text("c%d, r%d" % (col, row))
    label.center()

import task_handler
task_handler.TaskHandler(33)