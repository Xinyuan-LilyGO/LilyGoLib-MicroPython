'''
 * @file      DisplayBrightness.py
 * @license   MIT
 * @copyright Copyright (c) 2025  Shenzhen Xin Yuan Electronic Technology Co., Ltd
 * @date      2025-10-22
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

DEVICE_MIN_BRIGHTNESS_LEVEL = 0
DEVICE_MAX_BRIGHTNESS_LEVEL = 255

current_focus = 0
focus_objects = []

def set_brightness(value):
    value = max(DEVICE_MIN_BRIGHTNESS_LEVEL, min(DEVICE_MAX_BRIGHTNESS_LEVEL, value))
    brightness = int(value * 65535 / 255)
    brightness = max(0, min(65535, brightness))
    backlight_pwm.duty_u16(brightness)

def value_changed_event_cb(e):
    slider = lv.event.get_target_obj(e)
    value = slider.get_value()
    set_brightness(value)

def set_to_max(e):
    set_brightness(DEVICE_MAX_BRIGHTNESS_LEVEL)
    slider.set_value(DEVICE_MAX_BRIGHTNESS_LEVEL, False)
    
def set_to_min(e):
    set_brightness(DEVICE_MIN_BRIGHTNESS_LEVEL)
    slider.set_value(DEVICE_MIN_BRIGHTNESS_LEVEL, False)
    
btn1 = lv.button(scrn)
btn1.add_event_cb(set_to_max, lv.EVENT.CLICKED, None)
btn1.set_width(lv.pct(80))
btn1.align(lv.ALIGN.CENTER, 0, -10)
btn1.set_style_bg_opa(60, 0)

label1 = lv.label(btn1)
label1.set_text("Set to Max")
label1.center()

btn2 = lv.button(scrn)
btn2.add_event_cb(set_to_min, lv.EVENT.CLICKED, None)
btn2.set_width(lv.pct(80))
btn2.align_to(btn1, lv.ALIGN.OUT_BOTTOM_MID, 0, 10)
btn2.set_style_bg_opa(60, 0)

label2 = lv.label(btn2)
label2.set_text("Set to Min")
label2.center()

slider = lv.slider(scrn)
slider.set_width(lv.pct(80))
slider.set_height(lv.pct(10))
slider.set_range(DEVICE_MIN_BRIGHTNESS_LEVEL, DEVICE_MAX_BRIGHTNESS_LEVEL)
slider.add_event_cb(value_changed_event_cb, lv.EVENT.VALUE_CHANGED, None)
slider.align_to(btn2, lv.ALIGN.OUT_BOTTOM_MID, 0, 10)
slider.set_value(DEVICE_MAX_BRIGHTNESS_LEVEL, False)

selector = lv.obj(scrn)
selector.set_size(lv.pct(85), lv.SIZE_CONTENT)
selector.set_style_border_color(lv.color_hex(0x808080), 0)
selector.set_style_border_width(3, 0)
selector.set_style_bg_opa(0, 0)
selector.set_style_radius(5, 0)

focus_objects = [btn1, slider, btn2]

def update_selector():
    target = focus_objects[current_focus]
    selector.set_pos(target.get_x(), target.get_y())
    selector.set_size(target.get_width(), target.get_height())

slider_mode = False

def handle_encoder_input():
    global current_focus, slider_mode
    key = encoder.update()

    if key is None:
        return False

    if slider_mode:
        value = slider.get_value()
        if key == "up":
            value = min(DEVICE_MAX_BRIGHTNESS_LEVEL, value - 30)
            try:
                slider.set_value(value)
            except Exception:
                slider.set_value(value, False)
            set_brightness(value)
            return True
        elif key == "down":
            value = max(DEVICE_MIN_BRIGHTNESS_LEVEL, value + 30)
            try:
                slider.set_value(value)
            except Exception:
                slider.set_value(value, False)
            set_brightness(value)
            return True
        elif key == "enter":
            slider_mode = False
            selector.set_style_border_color(lv.color_hex(0x808080), 0)
            return True
        return False

    if key == "up":
        current_focus = (current_focus + 1) % len(focus_objects)
        update_selector()
        return True
    elif key == "down":
        current_focus = (current_focus - 1) % len(focus_objects)
        update_selector()
        return True
    elif key == "enter":
        target = focus_objects[current_focus]
        if target == btn1:
            set_to_max(None)
        elif target == btn2:
            set_to_min(None)
        elif target == slider:
            slider_mode = True
            selector.set_style_border_color(lv.color_hex(0xffff00), 0)
        return True
    return False

update_selector()
task_handler.TaskHandler(33)

while True:
    handle_encoder_input()
    time.sleep_ms(1)
