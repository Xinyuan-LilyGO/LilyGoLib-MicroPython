'''
 * @file      ImageDecoder.py
 * @license   MIT
 * @copyright Copyright (c) 2025  Shenzhen Xinyuan Electronic Technology Co., Ltd
 * @date      2025-10-28
 * @Note      You need to upload the files from the data file to the FFat
 *            file system before using this example
 * @note      Upload the entire data folder
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
import fs_driver
import gc
import task_handler

i2c = I2C(0, scl=Pin(2), sda=Pin(3), freq=400000)
vb = vibration.vibrationMotor(i2c)

def vibrate_motor():
    vb.vibrate(1, 200)

lv.init()

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

_thread.start_new_thread(vibrate_motor, ())

backlight_pin = Pin(42, Pin.OUT)
backlight_pin.value(1)

scr = lv.screen_active()
scr.set_style_bg_color(lv.color_hex(0x000000), 0)  

fs_drv = lv.fs_drv_t()
fs_driver.fs_register(fs_drv, 'S')

img_symbol = lv.image(scr)
img_symbol.align(lv.ALIGN.CENTER, 0, 0)

task_handler.TaskHandler(33)

image_files = [
    'S:data/logo.bmp',
    'S:data/logoColor1.png',
    'S:data/logoColor2.png',
    'S:data/product0.png',
    'S:data/product1.png',
    'S:data/product2.png',
    'S:data/product3.png',
    'S:data/product4.png',
    'S:data/product5.png',
    'S:data/ttgo.jpg'
]

for img in image_files:
    img_symbol.set_src(img)
    img_symbol.align(lv.ALIGN.CENTER, 0, 0)
    gc.collect()
    time.sleep(1)
