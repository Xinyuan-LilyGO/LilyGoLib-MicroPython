'''
 * @file      RTC_AlarmByUnits.py
 * @license   MIT
 * @copyright Copyright (c) 2025  Shenzhen Xin Yuan Electronic Technology Co., Ltd
 * @date      2025-10-29
'''
from machine import SPI, Pin, I2C, RTC
import sys
import lcd_bus
import st7796
import lvgl as lv
from micropython import const
import vibration
import _thread
import time

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

label1 = lv.label(scrn)
label1.set_text("RTC_AlarmByUnits_Example")
label1.set_width(lv.pct(90))
label1.center()

datetime_label = lv.label(scrn)
datetime_label.set_text("00:00:00")
datetime_label.set_width(lv.pct(90))
datetime_label.align_to(label1, lv.ALIGN.OUT_BOTTOM_MID, 0, 5)

last_millis = 0
next_hour = 22
next_month = 1
next_day = 1
next_minute = 59
next_second = 55

is_alarm = False
alarm_minute = 0  
alarm_hour = 0   
alarm_day = 1  

weekdays = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

def format_datetime():
    now = time.localtime()
    
    micropython_weekday = now[6] 
    cpp_weekday = (micropython_weekday + 1) % 7
    
    weekday = weekdays[cpp_weekday]
    month_name = months[now[1] - 1]
    
    return "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d} {}".format(
        now[0], now[1], now[2], now[3], now[4], now[5], weekday)

def set_rtc_datetime(year, month, day, hour, minute, second):
    rtc = RTC()
    rtc.datetime((year, month, day, 0, hour, minute, second, 0))

def get_days_in_month(month, year):
    if month in [1, 3, 5, 7, 8, 10, 12]:
        return 31
    elif month in [4, 6, 9, 11]:
        return 30
    elif month == 2:
        if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
            return 29
        else:
            return 28
    return 30

def set_alarm_by_minutes(minute):
    global alarm_minute
    alarm_minute = minute
    print("Alarm set to trigger at minute:", minute)

def set_alarm_by_hours(hour):
    global alarm_hour
    alarm_hour = hour
    print("Alarm set to trigger at hour:", hour)

def set_alarm_by_days(day):
    global alarm_day
    alarm_day = day
    print("Alarm set to trigger at day:", day)

def enable_alarm():
    print("Alarm enabled")

def reset_alarm():
    global is_alarm
    is_alarm = False
    print("Alarm reset")

def is_alarm_active():
    return is_alarm

def check_alarm():
    global is_alarm
    current = time.localtime()
    
    if alarm_minute is not None and current[4] == alarm_minute and current[5] == 0:
        is_alarm = True
        return True
        
    if alarm_hour is not None and current[3] == alarm_hour and current[4] == 0 and current[5] == 0:
        is_alarm = True
        return True

    if alarm_day is not None and current[2] == alarm_day and current[3] == 0 and current[4] == 0 and current[5] == 0:
        is_alarm = True
        return True
        
    return False

def print_datetime():
    global last_millis
    current_millis = time.ticks_ms()
    
    if time.ticks_diff(current_millis, last_millis) > 1000:
        datetime_str = format_datetime()
        print(datetime_str)
        
        datetime_label.set_text(datetime_str)
        datetime_label.align_to(label1, lv.ALIGN.OUT_BOTTOM_MID, 0, 5)
        last_millis = current_millis
        
    lv.task_handler()
    time.sleep_ms(5)

set_rtc_datetime(2023, next_month, next_day, next_hour, next_minute, next_second)
set_alarm_by_minutes(0) 
enable_alarm()

def test_alarm_minute():
    global next_hour, next_day, is_alarm
    
    label1.set_text("RTC_testAlarmMinute")
    label1.center()
    
    while True:
        if check_alarm():
            is_alarm = False
            print("testAlarmMinute Interrupt .... ")
            if is_alarm_active():
                print("Alarm active")
                reset_alarm()
                set_rtc_datetime(2022, next_month, next_day, next_hour, next_minute, next_second)
                next_hour += 1
                
                if next_hour >= 24:
                    next_hour = 23
                    next_day = 25
                    set_alarm_by_hours(0) 
                    print("setAlarmByHours")
                    return
        
        print_datetime()

def test_alarm_hour():
    global next_day, next_month, next_hour, next_minute, next_second, is_alarm
    
    label1.set_text("RTC_testAlarmHour")
    label1.center()
    
    while True:
        if check_alarm():
            is_alarm = False
            print("testAlarmHour Interrupt .... ")
            if is_alarm_active():
                print("Alarm active")
                reset_alarm()
                set_rtc_datetime(2022, next_month, next_day, next_hour, next_minute, next_second)
                next_day += 1
                
                if next_day >= 30:
                    next_month = 1
                    next_hour = 23
                    next_minute = 59
                    next_second = 55
                    next_day = get_days_in_month(next_month, 2022)
                    set_rtc_datetime(2022, next_month, next_day, next_hour, next_minute, next_second)
                    set_alarm_by_days(1)
                    print("setAlarmByDays")
                    return
        
        print_datetime()

def test_alarm_day():
    global next_day, next_month, is_alarm
    
    label1.set_text("RTC_testAlarmDay")
    label1.center()
    
    while True:
        if check_alarm():
            is_alarm = False
            print("testAlarmDay Interrupt .... ")
            if is_alarm_active():
                print("Alarm active")
                reset_alarm()
                next_day = get_days_in_month(next_month, 2022)
                set_rtc_datetime(2022, next_month, next_day, next_hour, next_minute, next_second)
                next_month += 1
                
                if next_month >= 12:
                    return
        
        print_datetime()

import task_handler
task_handler.TaskHandler(33)

def main():
    test_alarm_minute()
    test_alarm_hour()
    test_alarm_day()
    
    print("Test done ...")
    label1.set_text("RTC_Test done ...")
    
    while True:
        print_datetime()

if __name__ == '__main__':
    main()