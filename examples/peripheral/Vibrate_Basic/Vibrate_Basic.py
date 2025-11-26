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
backlight_pin.value(1)

scrn = lv.screen_active()
scrn.set_style_bg_color(lv.color_hex(0x000000), 0)

DEVICE_MIN_BRIGHTNESS_LEVEL = 0
DEVICE_MAX_BRIGHTNESS_LEVEL = 113

current_focus = 0
focus_objects = []

slider_mode = False

def changed_event_cb(e):
    pass

selector = lv.obj(scrn)
selector.set_size(lv.pct(85), lv.SIZE_CONTENT)
selector.set_style_border_color(lv.color_hex(0x808080), 0)
selector.set_style_border_width(3, 0)
selector.set_style_bg_opa(0, 0)
selector.set_style_radius(20, 0)

slider = lv.slider(scrn)
slider.set_width(lv.pct(80))
slider.set_height(lv.pct(10))
slider.set_range(DEVICE_MIN_BRIGHTNESS_LEVEL, DEVICE_MAX_BRIGHTNESS_LEVEL)
slider.add_event_cb(changed_event_cb, lv.EVENT.VALUE_CHANGED, None)
slider.center()
slider.set_style_radius(20, lv.PART.MAIN)      
slider.set_style_radius(20, lv.PART.INDICATOR) 
slider.set_style_bg_opa(lv.OPA.COVER, lv.PART.KNOB)
slider.set_value(DEVICE_MIN_BRIGHTNESS_LEVEL, False)

slider_label = lv.label(scrn)
slider_label.set_text("Effect:0")
slider_label.align_to(slider, lv.ALIGN.OUT_BOTTOM_MID, 0, 10)

focus_objects = [slider]

def update_selector():
    target = focus_objects[current_focus]
    selector.set_pos(target.get_x(), target.get_y())
    selector.set_size(target.get_width(), target.get_height())

pending_vibration = False
last_change_time = 0
last_effect_value = 0

def handle_encoder_input():
    global current_focus, slider_mode
    global pending_vibration, last_change_time, last_effect_value
    key = encoder.update()

    if key is None:
        return False

    if slider_mode:
        value = slider.get_value()
        if key == "down":
            value = min(DEVICE_MAX_BRIGHTNESS_LEVEL, value + 1)
            slider_label.set_text(f"Effect:{value}")
            try:
                slider.set_value(value)
            except Exception:
                slider.set_value(value, False)
                
            last_effect_value = value
            last_change_time = time.ticks_ms()
            pending_vibration = True
            return True

        elif key == "up":
            value = max(DEVICE_MIN_BRIGHTNESS_LEVEL, value - 1)
            slider_label.set_text(f"Effect:{value}")
            try:
                slider.set_value(value)
            except Exception:
                slider.set_value(value, False)

            last_effect_value = value
            last_change_time = time.ticks_ms()
            pending_vibration = True
            return True

        elif key == "enter":
            slider_mode = False
            selector.set_style_border_color(lv.color_hex(0x808080), 0)
            return True
        return False

    if key == "enter":
        target = focus_objects[current_focus]
        if target == slider:
            slider_mode = True
            selector.set_style_border_color(lv.color_hex(0xffff00), 0)
        return True
    return False

update_selector()
task_handler.TaskHandler(33)

while True:
    handle_encoder_input()
    if pending_vibration:
        if time.ticks_diff(time.ticks_ms(), last_change_time) >= 500:
            try:
                vb.setWaveform(0, last_effect_value)
                vb.run()
            except Exception:
                try:
                    vb.vibrate(1, 60)
                except Exception:
                    pass
            pending_vibration = False
    time.sleep_ms(1)