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

GPS_TX = 4      # GPS TX → ESP32 RX
GPS_RX = 12     # GPS RX → ESP32 TX
GPS_PPS = 13    

pps = Pin(GPS_PPS, Pin.IN)
baud_list = [38400, 57600, 115200, 9600]

uart = None

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

def try_init_gps():
    global uart
    retry = 4

    while retry > 0:
        for b in baud_list:
            print("Try use {} baud".format(b))
            uart = UART(1, baudrate=b, tx=Pin(GPS_RX), rx=Pin(GPS_TX), timeout=50)
            time.sleep(0.1)
            
            uart.write(b"$PUBX,00*33\r\n")
            time.sleep(0.1)

            data = uart.read()
            if data:
                print("UBlox GPS init succeeded @ {} baud".format(b))
                return True

        retry -= 1

    print("Warning: Failed to find UBlox GPS Module")
    return False

def gps_factory():
    cmd = b"$PUBX,41,1,0007,0003,9600,0*25\r\n"  # UBlox factory default example
    uart.write(cmd)
    time.sleep(0.2)

    resp = uart.read()
    if resp:
        print("UBlox GPS factory succeeded")
        return True
    else:
        print("Warning: Failed to factory UBlox GPS")
        return False


print("GPS Factory Example (MicroPython)")

if try_init_gps():
    gps_factory()
else:
    print("GPS init failed, exit.")
    while True:
        time.sleep(1)

print("Start reading GPS data...\n")

while True:
    if uart.any():
        data = uart.read()
        if data:
            try:
                print(data.decode("utf-8"))
            except UnicodeError:
                print(data.decode("latin-1"))
    time.sleep(0.01)