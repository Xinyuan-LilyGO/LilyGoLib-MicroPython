from machine import SPI, Pin, I2C
import sys
import lcd_bus
import st7796
import lvgl as lv
from micropython import const
import vibration
import _thread
import gifImage
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
except Exception as e:
    print("Display init failed:", e)
_thread.start_new_thread(vibrate_motor, ())
backlight_pin = Pin(42, Pin.OUT)
backlight_pin.value(1)
time.sleep(1)



scrn = lv.screen_active()
scrn.set_style_bg_color(lv.color_hex(0x000000), 0)


image_dsc = lv.image_dsc_t(
    {
        "header": {
            "magic": lv.IMAGE_HEADER_MAGIC,
            "cf": lv.COLOR_FORMAT.RAW_ALPHA,
            "flags": 0,
            "w": 0,
            "h": 0,
            "stride": 0
        },
        "data_size": len(gifImage.image_map),
        "data": gifImage.image_map
    }
)

img = lv.gif(scrn)
lv.gif.set_src(img, image_dsc)
img.center()

import task_handler
task_handler.TaskHandler(33)
