'''
 * @file      SimpleTone.py
 * @license   MIT
 * @copyright Copyright (c) 2025  ShenZhen XinYuan Electronic Technology Co., Ltd
 * @date      2025-12-22
'''
import os
import time
import math
from machine import Pin, I2S
from es8311 import ES8311
    # ======= ES8311 CONFIGURATION =======
codec = ES8311(scl=2, sda=3, mck=10, rate=32000)
codec.power_on()
codec.set_volume(70)

    # ======= I2S CONFIGURATION =======
SCK_PIN = 11
WS_PIN = 18
SD_PIN = 45
I2S_ID = 0
BUFFER_LENGTH_IN_BYTES = 40000
SAMPLE_RATE = 32000
bits_per_sample = 16
channels = I2S.MONO
    # ======= I2S CONFIGURATION =======

# Create I2S interface
audio_out = I2S(
    I2S_ID,
    sck=Pin(SCK_PIN),
    ws=Pin(WS_PIN),
    sd=Pin(SD_PIN),
    mode=I2S.TX,
    bits=bits_per_sample,
    format=channels,
    rate=SAMPLE_RATE,
    ibuf=BUFFER_LENGTH_IN_BYTES,
)

def generate_tone(frequency, duration_ms):
    """Generate a tone of specified frequency and duration"""
    num_samples = int(SAMPLE_RATE * duration_ms / 1000)
    samples = bytearray(num_samples * 2)  # 2 bytes per 16-bit sample
    
    for i in range(num_samples):
        # Generate sine wave
        value = int(32767 * math.sin(2 * math.pi * frequency * i / SAMPLE_RATE))
        # Convert to little-endian bytes
        samples[i * 2] = value & 0xff
        samples[i * 2 + 1] = (value >> 8) & 0xff
    
    return samples

# Generate "beep" tones
tone1 = generate_tone(1000, 200)  # 1000Hz, 200ms
silence = bytearray(3200)  # 100ms silence (32000 samples/sec * 0.1 sec * 2 bytes/sample)

# Play "beep beep beep" sequence
try:
    for _ in range(3):
        audio_out.write(tone1)
        audio_out.write(silence)
    
    # Wait for playback to complete
    time.sleep(2)
finally:
    audio_out.deinit()
    codec.power_off()
    from machine import SPI, Pin, PWM, ADC, RTC, deepsleep
    deepsleep()
