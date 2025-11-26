'''
 * @file      img.py
 * @license   MIT
 * @copyright Copyright (c) 2025  Shenzhen Xinyuan Electronic Technology Co., Ltd
 * @date      2025-10-13
'''
from machine import SPI, Pin, I2C
import sys
import lcd_bus
import st7796
import lvgl as lv
from micropython import const
import vibration
import _thread
import gear

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

img_cogwheel_argb = lv.image_dsc_t()
img_cogwheel_argb.header.w = 100
img_cogwheel_argb.header.h = 100
img_cogwheel_argb.header.stride = 400
img_cogwheel_argb.header.cf = lv.COLOR_FORMAT.ARGB8888
img_cogwheel_argb.data = gear.img_cogwheel_argb_map
img_cogwheel_argb.data_size = len(gear.img_cogwheel_argb_map)

img1 = lv.image(scrn)
img1.set_src(img_cogwheel_argb)
img1.align(lv.ALIGN.CENTER, 0, 0)

img2 = lv.image(scrn)
img2.set_src(lv.SYMBOL.OK + " Accept")
img2.align_to(img1, lv.ALIGN.OUT_BOTTOM_MID, 0, 20)

import task_handler
task_handler.TaskHandler(33)