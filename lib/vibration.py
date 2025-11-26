from machine import Pin, I2C
import time

class vibrationMotor:
    DEVICE_ADDR = 0x5A
    REG_MODE = 0x01
    REG_RTPIN = 0x02

    def __init__(self, i2c, frequency=400000):
        self.i2c = i2c
        self.init_realtime()

    def write_reg(self, reg, val):
        # Write to the specified register
        self.i2c.writeto_mem(self.DEVICE_ADDR, reg, bytes([val]))

    def init_realtime(self):
        # Initialize the vibration motor in real-time mode
        self.write_reg(self.REG_MODE, 0x05)

    def vibrate(self, duration=3, strength=200):
        # Set the strength and duration of the vibration
        self.write_reg(self.REG_RTPIN, strength)
        time.sleep(duration)
        self.write_reg(self.REG_RTPIN, 0)
