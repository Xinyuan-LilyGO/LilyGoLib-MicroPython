'''
 * @file      checkbox.py
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

style_radio = lv.style_t()
style_radio_chk = lv.style_t()
style_radio.init()
style_radio.set_radius(lv.RADIUS_CIRCLE)
style_radio.set_bg_color(lv.color_hex(0x000000))
style_radio_chk.init()
style_radio_chk.set_bg_color(lv.color_hex(0x000000))

class RadioGroup:
    def __init__(self, active_index=0):
        self.active_index = active_index

radio_group1 = RadioGroup(0)
radio_group2 = RadioGroup(0)

def create_radio_event_handler(radio_group):
    def handler(e):
        cont = e.get_current_target()
        act_cb = e.get_target()
        if act_cb == cont:
            return
        old_cb = cont.get_child(radio_group.active_index)
        old_cb.clear_state(lv.STATE.CHECKED)
        act_cb.add_state(lv.STATE.CHECKED)
        radio_group.active_index = cont.get_child_index(act_cb)
        print("Selected radio buttons:", radio_group1.active_index, radio_group2.active_index)
    return handler

def radiobutton_create(parent, txt):
    obj = lv.checkbox(parent)
    obj.set_text(txt)
    obj.add_flag(lv.obj.FLAG.EVENT_BUBBLE)
    obj.add_style(style_radio, lv.PART.INDICATOR)
    obj.add_style(style_radio_chk, lv.PART.INDICATOR | lv.STATE.CHECKED)
    return obj

cont1 = lv.obj(scrn)
cont1.set_style_bg_color(lv.color_hex(0x000000), 0)
cont1.set_flex_flow(lv.FLEX_FLOW.COLUMN)
cont1.set_size(175, 200)
cont1.set_y(50)
cont1.add_event_cb(create_radio_event_handler(radio_group1), lv.EVENT.CLICKED, None)

checkboxes1 = []
for i in range(5):
    buf = "A %d" % (i + 1)
    cb = radiobutton_create(cont1, buf)
    checkboxes1.append(cb)

checkboxes1[0].add_state(lv.STATE.CHECKED)

cont2 = lv.obj(scrn)
cont2.set_style_bg_color(lv.color_hex(0x000000), 0)
cont2.set_flex_flow(lv.FLEX_FLOW.COLUMN)
cont2.set_size(175, 200) 
cont2.set_x(200)
cont2.set_y(50)
cont2.add_event_cb(create_radio_event_handler(radio_group2), lv.EVENT.CLICKED, None)

checkboxes2 = []
for i in range(3):
    buf = "B %d" % (i + 1)
    cb = radiobutton_create(cont2, buf)
    checkboxes2.append(cb)

checkboxes2[0].add_state(lv.STATE.CHECKED)

import task_handler
task_handler.TaskHandler(33)