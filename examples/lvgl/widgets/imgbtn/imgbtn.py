'''
 * @file      imgbtn.py
 * @license   MIT
 * @copyright Copyright (c) 2025  Shenzhen Xinyuan Electronic Technology Co., Ltd
 * @date      2025-10-15
'''
from machine import SPI, Pin, I2C
import sys
import lcd_bus
import st7796
import lvgl as lv
from micropython import const
import vibration
import _thread
import imagebutton

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

imagebutton_left = lv.image_dsc_t()
imagebutton_left.header.w = 8
imagebutton_left.header.h = 50
imagebutton_left.header.stride = 32
imagebutton_left.header.cf = lv.COLOR_FORMAT.ARGB8888
imagebutton_left.data = imagebutton.imagebutton_left_map
imagebutton_left.data_size = len(imagebutton.imagebutton_left_map)

imagebutton_mid = lv.image_dsc_t()
imagebutton_mid.header.w = 5
imagebutton_mid.header.h = 49
imagebutton_mid.header.stride = 20
imagebutton_mid.header.cf = lv.COLOR_FORMAT.ARGB8888
imagebutton_mid.data = imagebutton.imagebutton_mid_map
imagebutton_mid.data_size = len(imagebutton.imagebutton_mid_map)

imagebutton_right = lv.image_dsc_t()
imagebutton_right.header.w = 8
imagebutton_right.header.h = 50
imagebutton_right.header.stride = 32
imagebutton_right.header.cf = lv.COLOR_FORMAT.ARGB8888
imagebutton_right.data = imagebutton.imagebutton_right_map
imagebutton_right.data_size = len(imagebutton.imagebutton_right_map)

tr_prop = [lv.STYLE.TRANSFORM_WIDTH, lv.STYLE.IMAGE_RECOLOR_OPA, 0]
tr = lv.style_transition_dsc_t()
# lv.style_transition_dsc_init(tr, tr_prop, lv.anim_t.path_linear, 200, 0, None)

style_def = lv.style_t()
style_def.init()
style_def.set_text_color(lv.color_hex(0x000000))
style_def.set_transition(tr)

style_pr = lv.style_t()
style_pr.init()
style_pr.set_image_recolor_opa(lv.OPA._30)
style_pr.set_image_recolor(lv.color_black())
style_pr.set_transform_width(20)

imagebutton1 = lv.imagebutton(lv.screen_active())
imagebutton1.set_src(lv.imagebutton.STATE.RELEASED, imagebutton_left, imagebutton_mid, imagebutton_right)
imagebutton1.add_style(style_def, 0)
imagebutton1.add_style(style_pr, lv.STATE.PRESSED)

imagebutton1.set_width(100)
imagebutton1.center()

label = lv.label(imagebutton1)
label.set_text("Button")
label.center()

import task_handler
task_handler.TaskHandler(33)