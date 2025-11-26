'''
 * @file      tabview.py
 * @license   MIT
 * @copyright Copyright (c) 2025  Shenzhen Xinyuan Electronic Technology Co., Ltd
 * @date      2025-10-16
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

# Create a Tab view object
tabview = lv.tabview(lv.screen_active())
tabview.set_pos(0,45)
# Add 3 tabs
tab1 = tabview.add_tab("Tab 1")
tab2 = tabview.add_tab("Tab 2") 
tab3 = tabview.add_tab("Tab 3")

# Add content to the tabs
label1 = lv.label(tab1)
label1.set_text("This the first tab\n\n"
                "If the content\n"
                "of a tab\n"
                "becomes too\n"
                "longer\n"
                "than the\n"
                "container\n"
                "then it\n"
                "automatically\n"
                "becomes\n"
                "scrollable.\n"
                "\n"
                "\n"
                "\n"
                "Can you see it?")

label2 = lv.label(tab2)
label2.set_text("Second tab")

label3 = lv.label(tab3) 
label3.set_text("Third tab")

try:
    label3.scroll_to_view(lv.ANIM.ON)
except:
    try:
        label3.scroll_to_view(lv.ANIM_ON)
    except:
        try:
            label3.scroll_to_view(True)
        except:
            pass

import task_handler
task_handler.TaskHandler(33)