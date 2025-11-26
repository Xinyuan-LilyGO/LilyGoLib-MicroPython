'''
 * @file      BLEMouse.py
 * @license   MIT
 * @copyright Copyright (c) 2025  ShenZhen XinYuan Electronic Technology Co., Ltd
 * @date      2025-11-20
 * @note      For devices with touch, use the touch screen to simulate a mouse
 *            For devices with a rotary encoder, use the encoder to simulate the middle scroll wheel
'''
import time
from machine import SoftSPI, Pin, SPI, I2C
from hid_services import Mouse
import rotary
import sys
import lcd_bus
import st7796
import lvgl as lv
from micropython import const
import vibration
import _thread
import task_handler

class Device:
    def __init__(self):
        self.encoder = rotary.RotaryEncoder(40, 41, 7)
        self.wheel_delta = 0
        self.click_pending = False 
        self.mouse = Mouse("T-LoRaPager-Mouse")
        # self.mouse.set_state_change_callback(self.mouse_state_callback)
        self.mouse.start()

    def mouse_state_callback(self):
        if self.mouse.get_state() is Mouse.DEVICE_IDLE:
            print("Idle equipment")
        elif self.mouse.get_state() is Mouse.DEVICE_ADVERTISING:
            print("Broadcasting now, waiting for connection...")
        elif self.mouse.get_state() is Mouse.DEVICE_CONNECTED:
            print("Connected")
        else:
            print("Unknown device")

    def handle_encoder_input(self):
        key = self.encoder.update()
        if key is None:
            return False
        
        if key == "up":
            self.wheel_delta = 1
            return True
            
        elif key == "down":
            self.wheel_delta = -1 
            return True
            
        elif key == "enter":
            self.click_pending = True
            return True
          
        return False

    def advertise(self):
        self.mouse.start_advertising()

    def stop_advertise(self):
        self.mouse.stop_advertising()

    def start(self):
        self.advertise()
        while True:
            input_detected = self.handle_encoder_input()
            time.sleep_ms(11) 
            if self.mouse.get_state() is Mouse.DEVICE_CONNECTED:
                if self.wheel_delta != 0:
                    self.mouse.set_wheel(self.wheel_delta)
                    self.mouse.notify_hid_report()
                    self.mouse.set_wheel(0)
                    self.wheel_delta = 0
                    time.sleep_ms(20)
                
                if self.click_pending:
                    self.mouse.set_wheel(0)
                    self.mouse.set_buttons(1)
                    self.mouse.notify_hid_report()
                    time.sleep_ms(50)
                    self.mouse.set_buttons(0)
                    self.mouse.notify_hid_report()
                    self.click_pending = False
                    self.mouse.set_wheel(0)

            elif self.mouse.get_state() is Mouse.DEVICE_IDLE:
                self.advertise()
                timeout = 30
                while timeout > 0 and self.mouse.get_state() is Mouse.DEVICE_ADVERTISING:
                    time.sleep(1)
                    timeout -= 1
                    self.handle_encoder_input()
                
                if self.mouse.get_state() is Mouse.DEVICE_ADVERTISING:
                    self.stop_advertise()
            
            if self.mouse.get_state() is Mouse.DEVICE_CONNECTED:
                time.sleep_ms(10) 
            else:
                time.sleep(1)

    def stop(self):
        self.mouse.stop()


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
label.set_text("BLE Mouse example\n 1.Turn on your phone's Bluetooth and search\n 2. Click Connect and the device will act as a mouse device\n Use a rotary encoder to simulate a mouse middle\n button scroll wheel operation")
label.center()

task_handler.TaskHandler(33)


if __name__ == "__main__":
    d = Device()
    try:
        d.start()
    except KeyboardInterrupt:
        d.stop()