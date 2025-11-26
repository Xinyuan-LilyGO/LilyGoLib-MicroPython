'''
 * @file      LightSleep.py
 * @license   MIT
 * @copyright Copyright (c) 2025  ShenZhen XinYuan Electronic Technology Co., Ltd
 * @date      2025-09-25
'''
from machine import SPI, I2C, Pin, deepsleep
import time
import sys
import lcd_bus
import st7796
import lvgl as lv
from micropython import const
import vibration
import _thread

i2c = I2C(0, scl=Pin(2), sda=Pin(3), freq=400000)

vb = vibration.vibrationMotor(i2c)

# Initialize the sleep counter
sleep_counter = 1

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

slider = lv.slider(scrn)
slider.set_size(350, 30)
slider.center()

label = lv.label(scrn)
label.set_text('Sleep counter: 1')
label.align(lv.ALIGN.CENTER, 0, -50)

def on_button_press(pin):
    global sleep_counter
    sleep_counter += 1
    label.set_text(f'Sleep counter: {sleep_counter}')
#     scrn.set_style_bg_color(lv.color_hex(0xffffff), 0)
#     backlight_pin.value(0)
    deepsleep(100)
    print("This will never be printed")

# Configure button on pin 35
button_pin = Pin(0, Pin.IN, Pin.PULL_UP)
button_pin.irq(trigger=Pin.IRQ_FALLING, handler=on_button_press)

def scan_i2c_devices():
    print("Listing directory: /")
    print("    " + " ".join("{:2x}".format(x) for x in range(16)))
    devices = i2c.scan()
    for i in range(0, 128, 16):
        print("{:02x}:".format(i), end=" ")
        for j in range(16):
            addr = i + j
            if addr in devices:
                print("{:02X}".format(addr), end=" ")
            else:
                print("--", end=" ")
        print()

scan_i2c_devices()
import task_handler
task_handler.TaskHandler(33)
