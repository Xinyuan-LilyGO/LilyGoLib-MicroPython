'''
 * @file      textarea.py
 * @license   MIT
 * @copyright Copyright (c) 2025  Shenzhen Xinyuan Electronic Technology Co., Ltd
 * @date      2025-10-16
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

text_display = lv.label(scrn)
text_display.set_size(280, 40)
text_display.align(lv.ALIGN.TOP_MID, 0, 60)
text_display.set_style_bg_color(lv.color_hex(0x000000), 0)
text_display.set_style_text_color(lv.color_hex(0xffffff), 0)
text_display.set_style_bg_opa(lv.OPA.COVER, 0)
text_display.set_style_pad_all(5, 0)
text_display.set_text("")
text_display.set_style_border_width(1, 0)
text_display.set_style_radius(10, 0)
text_display.set_style_border_color(lv.color_hex(0x808080), 0)

current_text = ""

def btnm_event_handler(e):
    global current_text
    obj = lv.event_get_target(e)
    btn_id = lv.buttonmatrix_get_selected_button(obj)
    txt = lv.buttonmatrix_get_button_text(obj, btn_id)
    
    if txt == lv.SYMBOL.BACKSPACE:
        current_text = current_text[:-1]
    elif txt == lv.SYMBOL.NEW_LINE:
        print("Enter was pressed. The current text is:", current_text)
    else:
        current_text += txt
    text_display.set_text(current_text)

btnm_map = [
    "1", "2", "3", "\n",
    "4", "5", "6", "\n", 
    "7", "8", "9", "\n",
    lv.SYMBOL.BACKSPACE, "0", lv.SYMBOL.NEW_LINE, ""
]

btnm = lv.buttonmatrix(scrn)
btnm.set_size(190, 140)
btnm.set_style_bg_color(lv.color_hex(0x000000), 0)
btnm.align(lv.ALIGN.BOTTOM_MID, 0, -60)
btnm.add_event_cb(btnm_event_handler, lv.EVENT.VALUE_CHANGED, None)
btnm.remove_flag(lv.obj.FLAG.CLICK_FOCUSABLE)
btnm.set_map(btnm_map)

import task_handler
task_handler.TaskHandler(33)