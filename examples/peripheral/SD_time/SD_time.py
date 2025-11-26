'''
 * @file      SD_time.py
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
import network
import ntptime
import time

# WiFi credentials
SSID = "LilyGo-AABB"
PASSWORD = "xinyuandianzi"

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
label.set_text('SD Test Example')
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

def fmt_time(t_tuple):
    # t_tuple from time.localtime() -> (year,mon,mday,hour,min,sec,weekday,yday)
    try:
        year = t_tuple[0]
        mon = t_tuple[1]
        mday = t_tuple[2]
        hour = t_tuple[3]
        minute = t_tuple[4]
        sec = t_tuple[5]
        return "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(year, mon, mday, hour, minute, sec)
    except:
        return "1970-01-01 00:00:00"

print("")
print("")
print("Connecting to ")
print(SSID)

wlan = network.WLAN(network.STA_IF)
if not wlan.active():
    wlan.active(True)
wlan.connect(SSID, PASSWORD)

while not wlan.isconnected():
    time.sleep(0.5)
    print(".", end="")

print("WiFi connected")
try:
    ip = wlan.ifconfig()[0]
    print("IP address: ")
    print(ip)
except:
    print("IP address: ")
    print("0.0.0.0")

print("Contacting Time Server")

timezone = 8
daysavetime = 0 

tz_offset_seconds = 3600 * timezone + 3600 * daysavetime

try:
    # set RTC to UTC from NTP
    ntptime.settime()  # sets RTC to UTC
    print("NTP time synchronized successfully")
except Exception as e:
    print("NTP sync failed:", e)
    # ntp may fail on some ports; continue anyway
    pass

# wait a bit, then print local time like Arduino
time.sleep(2)
try:
    utc = time.localtime()
    print("UTC time: {}".format(fmt_time(utc)))

    secs = time.mktime(utc) + tz_offset_seconds
    local = time.localtime(secs)
    
    print("\nNow is : {}".format(fmt_time(local)))
    print("")
except Exception as e:
    print("Time conversion error:", e)
    print("\nNow is : 1970-01-01 00:00:00\n")

# Try sd.card_type() or sd.info(); otherwise fallback to UNKNOWN
try:
    sd_card_type = None
    # common MicroPython SDCard APIs vary; try some heuristics
    if hasattr(sd, "card_type"):
        sd_card_type = sd.card_type()
    elif hasattr(sd, "info"):
        info = sd.info()
        # some implementations return tuple where 0 is type
        if isinstance(info, (tuple, list)) and len(info) > 0:
            sd_card_type = info[0]
    # Map to Arduino labels:
    # We'll assume 1->MMC, 2->SDSC, 3->SDHC; else UNKNOWN
    print("SD Card Type: ", end="")
    if sd_card_type == 1:
        print("MMC")
    elif sd_card_type == 2:
        print("SDSC")
    elif sd_card_type == 3:
        print("SDHC")
    else:
        print("UNKNOWN")
except Exception:
    print("SD Card Type: UNKNOWN")

# Card size: try to compute from statvfs if possible
try:
    statvfs = os.statvfs("/sd")
    # statvfs returns: (bsize, frsize, blocks, bfree, bavail, files, ffree, favail, fsid)
    # total bytes = frsize * blocks or bsize * blocks depending on port; use [1]*[2] fallback
    total_bytes = (statvfs[0] * statvfs[2])
    card_size_mb = total_bytes // (1024 * 1024)
    print("SD Card Size: {}MB".format(card_size_mb))
except Exception:
    # fallback to previously computed value if available in your install_sd (you printed it earlier)
    print("SD Card Size: UNKNOWN")

def listDir(path, levels):
    print("Listing directory: {}".format(path))
    try:
        for entry in os.ilistdir(path):
            name = entry[0]
            mode = entry[1]
            size = entry[3]
            is_dir = (mode & 0x4000) != 0
            if is_dir:
                print("  DIR : {}".format(name))
                # try to get last write time if possible
                try:
                    st = os.stat(path + "/" + name)
                    mtime = st[8] if len(st) > 8 else None
                    if mtime:
                        t = time.localtime(mtime + tz_offset_seconds)
                        print("  LAST WRITE: {}".format(fmt_time(t)))
                    else:
                        print("  LAST WRITE: 1970-01-01 00:00:00")
                except:
                    print("  LAST WRITE: 1970-01-01 00:00:00")
                if levels:
                    listDir(path + "/" + name, levels - 1)
            else:
                print("  FILE: {}  SIZE: {}".format(name, size))
                try:
                    st = os.stat(path + "/" + name)
                    mtime = st[8] if len(st) > 8 else None
                    if mtime:
                        t = time.localtime(mtime + tz_offset_seconds)
                        print("  LAST WRITE: {}".format(fmt_time(t)))
                    else:
                        print("  LAST WRITE: 1970-01-01 00:00:00")
                except:
                    print("  LAST WRITE: 1970-01-01 00:00:00")
    except Exception as e:
        print("Failed to open directory:", e)

def createDir(path):
    print("Creating Dir: {}".format(path))
    try:
        os.mkdir(path)
        print("Dir created")
    except Exception as e:
        print("mkdir failed:", e)

def removeDir(path):
    print("Removing Dir: {}".format(path))
    try:
        os.rmdir(path)
        print("Dir removed")
    except Exception as e:
        print("rmdir failed:", e)

def readFile(path):
    print("Reading file: {}".format(path))
    try:
        with open(path, "rb") as f:
            print("Read from file: ", end="")
            # write bytes to stdout like Arduino Serial.write
            data = f.read()
            try:
                # try decode safe
                print(data.decode('utf-8'), end="")
            except:
                # raw bytes fallback: print repr without extra newlines
                import ubinascii
                print(ubinascii.hexlify(data).decode(), end="")
    except Exception as e:
        print("Failed to open file for reading:", e)
    print("")  # ensure newline

def writeFile(path, message):
    print("Writing file: {}".format(path))
    try:
        with open(path, "w") as f:
            f.write(message)
        print("File written")
    except Exception as e:
        print("Write failed:", e)

def appendFile(path, message):
    print("Appending to file: {}".format(path))
    try:
        with open(path, "a") as f:
            f.write(message)
        print("Message appended")
    except Exception as e:
        print("Append failed:", e)

def renameFile(path1, path2):
    print("Renaming file {} to {}".format(path1, path2))
    try:
        os.rename(path1, path2)
        print("File renamed")
    except Exception as e:
        print("Rename failed:", e)

def deleteFile(path):
    print("Deleting file: {}".format(path))
    try:
        os.remove(path)
        print("File deleted")
    except Exception as e:
        print("Delete failed:", e)

def testFileIO(path):
    # try to match Arduino behavior: read file fully and measure, then write 2048*512 bytes and measure
    try:
        f = open(path, "rb")
    except Exception as e:
        print("Failed to open file for reading:", e)
        return

    buf = bytearray(512)
    try:
        f.seek(0, 2)
        flen = f.tell()
        f.seek(0)
        start = time.ticks_ms()
        remain = flen
        while remain > 0:
            toread = 512 if remain >= 512 else remain
            data = f.read(toread)
            remain -= len(data)
        elapsed = time.ticks_diff(time.ticks_ms(), start)
        print("{} bytes read for {} ms".format(flen, elapsed))
        f.close()
    except Exception as e:
        print("Failed to read file for speed test:", e)
        f.close()
        return

    try:
        f = open(path, "wb")
    except Exception as e:
        print("Failed to open file for writing:", e)
        return

    try:
        start = time.ticks_ms()
        for i in range(2048):
            f.write(buf)
        elapsed = time.ticks_diff(time.ticks_ms(), start)
        print("{} bytes written for {} ms".format(2048 * 512, elapsed))
        f.close()
    except Exception as e:
        print("Failed to write file for speed test:", e)
        try:
            f.close()
        except:
            pass

if install_sd():
    print("SD initialization successful.")
    time.sleep(1)    
else:
    print("SD initialization failed.")
    label.set_text("SD Mount Failed!")
    
listDir("/sd", 0)
removeDir("/sd/mydir")
createDir("/sd/mydir")
deleteFile("/sd/hello.txt")
writeFile("/sd/hello.txt", "Hello ")
appendFile("/sd/hello.txt", "World!\n")
listDir("/sd", 0)
    
import task_handler
task_handler.TaskHandler(33)