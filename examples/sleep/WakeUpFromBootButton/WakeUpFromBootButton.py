'''
 * @file      WakeUpFromBootButton.py
 * @license   MIT
 * @copyright Copyright (c) 2025  Shenzhen Xinyuan Electronic Technology Co., Ltd
 * @date      2025-09-25
 * @note      You need to copy the code to main.py and upload it to the device to run
'''
from machine import SPI, I2C, Pin, deepsleep, reset_cause
from machine import PWRON_RESET, HARD_RESET, WDT_RESET, DEEPSLEEP_RESET, SOFT_RESET
import machine
import time
import sys
import lcd_bus
import st7796
import lvgl as lv
import vibration
import esp32
import _thread
import task_handler

i2c = I2C(0, scl=Pin(2), sda=Pin(3), freq=400000)
vb = vibration.vibrationMotor(i2c)
reason = None
sleep_status = False

def scan_i2c_devices():
    print("Listing directory: /")
    print("    " + " ".join("{:2x}".format(x) for x in range(16)))
    devices = i2c.scan()
    for i in range(0, 128, 16):
        print("{:02x}:".format(i), end=" ")
        for j in range(16):
            addr = i + j
            if addr in devices:
                print("{:02X}".format(addr), end=" ")
            else:
                print("--", end=" ")
        print()

# print the cause of the last reset
def print_reset_cause():
    global reason
    rc = reset_cause() # Get reset cause

    # Try to obtain the wake reason (prefer machine.wake_reason(), fallback to esp32.wake_reason())
    wake_tuple = None
    wake_cause = None
    wake_gpio = None
    try:
        wake_tuple = machine.wake_reason()
    except Exception:
        try:
            wake_tuple = esp32.wake_reason()
        except Exception:
            wake_tuple = None

    # Normalize wake_tuple into (wake_cause, wake_gpio)
    if wake_tuple is not None:
        # Debug: print raw wake tuple so you can see what your firmware returns
        # print("raw wake_reason:", wake_tuple)
        if isinstance(wake_tuple, tuple):
            if len(wake_tuple) >= 1:
                wake_cause = wake_tuple[0]
            if len(wake_tuple) >= 2:
                wake_gpio = wake_tuple[1]
        elif isinstance(wake_tuple, int):
            wake_cause = wake_tuple

    # Build a robust mapping (try esp32 constants, machine constants, then numeric fallbacks)
    wake_map = {}
    # esp32 constants (if present)
    try:
        if hasattr(esp32, 'ESP_SLEEP_WAKEUP_EXT0'):
            wake_map[getattr(esp32, 'ESP_SLEEP_WAKEUP_EXT0')] = "Wakeup caused by external signal using RTC_IO"
        if hasattr(esp32, 'ESP_SLEEP_WAKEUP_EXT1'):
            wake_map[getattr(esp32, 'ESP_SLEEP_WAKEUP_EXT1')] = "Wakeup caused by external signal using RTC_CNTL"
        if hasattr(esp32, 'ESP_SLEEP_WAKEUP_TIMER'):
            wake_map[getattr(esp32, 'ESP_SLEEP_WAKEUP_TIMER')] = "Wakeup caused by timer"
        if hasattr(esp32, 'ESP_SLEEP_WAKEUP_TOUCHPAD'):
            wake_map[getattr(esp32, 'ESP_SLEEP_WAKEUP_TOUCHPAD')] = "Wakeup caused by touchpad"
        if hasattr(esp32, 'ESP_SLEEP_WAKEUP_ULP'):
            wake_map[getattr(esp32, 'ESP_SLEEP_WAKEUP_ULP')] = "Wakeup caused by ULP program"
    except Exception:
        pass

    # machine constants (if present)
    try:
        if hasattr(machine, 'PIN_WAKE'):
            wake_map[getattr(machine, 'PIN_WAKE')] = "Wakeup caused by external signal using RTC_IO"
        if hasattr(machine, 'RTC_WAKE'):
            wake_map[getattr(machine, 'RTC_WAKE')] = "Wakeup caused by timer"
        if hasattr(machine, 'ULP_WAKE'):
            wake_map[getattr(machine, 'ULP_WAKE')] = "Wakeup caused by ULP program"
        if hasattr(machine, 'WLAN_WAKE'):
            wake_map[getattr(machine, 'WLAN_WAKE')] = "Wakeup caused by WLAN"
        if hasattr(machine, 'PWRON_WAKE'):
            wake_map[getattr(machine, 'PWRON_WAKE')] = "Wakeup was caused by power on / reset"
    except Exception:
        pass

    # Numeric fallbacks (cover several common enum orderings across firmwares)
    numeric_fallback = {
        0: "Wakeup was not caused",
        1: "Wakeup was not caused",
        2: "Wakeup caused by external signal using RTC_IO",
        3: "Wakeup caused by external signal using RTC_CNTL",
        4: "Wakeup caused by timer",
        5: "Wakeup caused by touchpad",
        6: "Wakeup caused by ULP program"
    }

    # Decide final message
    msg = "Wakeup was not caused"
    if wake_cause is not None:
        if wake_cause in wake_map:
            msg = wake_map[wake_cause]
        elif isinstance(wake_cause, int) and wake_cause in numeric_fallback:
            msg = numeric_fallback[wake_cause]
        else:
            # Unknown numeric/enum value — include raw value to help debugging
            try:
                msg = f"Wakeup was not caused (raw={int(wake_cause)})"
            except Exception:
                msg = "Wakeup was not caused (raw_unknown)"

    # If the reset was due to deep sleep wakeup, show Arduino-style wakeup message
    if rc == DEEPSLEEP_RESET:
        reason = msg
        # print("reset_cause:", rc, reason)
        return rc

    # Non-deep-sleep resets: keep the original reset-name mapping
    cause_map = {
        PWRON_RESET:      "PWRON_RESET",
        HARD_RESET:       "HARD_RESET",
        WDT_RESET:        "WDT_RESET",
        DEEPSLEEP_RESET:  "DEEPSLEEP_RESET",
        SOFT_RESET:       "SOFT_RESET"
    }
    if rc in cause_map:
        reason = cause_map[rc]
    else:
        reason = "None"
    print("reset_cause:", rc, cause_map.get(rc, "None"))
    return rc

