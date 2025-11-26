from machine import Pin
import time

class RotaryEncoder:
    def __init__(self, clk_pin, dt_pin, sw_pin):
        self.pin_clk = Pin(clk_pin, Pin.IN, Pin.PULL_UP)
        self.pin_dt = Pin(dt_pin, Pin.IN, Pin.PULL_UP)
        self.pin_sw = Pin(sw_pin, Pin.IN, Pin.PULL_UP)

        self.last_clk_state = self.pin_clk.value()
        self.last_button_state = 1
        self.button_debounce_time = 0
        self.rotary_debounce_time = 0

        self.rotary_key = None 

        #print("Rotary encoder ready.")

    def update(self):
        clk_state = self.pin_clk.value()
        dt_state = self.pin_dt.value()
        sw_state = self.pin_sw.value()
        current_time = time.ticks_ms()

        self.rotary_key = None 

        if clk_state == 0 and self.last_clk_state == 1:
            if time.ticks_diff(current_time, self.rotary_debounce_time) > 100:
                if dt_state == 0:
                    self.rotary_key = "down"
                else:
                    self.rotary_key = "up"
                self.rotary_debounce_time = current_time

        self.last_clk_state = clk_state

        if sw_state == 0 and self.last_button_state == 1:
            if time.ticks_diff(current_time, self.button_debounce_time) > 500:
                self.rotary_key = "enter"
                self.button_debounce_time = current_time

        self.last_button_state = sw_state

        return self.rotary_key
