'''
 * @file      flex.py
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

# Create a container with ROW flex direction
cont_row = lv.obj(scrn)
cont_row.set_style_bg_color(lv.color_hex(0x000000), 0)  
cont_row.set_size(300, 75)
cont_row.align(lv.ALIGN.TOP_MID, 0, 55)
cont_row.set_flex_flow(lv.FLEX_FLOW.ROW)

# Create a container with COLUMN flex direction
cont_col = lv.obj(scrn)
cont_col.set_style_bg_color(lv.color_hex(0x000000), 0)  
cont_col.set_size(200, 150)
cont_col.align_to(cont_row, lv.ALIGN.OUT_BOTTOM_MID, 0, 5)
cont_col.set_flex_flow(lv.FLEX_FLOW.COLUMN)

for i in range(10):
    # Add items to the row
    obj_row = lv.button(cont_row)
    obj_row.set_size(100, lv.pct(100))
    
    label_row = lv.label(obj_row)
    label_row.set_text("Item: %d" % i)
    label_row.center()
    
    # Add items to the column  
    obj_col = lv.button(cont_col)
    obj_col.set_size(lv.pct(100), lv.SIZE_CONTENT)
    
    label_col = lv.label(obj_col)
    label_col.set_text("Item: %d" % i)
    label_col.center()


import task_handler
task_handler.TaskHandler(33)