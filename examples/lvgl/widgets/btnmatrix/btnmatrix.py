'''
 * @file      btnmatrix.py
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

btnm_map = ["1", "2", "3", "4", "5", "\n",
            "6", "7", "8", "9", "0", "\n",
            "Action1", "Action2", ""]

def event_handler(e):
    code = e.get_code()
    obj = e.get_target()
    if code == lv.EVENT.VALUE_CHANGED:
        id = obj.get_selected_button()
        txt = obj.get_button_text(id)
        print("%s was pressed" % txt)

btnm1 = lv.buttonmatrix(scrn)
btnm1.set_map(btnm_map)
btnm1.set_button_width(10, 2)
btnm1.set_button_ctrl(10, lv.buttonmatrix.CTRL.CHECKABLE)
btnm1.set_button_ctrl(11, lv.buttonmatrix.CTRL.CHECKED)

btnm1.set_size(300, 160)
btnm1.center()

btnm1.set_style_bg_color(lv.color_hex(0x000000), 0)
btnm1.set_style_bg_color(lv.color_hex(0x4A86E8), lv.PART.ITEMS | lv.STATE.CHECKED)
btnm1.set_style_bg_color(lv.color_hex(0x666666), lv.PART.ITEMS | lv.STATE.PRESSED)
btnm1.set_style_text_color(lv.color_hex(0xFFFFFF), lv.PART.ITEMS)

btnm1.set_style_radius(8, lv.PART.MAIN)
btnm1.set_style_radius(15, lv.PART.ITEMS) 
btnm1.set_style_border_width(1, lv.PART.MAIN)
btnm1.set_style_border_color(lv.color_hex(0x555555), lv.PART.MAIN)
btnm1.set_style_pad_all(18, lv.PART.MAIN) 
btnm1.set_style_pad_row(8, lv.PART.MAIN) 
btnm1.set_style_pad_column(8, lv.PART.MAIN) 
btnm1.set_style_pad_top(1, lv.PART.ITEMS)
btnm1.set_style_pad_bottom(1, lv.PART.ITEMS) 
btnm1.set_style_pad_left(3, lv.PART.ITEMS)
btnm1.set_style_pad_right(3, lv.PART.ITEMS)
btnm1.set_style_min_width(25, lv.PART.ITEMS) 
btnm1.set_style_min_height(30, lv.PART.ITEMS)
btnm1.set_style_text_font(lv.font_montserrat_14, lv.PART.ITEMS)
btnm1.add_event_cb(event_handler, lv.EVENT.ALL, None)

import task_handler
task_handler.TaskHandler(33)