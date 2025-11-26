'''
 
 * @copyright Copyright (c) 2025  Shenzhen Xin Yuan Electronic Technology Co., Ltd
 * @date      2025-10-23
'''
from machine import SPI, Pin, I2C, PWM
import sys
import lcd_bus
import st7796
import lvgl as lv
from micropython import const
import vibration
import _thread
import rotary
import time
import task_handler

i2c = I2C(0, scl=Pin(2), sda=Pin(3), freq=400000)
vb = vibration.vibrationMotor(i2c)
encoder = rotary.RotaryEncoder(40, 41, 7)

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
backlight_pwm = PWM(backlight_pin)
backlight_pwm.freq(1000)
backlight_pwm.duty_u16(65535)

scrn = lv.screen_active()
scrn.set_style_bg_color(lv.color_hex(0x000000), 0)

current_focus = 0
current_rotation = lv.DISPLAY_ROTATION._90

def create_ui():
    global btn, value_label, label, selector
    
    scrn.clean()
    btn = lv.button(scrn)
    if current_rotation == lv.DISPLAY_ROTATION._0 or current_rotation == lv.DISPLAY_ROTATION._180:
        btn.set_width(lv.pct(30))
        btn.set_height(lv.pct(10))
    else:
        btn.set_width(lv.pct(60))
        btn.set_height(lv.pct(15))
    
    btn.set_style_bg_opa(0, 50)
    btn.align(lv.ALIGN.BOTTOM_MID, 0, -90)

    value_label = lv.label(scrn)
    value_label.set_text("0000")
    value_label.set_style_text_font(lv.font_montserrat_16, 0)
    value_label.align_to(btn, lv.ALIGN.OUT_TOP_MID, 0, -20)

    label = lv.label(btn)
    label.set_text("Set Ration")
    label.set_style_text_color(lv.color_hex(0x000000), 0)
    label.center()

    selector = lv.obj(scrn)
    
    if current_rotation == lv.DISPLAY_ROTATION._0 or current_rotation == lv.DISPLAY_ROTATION._180:
        selector.set_size(lv.pct(30), 50)
    else:
        selector.set_size(lv.pct(60), 50)
        
    selector.set_style_border_color(lv.color_hex(0x606060), 0)
    selector.set_style_border_width(3, 0)
    selector.set_style_bg_opa(0, 0)
    selector.set_style_radius(5, 0)
    selector.align(lv.ALIGN.BOTTOM_MID, 0, -90)

    focus_objects = [btn]
    return focus_objects

focus_objects = create_ui()

def rotate_display():
    global current_rotation

    rotations = [
        lv.DISPLAY_ROTATION._0,
        lv.DISPLAY_ROTATION._90, 
        lv.DISPLAY_ROTATION._180,
        lv.DISPLAY_ROTATION._270
    ]
    
    current_index = rotations.index(current_rotation)
    next_index = (current_index - 1) % 4
    current_rotation = rotations[next_index]
    
    display.set_rotation(current_rotation)
    
    global focus_objects
    focus_objects = create_ui()

def handle_encoder_input():
    global current_focus
    key = encoder.update()
    if key is None:
        return False
    if key == "enter":
        target = focus_objects[current_focus]
        if target == btn:
            rotate_display()
        return True
    return False

task_handler.TaskHandler(33)

while True:
    handle_encoder_input()
    time.sleep_ms(1)
