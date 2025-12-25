import math

import time
from machine import PWM, Pin, I2C, I2S

# --------------------------------------------------
# ES8311 I2C address
# --------------------------------------------------
ES8311_ADDR = 0x18

# --------------------------------------------------
# ES8311 register initialization table
# --------------------------------------------------
register_values = [
    (0x00, 0x80), (0x01, 0x3F), (0x02, 0x00), (0x03, 0x10), (0x04, 0x10),
    (0x05, 0x00), (0x06, 0x03), (0x07, 0x00), (0x08, 0xFF), (0x09, 0x0C),
    (0x0A, 0x4C), (0x0B, 0x00), (0x0C, 0x00), (0x0D, 0x01), (0x0E, 0x02),
    (0x0F, 0x00), (0x10, 0x1F), (0x11, 0x7F), (0x12, 0x00), (0x13, 0x10),
    (0x14, 0x1A), (0x15, 0x40), (0x16, 0x24), (0x17, 0xBF), (0x18, 0x00),
    (0x19, 0x00), (0x1A, 0x00), (0x1B, 0x0A), (0x1C, 0x6A),
    (0x32, 0x9F), (0x37, 0x08), (0x44, 0x50),
]
initial_register_values = [
    (0x00, 0x1F), (0x01, 0x00), (0x02, 0x00), (0x03, 0x10), (0x04, 0x10),
    (0x05, 0x00), (0x06, 0x03), (0x07, 0x00), (0x08, 0xFF), (0x09, 0x00),
    (0x0A, 0x00), (0x0B, 0x00), (0x0C, 0x20), (0x0D, 0xFC), (0x0E, 0x6A),
    (0x0F, 0x00), (0x10, 0x13), (0x11, 0x7C), (0x12, 0x02), (0x13, 0x40),
    (0x14, 0x10), (0x15, 0x00), (0x16, 0x04), (0x17, 0x00), (0x18, 0x00),
    (0x19, 0x00), (0x1A, 0x00), (0x1B, 0x0C), (0x1C, 0x4C),
    (0x32, 0x00), (0x37, 0x08), (0x44, 0x00),
]
# --------------------------------------------------
# Speaker amplifier enable
# --------------------------------------------------
amp_enable = Pin(9, Pin.OUT)
amp_enable.value(1)

# --------------------------------------------------
# ES8311 Driver Class
# --------------------------------------------------
class ES8311:
    def __init__(self,
                 scl=4,
                 sda=5,
                 mck=6, rate = 8000):
        
        self.scl = scl
        self.sda = sda
        self.mck = mck
        self.rate = rate
        # ---------- MCLK (must persist) ----------
        self.mclk = PWM(
            Pin(mck),
            freq=44100 * 256,
            duty_u16=32768)
    def power_on(self):
    # Re-create peripherals
        self.i2c = I2C(1, scl=Pin(self.scl), sda=Pin(self.sda), freq=400_000)
        self.mclk = PWM(Pin(self.mck), freq=self.rate * 256, duty_u16=32768)

    # Codec init
        for reg, val in register_values:
            self.write(reg, val)
            time.sleep_ms(10)

    def power_off(self):
    # Power down codec first (I2C must still be alive)
        for reg, val in initial_register_values:
            self.write(reg, val)
            time.sleep_ms(10)

    # Stop clocks AFTER codec is powered down
        if hasattr(self, "mclk"):
            self.mclk.deinit()
            del self.mclk


    # I2C can now be safely disabled
        if hasattr(self, "i2c"):
            del self.i2c
            self.i2c = None


    # --------------------------------------------------
    # Low-level register write
    # --------------------------------------------------
    def write(self, reg, value):
        if isinstance(value, int):
            value = value.to_bytes(1, "little")
        self.i2c.writeto_mem(ES8311_ADDR, reg, value)
    
    # --------------------------------------------------
    # Volume control (0–100%)
    # --------------------------------------------------
    def set_volume(self, volume):
        volume = max(0, min(100, volume))
        vol = int(255 * volume / 100)
        self.write(0x32, vol)