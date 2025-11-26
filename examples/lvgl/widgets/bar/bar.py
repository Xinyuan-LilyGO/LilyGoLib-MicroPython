'''
 * @file      bar.py
 * @license   MIT
 * @copyright Copyright (c) 2025  Shenzhen Xinyuan Electronic Technology Co., Ltd
 * @date      2025-10-9
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
    spi_bus = SPI.Bus(host=1, mosi=34, miso=33, sck=35)
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
time.sleep(1)
scrn = lv.screen_active()
scrn.set_style_bg_color(lv.color_hex(0x000000), 0)

class BarAnim:
    def __init__(self, bar_obj, label_obj):
        self.bar = bar_obj
        self.label = label_obj
        self.value = 0
        self.direction = 1
        self.timer = lv.timer_create(self.update, 50, None)
    
    def update(self, timer):
        self.value += self.direction
        if self.value >= 100:
            self.value = 100
            self.direction = -1
        elif self.value <= 0:
            self.value = 0
            self.direction = 1
        
        self.bar.set_value(self.value, True)
        self.label.set_text(f"{int(self.value)}%")
        self.update_label_position()
    
    def update_label_position(self):
        bar_x = self.bar.get_x()
        bar_y = self.bar.get_y()
        bar_width = self.bar.get_width()
        bar_height = self.bar.get_height()

        progress_pixels = (self.value / 100) * bar_width
        text_width = 25
        
        if progress_pixels - text_width < 0:
            label_x = bar_x + progress_pixels + 5 
        else:
            label_x = bar_x + progress_pixels - text_width - 5
        
        label_y = bar_y + (bar_height // 2) - 10 
        
        self.label.set_pos(int(label_x), int(label_y))


def lv_example_bar_anim():
    bar = lv.bar(scrn)
    bar.set_size(200, 20)
    bar.set_range(0, 100)
    bar.set_value(0, False)
    bar.center()

    style_bg = lv.style_t()
    style_bg.init()
    style_bg.set_bg_color(lv.palette_main(lv.PALETTE.BLUE_GREY))
    style_bg.set_bg_opa(lv.OPA.COVER)
    style_bg.set_border_width(0)
    style_bg.set_radius(10)
    style_bg.set_pad_all(0)

    style_indic = lv.style_t()
    style_indic.init()
    style_indic.set_bg_color(lv.palette_main(lv.PALETTE.BLUE))
    style_indic.set_bg_grad_color(lv.palette_main(lv.PALETTE.CYAN))
    style_indic.set_bg_grad_dir(lv.GRAD_DIR.HOR)
    style_indic.set_radius(10)
    style_indic.set_pad_all(0)
    style_indic.set_border_width(0)

    bar.add_style(style_bg, lv.PART.MAIN)
    bar.add_style(style_indic, lv.PART.INDICATOR)

    label = lv.label(scrn)
    label.set_text("0%")
    label.set_width(30)
    
    style_label = lv.style_t()
    style_label.init()
    style_label.set_text_color(lv.color_hex(0x000000))
    
    label.add_style(style_label, lv.PART.MAIN)
    bar.align(lv.ALIGN.CENTER, 0, 0)

    BarAnim(bar, label)


lv_example_bar_anim()

import task_handler
task_handler.TaskHandler(33)