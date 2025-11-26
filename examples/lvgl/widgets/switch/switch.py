'''
 * @file      switch.py
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

import time

_thread.start_new_thread(vibrate_motor, ())
time.sleep(1)
backlight_pin = Pin(42, Pin.OUT)
backlight_pin.value(1)

scrn = lv.screen_active()
scrn.set_style_bg_color(lv.color_hex(0x000000), 0)  

def event_handler(e):
    code = e.get_code()
    obj = e.get_target()
    if code == lv.EVENT.VALUE_CHANGED:
        state = "On" if obj.has_state(lv.STATE.CHECKED) else "Off"
        print("State: %s" % state)

scrn.set_flex_flow(lv.FLEX_FLOW.COLUMN)
scrn.set_flex_align(lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER)

style_knob = lv.style_t()
style_knob.init()
style_knob.set_bg_color(lv.color_hex(0x000000))
style_knob.set_bg_opa(lv.OPA.COVER)

sw1 = lv.switch(scrn)
sw1.add_style(style_knob, lv.PART.KNOB)
sw1.add_event_cb(event_handler, lv.EVENT.ALL, None)
sw1.add_flag(lv.obj.FLAG.EVENT_BUBBLE)

sw2 = lv.switch(scrn)
sw2.add_state(lv.STATE.CHECKED)
sw2.add_style(style_knob, lv.PART.KNOB)
sw2.add_event_cb(event_handler, lv.EVENT.ALL, None)

sw3 = lv.switch(scrn)
sw3.add_state(lv.STATE.DISABLED)
sw3.add_style(style_knob, lv.PART.KNOB)
sw3.add_event_cb(event_handler, lv.EVENT.ALL, None)

sw4 = lv.switch(scrn)
sw4.add_state(lv.STATE.CHECKED | lv.STATE.DISABLED)
sw4.add_style(style_knob, lv.PART.KNOB)
sw4.add_event_cb(event_handler, lv.EVENT.ALL, None)

import task_handler
task_handler.TaskHandler(33)
