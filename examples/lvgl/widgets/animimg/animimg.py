'''
 * @file      animimg.PY
 * @license   MIT
 * @copyright Copyright (c) 2025  Shenzhen Xinyuan Electronic Technology Co., Ltd
 * @date      2025-11-11
'''
from machine import SPI, Pin, I2C
import lcd_bus
import st7796
import lvgl as lv
import vibration
import task_handler

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

backlight_pin = Pin(42, Pin.OUT)
backlight_pin.value(1)

def read_bin_file(filename):
    try:
        with open(filename, 'rb') as f:
            return f.read()
    except:
        return None

animimg001_map = read_bin_file('animimg001_map.bin')
animimg002_map = read_bin_file('animimg002_map.bin')  
animimg003_map = read_bin_file('animimg003_map.bin')

def create_image_dsc(data, width, height, stride):
    img_dsc = lv.image_dsc_t()
    img_dsc.header.w = width
    img_dsc.header.h = height
    img_dsc.header.stride = stride
    img_dsc.header.cf = lv.COLOR_FORMAT.ARGB8888
    img_dsc.data = data
    img_dsc.data_size = len(data)
    return img_dsc

animimg001 = create_image_dsc(animimg001_map, 130, 170, 520) # w, h, stride
animimg002 = create_image_dsc(animimg002_map, 130, 170, 520)
animimg003 = create_image_dsc(animimg003_map, 130, 170, 520)

anim_imgs = [animimg001, animimg002, animimg003]

scrn = lv.screen_active()
scrn.set_style_bg_color(lv.color_hex(0x000000), 0)

animimg0 = lv.animimg(scrn)
animimg0.center()
animimg0.set_src(anim_imgs, 3)
animimg0.set_duration(1000)
animimg0.set_repeat_count(65535)
animimg0.start()

task_handler.TaskHandler(33)