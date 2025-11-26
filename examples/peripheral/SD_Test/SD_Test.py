'''
 * @file      SD_Test.py
 * @license   MIT
 * @copyright Copyright (c) 2025  ShenZhen XinYuan Electronic Technology Co., Ltd
 * @date      2025-10-24
'''
from machine import SPI, Pin, I2C, SDCard
import sys
import lcd_bus
import st7796
import lvgl as lv
from micropython import const
import vibration
import _thread
import os
import time

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

label = lv.label(scrn)
label.set_text('SD Test example')
label.set_style_text_font(lv.font_montserrat_16, 0)
label.center()
lv.task_handler()

NFC_CS = 39       # NFC Chip Select
LORA_CS = 36      # LoRa Chip Select
NFC_RST = 21      # NFC Reset
LORA_RST = 47     # LoRa Reset
SD_CS = 21
SPI_MOSI = 34
SPI_MISO = 33
SPI_SCK = 35

def init_share_spi_pins():
    share_spi_bus_devices_cs_pins = [
        NFC_RST,
        NFC_CS,
        LORA_CS,
        SD_CS,
        LORA_RST
    ]
    for pin_num in share_spi_bus_devices_cs_pins:
        p = Pin(pin_num, Pin.OUT)
        p.value(1)

def install_sd():
    try:
        init_share_spi_pins()

        spi_bus = SPI.Bus(
            host=1,
            sck=SPI_SCK,
            mosi=SPI_MOSI,
            miso=SPI_MISO
        )

        sd = SDCard(spi_bus=spi_bus, cs=SD_CS)

        os.mount(sd, "/sd")
        statvfs = os.statvfs("/sd")
        total_size = (statvfs[0] * statvfs[2]) / (1024 * 1024)
        print("SD Card mounted at /sd, size: {:.2f} MB".format(total_size))

        return True

    except Exception as e:
        print("Failed to detect or mount SD Card:", e)
        return False


def listDir(fs_path, levels):
    print("Listing directory: {}".format(fs_path))
    try:
        for entry in os.ilistdir(fs_path):
            name = entry[0]
            is_dir = entry[1] == 0x4000
            if is_dir:
                print("  DIR : {}".format(name))
                if levels > 0:
                    listDir(fs_path + "/" + name, levels - 1)
            else:
                size = os.stat(fs_path + "/" + name)[6]
                print("  FILE: {}  SIZE: {}".format(name, size))
    except:
        print("Failed to open directory")

def createDir(path):
    print("Creating Dir: {}".format(path))
    try:
        os.mkdir(path)
        print("Dir created")
    except:
        print("mkdir failed")

def removeDir(path):
    print("Removing Dir: {}".format(path))
    try:
        os.rmdir(path)
        print("Dir removed")
    except:
        print("rmdir failed")

def readFile(path):
    print("Reading file: {}".format(path))
    try:
        with open(path, "r") as f:
            data = f.read()
            print("Read from file: {}".format(data), end="")
    except:
        print("Failed to open file for reading")

def writeFile(path, message):
    print("Writing file: {}".format(path))
    try:
        with open(path, "w") as f:
            f.write(message)
        print("File written")
    except:
        print("Write failed")

def appendFile(path, message):
    print("Appending to file: {}".format(path))
    try:
        with open(path, "a") as f:
            f.write(message)
        print("Message appended")
    except:
        print("Append failed")

def renameFile(path1, path2):
    print("Renaming file {} to {}".format(path1, path2))
    try:
        os.rename(path1, path2)
        print("File renamed")
    except:
        print("Rename failed")

def deleteFile(path):
    print("Deleting file: {}".format(path))
    try:
        os.remove(path)
        print("File deleted")
    except:
        print("Delete failed")

def testFileIO(path):
    buf = bytearray(512)

    try:
        f = open(path, "r+b")
    except:
        print("Failed to open file for reading")
        return

    size = os.stat(path)[6]
    start = time.ticks_ms()
    remain = size
    while remain > 0:
        chunk = min(remain, 512)
        f.readinto(buf)
        remain -= chunk
    elapsed = time.ticks_diff(time.ticks_ms(), start)
    print("{} bytes read for {} ms".format(size, elapsed))
    f.close()

    try:
        f = open(path, "w+b")
    except:
        print("Failed to open file for writing")
        return

    start = time.ticks_ms()
    for _ in range(2048):
        f.write(buf)
    elapsed = time.ticks_diff(time.ticks_ms(), start)
    print("{} bytes written for {} ms".format(2048 * 512, elapsed))
    f.close()

if install_sd():
    print("SD initialization successful.")
    time.sleep(1)

    listDir("/sd", 0)
    createDir("/sd/mydir")
    listDir("/sd", 0)
    removeDir("/sd/mydir")
    listDir("/sd", 2)

    writeFile("/sd/hello.txt", "Hello ")
    appendFile("/sd/hello.txt", "World!\n")
    readFile("/sd/hello.txt")

    deleteFile("/sd/foo.txt")
    renameFile("/sd/hello.txt", "/sd/foo.txt")
    readFile("/sd/foo.txt")

    testFileIO("/sd/test.txt")

    statvfs = os.statvfs("/sd")
    total = (statvfs[1] * statvfs[2]) // (1024 * 1024)
    used = total - (statvfs[1] * statvfs[3]) // (1024 * 1024)
    print("Total space: {}MB".format(total))
    print("Used space: {}MB".format(used))

    os.umount("/sd")
else:
    print("SD initialization failed.")
    label.set_text("SD Mount Failed!")

import task_handler
task_handler.TaskHandler(33)