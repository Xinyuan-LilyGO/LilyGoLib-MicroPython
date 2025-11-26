'''
 * @file      calendar.py
 * @license   MIT
 * @copyright Copyright (c) 2025  Shenzhen Xinyuan Electronic Technology Co., Ltd
 * @date      2025-10-11
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

scr = lv.screen_active()
# scr.set_style_bg_color(lv.color_hex(0x000000), 0)

#创建日历对象
calendar = lv.calendar(scr)
calendar.set_style_bg_color(lv.color_hex(0x000000), 0)
#设置大小
calendar.set_size(250, 220)
#居中显示
calendar.center()

calendar.set_today_date(2025, 10, 10)

shown_date = lv.calendar_date_t()
shown_date.year = 2025
shown_date.month = 10

# calendar.add_header_arrow()

calendar.add_header_dropdown()
# 设置年份列表（2020-2030）
year_list = "\n".join([str(y) for y in range(2020, 2031)])
calendar.header_dropdown_set_year_list(year_list)

import task_handler
task_handler.TaskHandler(33)
