import time
from machine import SPI, Pin, I2C, UART
import sys
import lcd_bus
import st7796
import lvgl as lv
from micropython import const
import vibration
import _thread
import task_handler
import re

GPS_TX = 4      # GPS TX → ESP32 RX
GPS_RX = 12     # GPS RX → ESP32 TX
GPS_PPS = 13

pps = Pin(GPS_PPS, Pin.IN)

uart = UART(1, baudrate=9600, tx=Pin(GPS_RX), rx=Pin(GPS_TX))

rx_chars = 0
last_fix_time = time.ticks_ms()

gps_data = {
    "lat": None,
    "lng": None,
    "sats": 0,
    "hdop": 0,
    "alt": 0,
    "speed": 0,
    "date": (0, 0, 0),
    "time": (0, 0, 0),
    "valid": False,
}

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
time.sleep(1)
backlight_pin = Pin(42, Pin.OUT)
backlight_pin.value(1)

scrn = lv.screen_active()
scrn.set_style_bg_color(lv.color_hex(0x000000), 0)

label = lv.label(scrn)
label.set_text('UBlox GPS factory succeeded')
label.center()

task_handler.TaskHandler(33)

def parse_latlng(v, d):
    if v == "":
        return None
    deg = int(v[:2])
    mins = float(v[2:])
    sign = -1 if d in ("S", "W") else 1
    return sign * (deg + mins / 60)

def parse_nmea(line):
    global gps_data, last_fix_time

    parts = line.split(",")
    if line.startswith("$GPGGA"):
        if len(parts[1]) >= 6:
            hh = int(parts[1][0:2])
            mm = int(parts[1][2:4])
            ss = int(parts[1][4:6])
            gps_data["time"] = (hh, mm, ss)

        gps_data["lat"] = parse_latlng(parts[2], parts[3])
        gps_data["lng"] = parse_latlng(parts[4], parts[5])
        gps_data["sats"] = int(parts[7] or 0)
        gps_data["hdop"] = float(parts[8] or 0)
        gps_data["alt"] = float(parts[9] or 0)

        gps_data["valid"] = gps_data["sats"] >= 3
        if gps_data["valid"]:
            last_fix_time = time.ticks_ms()

    elif line.startswith("$GPRMC"):
        if parts[2] == "A":
            gps_data["valid"] = True
            last_fix_time = time.ticks_ms()

        if len(parts[9]) == 6:
            dd = int(parts[9][0:2])
            mm = int(parts[9][2:4])
            yy = int(parts[9][4:6]) + 2000
            gps_data["date"] = (yy, mm, dd)

        gps_data["lat"] = parse_latlng(parts[3], parts[4])
        gps_data["lng"] = parse_latlng(parts[5], parts[6])

        gps_data["speed"] = float(parts[7] or 0) * 1.852

print("FullExample.py (MicroPython)")
print("An extensive example of many interesting GPS features")
print()
print("Sats HDOP  Latitude   Longitude   Fix  Date       Time     Date Alt    Course Speed Card  Distance Course Card  Chars Sentences Checksum")
print("           (deg)      (deg)       Age                      Age  (m)    --- from GPS ----  ---- to London  ----  RX    RX        Fail")
print("----------------------------------------------------------------------------------------------------------------------------------------")

buffer = b""

while True:
    if uart.any():
        b = uart.read(1)
        
        if not b:
            continue
        rx_chars += 1

        if b == b'\n':
            try:
                line = buffer.decode("latin-1").strip()
                
            except:
                buffer = b""
                continue

            if line.startswith("$"):
                parse_nmea(line)

            buffer = b""
        else:
            buffer += b

    age = time.ticks_diff(time.ticks_ms(), last_fix_time)

    year, month, day = gps_data["date"]
    hh, mm, ss = gps_data["time"]

    lat = gps_data["lat"] or 0
    lng = gps_data["lng"] or 0
    sats = gps_data["sats"]
    hdop = gps_data["hdop"]
    alt = gps_data["alt"]
    speed = gps_data["speed"]

    label.set_text(f"Fix: {age}\nSats: {sats}\nHDOP: {hdop}\nLat: {lat}\nLon: {lng}\nDate: {year}/{month}/{day}\nTime: {hh}/{mm}/{ss}\nAlt: {alt}\nSpeed: {speed}\nRX: {rx_chars}")
    label.center()
    
    print("Fix:%u  Sats:%u  HDOP:%.1f  Lat:%.5f  Lon:%.5f   Date:%d/%d/%d   Time:%d/%d/%d  Alt:%.2f m   Speed:%.2f  RX:%u" %
        (age, sats, hdop, lat, lng, year, month, day, hh, mm, ss, alt, speed, rx_chars))

    time.sleep(1)