#  activate the vibration motor
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
    print("error:", e)

backlight_pin = Pin(42, Pin.OUT)
backlight_pin.value(1)

scrn = lv.screen_active()
scrn.set_style_bg_color(lv.color_hex(0x000000), 0)

a = lv.label(scrn)
a.set_text('Boot counter: 1')
a.align(lv.ALIGN.TOP_LEFT, 30,100)

b = lv.label(scrn)
b.set_text('Wakeup was not caused')
b.align(lv.ALIGN.TOP_LEFT, 30,130)

c = lv.label(scrn)
c.set_text('Waiting to press the crown to go to sleep ...')
c.align(lv.ALIGN.TOP_LEFT, 30,160)

vibrate_motor()
scan_i2c_devices()

# read the sleep counter from a file
def read_boot_counter():
    try:
        with open('boot_counter.txt', 'r') as f:
            count = int(f.read())
            return count
    except (OSError, ValueError):
        return 1
# write the sleep counter to a file
def write_boot_counter(count):
    with open('boot_counter.txt', 'w') as f:
        f.write(str(count))

# called after waking up
def after_wakeup():
    global boot_counter, reason
    boot_counter += 1
    write_boot_counter(boot_counter) 
    a.set_text(f'Boot counter: {boot_counter}')
    b.set_text(reason)
    
# Check the type of reset that occurred
rc = print_reset_cause()
if rc == DEEPSLEEP_RESET:
    boot_counter = read_boot_counter()
    after_wakeup()
else:
    boot_counter = 1 
    write_boot_counter(boot_counter)

def countdown_timer(s):
    while True:
        s -= 1
        time.sleep(1)
        if s == 0:
            break

#  handle button press and initiate deep sleep
def on_button_press(pin):
    global sleep_status
    esp32.wake_on_ext0(pin=pin, level=0)
    sleep_status = True

button_pin = Pin(0, Pin.IN, Pin.PULL_UP)
button_pin.irq(trigger=Pin.IRQ_FALLING, handler=on_button_press)

task_handler.TaskHandler(33)

while True:
    if sleep_status:
        s = 5
        while True:
            print(s)
            c.set_text(f'Go to sleep after {s} seconds')
            s -= 1
            time.sleep(1)
            if s == 0:
                c.set_text(f'Sleep now ...')
                time.sleep(1)
                sleep_status = False
                break
        deepsleep()
        print("This will never be printed")