'''
 * @file      chart.py
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
import random

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

main_cont = lv.obj(scrn)
main_cont.set_size(250, 150)
main_cont.set_style_bg_color(lv.color_hex(0x000000), 0)
main_cont.center()

wrapper = lv.obj(main_cont)
wrapper.remove_style_all()
wrapper.set_size(600, 150)
wrapper.set_flex_flow(lv.FLEX_FLOW.COLUMN)
 
chart = lv.chart(wrapper)
chart.set_style_bg_color(lv.color_hex(0x000000), 0)
chart.set_width(600)
chart.set_height(100)
chart.set_type(lv.chart.TYPE.BAR)
chart.set_point_count(12)
chart.set_style_radius(0, 0)

scale_bottom = lv.scale(wrapper)
scale_bottom.set_mode(lv.scale.MODE.HORIZONTAL_BOTTOM)
scale_bottom.set_size(600, 25)
scale_bottom.set_total_tick_count(13)
scale_bottom.set_major_tick_every(1)
scale_bottom.set_style_translate_x(27, 0)

months = ["Jan", "Febr", "March", "Apr", "May", "Jun", "July", "Aug", "Sept", "Oct", "Nov", "Dec"]
scale_bottom.set_text_src(months)

ser1 = chart.add_series(lv.palette_lighten(lv.PALETTE.GREEN, 2), lv.chart.AXIS.PRIMARY_Y)
ser2 = chart.add_series(lv.palette_darken(lv.PALETTE.GREEN, 2), lv.chart.AXIS.PRIMARY_Y)

data1 = [random.randint(10, 60) for _ in range(12)]
data2 = [random.randint(50, 90) for _ in range(12)]

for i in range(12):
    chart.set_next_value(ser1, data1[i])
    chart.set_next_value(ser2, data2[i])

import task_handler
task_handler.TaskHandler(33)