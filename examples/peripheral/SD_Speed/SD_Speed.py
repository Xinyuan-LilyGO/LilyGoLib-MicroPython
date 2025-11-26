'''
 * @file      SD_Speed.py
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

TEST_FILE_SIZE = 1024 * 1024  # 1MB
BLOCK_SIZE = 512

NFC_CS = 39       # NFC Chip Select
LORA_CS = 36      # LoRa Chip Select
NFC_RST = 21      # NFC Reset
LORA_RST = 47     # LoRa Reset
SD_CS = 21
SPI_MOSI = 34
SPI_MISO = 33
SPI_SCK = 35

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
label.set_text('SD Speed test')
label.set_style_text_font(lv.font_montserrat_16, 0)
label.center()
lv.task_handler()

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

def test_write_speed():
    print("Starting write speed test...")
    try:
        start_time = time.ticks_ms()
        
        with open("/sd/testfile.bin", "wb") as test_file:
            for i in range(0, TEST_FILE_SIZE, BLOCK_SIZE):
                buffer = bytearray(BLOCK_SIZE)
                for j in range(BLOCK_SIZE):
                    buffer[j] = (i + j) & 0xFF
                test_file.write(buffer)
        
        end_time = time.ticks_ms()
        write_time = (end_time - start_time) / 1000.0
        write_speed = TEST_FILE_SIZE / (write_time * 1024.0)
        
        print("Write time: {:.2f} s".format(write_time))
        print("Write speed: {:.2f} KB/s".format(write_speed))
        return True, write_time, write_speed
        
    except Exception as e:
        print("Write speed test failed:", e)
        return False, 0, 0

def test_read_speed():
    print("Starting read speed test...")
    try:
        start_time = time.ticks_ms()
        
        with open("/sd/testfile.bin", "rb") as test_file:
            buffer = bytearray(BLOCK_SIZE)
            for i in range(0, TEST_FILE_SIZE, BLOCK_SIZE):
                test_file.readinto(buffer)
        
        end_time = time.ticks_ms()
        read_time = (end_time - start_time) / 1000.0
        read_speed = TEST_FILE_SIZE / (read_time * 1024.0)
        
        print("Read time: {:.2f} s".format(read_time))
        print("Read speed: {:.2f} KB/s".format(read_speed))
        return True, read_time, read_speed
        
    except Exception as e:
        print("Read speed test failed:", e)
        return False, 0, 0

def get_sd_card_info():
    try:
        statvfs = os.statvfs("/sd")
        total_size = (statvfs[0] * statvfs[2]) / (1024 * 1024)
        
        card_type = "UNKNOWN"
        if total_size > 4096:
            card_type = "SDHC"
        elif total_size > 0:
            card_type = "SDSC"
            
        return True, total_size, card_type
    except Exception as e:
        print("Failed to get SD card info:", e)
        return False, 0, "UNKNOWN"

def run_sd_speed_test():
    info_success, total_size, card_type = get_sd_card_info()
    
    if info_success:
        print("SD Card Type:", card_type)
        print("SD Card Size: {:.0f}MB".format(total_size))
        
        time.sleep(1)
        label.set_text("SD Size :{:.0f}MB".format(total_size))
        label.center()
        
        write_success, write_time, write_speed = test_write_speed()
        
        write_label = lv.label(scrn)
        write_label.set_style_text_font(lv.font_montserrat_16, 0)
        if write_success:
            write_text = "Write block use {:.2f} s\nWrite Speed is {:.2f} KB/s".format(write_time, write_speed)
            write_label.set_text(write_text)
        else:
            write_label.set_text("Write speed test Failed")
        write_label.align_to(label, lv.ALIGN.OUT_BOTTOM_MID, 0, 10)
        lv.task_handler()

        read_success, read_time, read_speed = test_read_speed()

        read_label = lv.label(scrn)
        read_label.set_style_text_font(lv.font_montserrat_16, 0)
        if read_success:
            read_text = "Read block use {:.2f} s\nRead Speed is {:.2f} KB/s".format(read_time, read_speed)
            read_label.set_text(read_text)
        else:
            read_label.set_text("Read speed test Failed")
        read_label.align_to(write_label, lv.ALIGN.OUT_BOTTOM_MID, 0, 10)
        lv.task_handler()

        try:
            os.remove("/sd/testfile.bin")
            print("Test file cleaned up")
        except:
            print("Failed to clean up test file")
            
    else:
        label.set_text("SD Mount Failed!")
        label.center()

if install_sd():
    print("SD initialization successful.")
    time.sleep(1)
    run_sd_speed_test()
else:
    print("SD initialization failed.")
    label.set_text("SD Mount Failed!")
    label.center()

import task_handler
task_handler.TaskHandler(33)


