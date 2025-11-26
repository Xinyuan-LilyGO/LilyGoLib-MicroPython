'''
 * @file      arc.py
 * @license   MIT
 * @copyright Copyright (c) 2025  Shenzhen Xinyuan Electronic Technology Co., Ltd
 * @date      2025-10-09
'''
from machine import SPI, Pin, I2C
import sys
import lcd_bus
import st7796
import lvgl as lv
from micropython import const
import vibration
import _thread
import time

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

class ArcAnim:
    def __init__(self, arc_obj):
        self.arc = arc_obj
        self.value = 0
        self.direction = 1
        self.timer = lv.timer_create(self.update, 50, None)
    
    def update(self, timer):
        self.value += self.direction
        if self.value >= 100:
            self.value = 0
        elif self.value <= 0:
            self.value = 0
            self.direction = 1
        
        self.arc.set_value(self.value)
        
def lv_example_arc_1():
    label = lv.label(scrn)
    label.set_text("10%")
    arc = lv.arc(scrn)
    arc.set_size(150, 150)
    arc.set_rotation(135)
    arc.set_bg_angles(0, 270)
    arc.set_value(10)
    arc.center()
    arc.rotate_obj_to_angle(label, 25)

def lv_example_arc_2():
    # Create an Arc
    arc = lv.arc(scrn)
    arc.set_rotation(270)
    arc.set_bg_angles(0, 360)
    arc.set_size(150, 150)
    arc.center()
    time.sleep(1)
    try:
        arc.remove_style(None, lv.PART.KNOB)
    except:
        pass
    
    arc_anim = ArcAnim(arc)
    
lv_example_arc_1()
# lv_example_arc_2()

import task_handler
task_handler.TaskHandler(33)