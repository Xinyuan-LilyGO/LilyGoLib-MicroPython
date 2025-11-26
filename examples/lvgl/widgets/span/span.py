'''
 * @file      span.py
 * @license   MIT
 * @copyright Copyright (c) 2025  Shenzhen Xinyuan Electronic Technology Co., Ltd
 * @date      2025-10-15
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

scrn = lv.screen_active()
scrn.set_style_bg_color(lv.color_hex(0x000000), 0)

container_style = lv.style_t()
container_style.init()
container_style.set_border_width(1)
container_style.set_border_color(lv.palette_main(lv.PALETTE.ORANGE))
container_style.set_pad_all(2)

container = lv.obj(scrn)
container.set_size(300, 120)
container.center()
container.add_style(container_style, 0)
container.set_flex_flow(lv.FLEX_FLOW.COLUMN)
container.set_flex_align(lv.FLEX_ALIGN.START, lv.FLEX_ALIGN.START, lv.FLEX_ALIGN.START)

label1 = lv.label(container)
label1.set_text("China is a beautiful country.")
label1_style = lv.style_t()
label1_style.init()
label1_style.set_text_color(lv.palette_main(lv.PALETTE.RED))
label1_style.set_text_decor(lv.TEXT_DECOR.UNDERLINE)
label1_style.set_text_opa(lv.OPA._50)
label1.add_style(label1_style, 0)

label2 = lv.label(container)
label2.set_text("good good study, day day up.")
label2_style = lv.style_t()
label2_style.init()
label2_style.set_text_color(lv.palette_main(lv.PALETTE.GREEN))
try:
    label2_style.set_text_font(lv.font_montserrat_24)
except:
    pass
label2.add_style(label2_style, 0)

label3 = lv.label(container)
label3.set_text("LVGL is an open-source graphics library.")
label3_style = lv.style_t()
label3_style.init()
label3_style.set_text_color(lv.palette_main(lv.PALETTE.BLUE))
label3.add_style(label3_style, 0)

label4 = lv.label(container)
label4.set_text("the boy no name.")
label4_style = lv.style_t()
label4_style.init()
label4_style.set_text_color(lv.palette_main(lv.PALETTE.GREEN))
label4_style.set_text_decor(lv.TEXT_DECOR.UNDERLINE)
try:
    label4_style.set_text_font(lv.font_montserrat_20)
except:
    pass
label4.add_style(label4_style, 0)

label5 = lv.label(container)
label5.set_text("I have a dream that hope to come true.")
label5_style = lv.style_t()
label5_style.init()
label5_style.set_text_decor(lv.TEXT_DECOR.STRIKETHROUGH)
label5.add_style(label5_style, 0)

import task_handler
task_handler.TaskHandler(33)