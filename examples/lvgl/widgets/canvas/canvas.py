'''
 * @file      canvas.py
 * @license   MIT
 * @copyright Copyright (c) 2025  Shenzhen Xinyuan Electronic Technology Co., Ltd
 * @date      2025-10-11
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

canvas1 = lv.canvas(scrn)
canvas1.set_size(200, 150) 
canvas1.center()
canvas1.set_style_bg_color(lv.palette_main(lv.PALETTE.GREY), 0) 
canvas1.set_style_bg_opa(lv.OPA.COVER, 0) 
canvas1.move_foreground()

canvas2 = lv.canvas(scrn)
canvas2.set_size(200, 150) 
canvas2.center()
canvas2.set_style_bg_opa(lv.OPA.COVER, 0)
canvas2.set_style_bg_color(lv.color_hex(0x000000), 0)
canvas2.set_style_transform_rotation(115, 0) 
canvas2.set_style_transform_pivot_x(125, 0)
canvas2.set_style_transform_pivot_y(75, 0) 
canvas2.move_foreground()

canvas3 = lv.canvas(scrn)
canvas3.set_size(100, 100)
canvas3.center()
canvas3.set_style_bg_opa(lv.OPA.TRANSP, 0) 
canvas3.move_foreground()
canvas3.set_style_transform_rotation(115, 0) 
canvas3.set_style_transform_pivot_x(125, 0)
canvas3.set_style_transform_pivot_y(75, 0) 
rect = lv.obj(canvas3)
rect.set_size(80, 60)
rect.set_style_bg_color(lv.palette_main(lv.PALETTE.RED), 0)
rect.set_style_bg_grad_color(lv.palette_main(lv.PALETTE.BLUE), 0)
rect.set_style_bg_grad_dir(lv.GRAD_DIR.VER, 0)
rect.set_style_radius(15, 0)
rect.set_style_border_width(2, 0)
rect.set_style_border_color(lv.color_black(), 0)
rect.set_style_border_opa(lv.OPA._90, 0)
rect.set_style_shadow_width(5, 0)
rect.set_style_shadow_color(lv.color_black(), 0)

label = lv.label(scrn)
label.set_text("Some\ntext on\ntext\ncanvas")
label.set_style_text_color(lv.palette_main(lv.PALETTE.ORANGE), 0)
label.set_style_text_font(lv.font_montserrat_12, 0)
label.set_style_transform_rotation(115, 0) 
label.set_style_transform_pivot_x(125, 0)
label.set_style_transform_pivot_y(75, 0) 
label.set_pos(185, 175)
label.move_foreground()

import task_handler
task_handler.TaskHandler(33)
