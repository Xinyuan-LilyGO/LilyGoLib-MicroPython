from machine import SPI, Pin, I2C
import sys
import lcd_bus
import st7796
import lvgl as lv
import vibration
import _thread
import time

BQ27220_ADDRESS = 0x55
BQ25896_ADDRESS = 0x6B
DRV2605_ADDRESS = 0x5A
BQ27220_REG_ROM_START = 0x40
BQ27220_ROM_OPERATION_CONFIG_A = 0x0000
START_REGISTER  = 0x02
REGISTER_COUNT  = 54
data = bytearray(REGISTER_COUNT * 2)

i2c = I2C(0, scl=Pin(2), sda=Pin(3), freq=400000)
vb = vibration.vibrationMotor(i2c)

def vibrate_motor():
    vb.vibrate(1, 200)
    
def low_byte(value):
    return value & 0xFF

def high_byte(value):
    return (value >> 8) & 0xFF

class OperationStatus:
    def __init__(self, value):
        self.value = value
    
    def getIsConfigUpdateMode(self):
        return bool(self.value & 0x8000)
    
    def getIsBtpThresholdExceeded(self):
        return bool(self.value & 0x4000)
    
    def getIsCapacityAccumulationThrottled(self):
        return bool(self.value & 0x2000)
    
    def getIsInitializationComplete(self):
        return bool(self.value & 0x1000)
    
    def getIsDischargeCycleCompliant(self):
        return bool(self.value & 0x0800)
    
    def getIsBatteryVoltageBelowEdv2(self):
        return bool(self.value & 0x0400)
    
    def getSecurityAccessLevel(self):
        return (self.value >> 6) & 0x03
    
    def getIsCalibrationModeEnabled(self):
        return bool(self.value & 0x0020)

class BatteryStatus:
    def __init__(self, value):
        self.value = value
    
    def isFullDischargeDetected(self):
        return bool(self.value & 0x8000)
    
    def isOcvMeasurementUpdateComplete(self):
        return bool(self.value & 0x4000)
    
    def isOcvReadFailedDueToCurrent(self):
        return bool(self.value & 0x2000)
    
    def isInSleepMode(self):
        return bool(self.value & 0x1000)
    
    def isOverTemperatureDuringCharging(self):
        return bool(self.value & 0x0800)
    
    def isOverTemperatureDuringDischarge(self):
        return bool(self.value & 0x0400)
    
    def isFullChargeDetected(self):
        return bool(self.value & 0x0200)
    
    def isChargeInhibited(self):
        return bool(self.value & 0x0100)
    
    def isChargingTerminationAlarm(self):
        return bool(self.value & 0x0080)
    
    def isGoodOcvMeasurement(self):
        return bool(self.value & 0x0040)
    
    def isBatteryInserted(self):
        return bool(self.value & 0x0020)
    
    def isBatteryPresent(self):
        return bool(self.value & 0x0010)
    
    def isDischargeTerminationAlarm(self):
        return bool(self.value & 0x0008)
    
    def isSystemShutdownRequired(self):
        return bool(self.value & 0x0004)
    
    def isInDischargeMode(self):
        return bool(self.value & 0x0002)

def getOperationStatus():
    status_value = int.from_bytes(data[48:50], 'little')
    return OperationStatus(status_value)

def getBatteryStatus():
    status_value = int.from_bytes(data[50:52], 'little')
    return BatteryStatus(status_value)

class OperationConfig:
    def __init__(self, value):
        self.value = value
        self.registerValue = value << 16
        
        self.rawA = value
        self.temps = (self.rawA >> 7) & 1
        self.reserved1 = (self.rawA >> 6) & 1
        self.batg_pol = (self.rawA >> 5) & 1
        self.batg_en = (self.rawA >> 4) & 1
        self.reserved2 = (self.rawA >> 3) & 1
        self.sleep = (self.rawA >> 2) & 1
        self.slpwakechg = (self.rawA >> 1) & 1
        self.wrtemp = self.rawA & 1
        
        # Parse low - byte bits
        self.bienable = (self.rawA >> 15) & 1
        self.reserved3 = (self.rawA >> 14) & 1
        self.bl_pup_en = (self.rawA >> 13) & 1
        self.pfc_cfg = (self.rawA >> 11) & 1
        self.wake_en = (self.rawA >> 10) & 1
        self.wk_th1 = (self.rawA >> 9) & 1
        self.wk_th0 = (self.rawA >> 8) & 1
    
        self.rawB = (self.value & 0xFFFF)

        # Parse high - byte bits
        self.defaultSeal = (self.rawB >> 3) & 1
        self.nonRemovable = (self.rawB >> 2) & 1
  
        # Parse low - byte bits
        self.intBrem = (self.rawB >> 15) & 1
        self.intBatL = (self.rawB >> 14) & 1
        self.intState = (self.rawB >> 13) & 1
        self.intOcv = (self.rawB >> 12) & 1
        self.intOt = (self.rawB >> 10) & 1
        self.intPol = (self.rawB >> 9) & 1
        self.intFocv = (self.rawB >> 8) & 1
        
    def is_temps_set(self):
        return bool(self.temps)
    
    def isBatgPolHigh(self):
        return bool(self.batg_pol)
    
    def isBatgEnEnabled(self):
        return bool(self.batg_en)
    
    def canEnterSleep(self):
        return bool(self.sleep)
    
    def isSlpwakechgEnabled(self):
        return bool(self.slpwakechg)
    
    def isWrtempEnabled(self):
        return bool(self.wrtemp)
    
    def isBienableEnabled(self):
        return bool(self.bienable)
    
    def isBlPupEnEnabled(self):
        return bool(self.bl_pup_en)
    
    def getPfcCfg(self):
        return int(self.pfc_cfg)
    
    def isWakeEnEnabled(self):
        return bool(self.wake_en)
    
    def getWkTh1(self):
        return int(self.wk_th1)
    
    def getWkTh0(self):
        return int(self.wk_th0)
    
    def getConfigB(self):
        return self.rawB
    
    def isDefaultSealEnabled(self):
        return bool(self.defaultSeal)
    
    def isNonRemovableSet(self):
        return bool(self.nonRemovable)
    
    def isIntBremEnabled(self):
        return bool(self.intBrem)
    
    def isIntBatLEnabled(self):
        return bool(self.intBatL)
    
    def isIntStateEnabled(self):
        return bool(self.intState)
    
    def isIntOcvEnabled(self):
        return bool(self.intOcv)
    
    def isIntOtEnabled(self):
        return bool(self.intOt)
    
    def isIntPolHigh(self):
        return bool(self.intPol)
    
    def isIntFocvEnabled(self):
        return bool(self.intFocv)
    
    def __str__(self):
        return f"OperationConfig(0x{self.value:04X})"

def getOperationConfig():
    try:
        address_bytes = bytes([low_byte(BQ27220_ROM_OPERATION_CONFIG_A), 
                              high_byte(BQ27220_ROM_OPERATION_CONFIG_A)])
        i2c.writeto_mem(BQ27220_ADDRESS, BQ27220_REG_ROM_START, address_bytes)
        time.sleep_ms(10)
        buffer = i2c.readfrom_mem(BQ27220_ADDRESS, 0x40, 2)
        config_value_big = (buffer[0] << 8) | buffer[1] 
        config_value_little = (buffer[1] << 8) | buffer[0]
        
        if config_value_big == 0x484:
            config_value = config_value_big
        elif config_value_little == 0x484:
            config_value = config_value_little
        else:
            config_value = config_value_little
        
        return OperationConfig(config_value)
        
    except Exception as e:
        return OperationConfig(0)

def refresh():
    try:
        buffer = i2c.readfrom_mem(BQ27220_ADDRESS, START_REGISTER, REGISTER_COUNT)
        if buffer is None or len(buffer) < REGISTER_COUNT:
            return False
        
        ptr = 0
        for i in range(0, REGISTER_COUNT, 2):
            value = (buffer[i + 1] << 8) | buffer[i]
            data[ptr] = value & 0xFF
            data[ptr + 1] = (value >> 8) & 0xFF
            ptr += 2
            
        status_buffer = i2c.readfrom_mem(BQ27220_ADDRESS, 0x3A, 4)
        if status_buffer is None or len(status_buffer) < 4:
            return False

        OperationStatus = (status_buffer[1] << 8) | status_buffer[0]
        DesignCapacity = (status_buffer[3] << 8) | status_buffer[2]
        
        return True
    except Exception as e:
        print(f"Error in refresh: {e}")
        return False
    
def getAtRate():
    value = int.from_bytes(data[0:2], 'little')
    if value >= 0x8000: 
        return value - 0x10000
    return value

def getAtRateTimeToEmpty():
    return int.from_bytes(data[2:4], 'little')

def getTemperature():
    return int.from_bytes(data[4:6], 'little') / 10.0 - 273.15

def getVoltage():
    return int.from_bytes(data[6:8], 'little')

def getCurrent():
    value = int.from_bytes(data[10:11], 'little')
    if value >= 0x8000: 
        return value - 0x10000
    return value

def getRemainingCapacity():
    return int.from_bytes(data[10:12], 'little')

def getFullChargeCapacity():
    return int.from_bytes(data[14:16], 'little')

def getDesignCapacity():
    return int.from_bytes(data[16:18], 'little')

def getTimeToEmpty():
    return int.from_bytes(data[20:22], 'little')

def getTimeToFull():
    value = int.from_bytes(data[22:24], 'little')
    if value >= 0x8000: 
         return value - 0x10000
    return value

def getStandbyCurrent():
    value = int.from_bytes(data[24:26], 'little')
    if value >= 0x8000: 
         return value - 0x10000
    return value

def getStandbyTimeToEmpty():
    return int.from_bytes(data[26:28], 'little')

def getMaxLoadCurrent():
    value = int.from_bytes(data[28:30], 'little')
    if value >= 0x8000: 
         return value - 0x10000
    return value
    
def getMaxLoadTimeToEmpty():
    return int.from_bytes(data[30:32], 'little')

def getRawCoulombCount():
    value = int.from_bytes(data[32:34], 'little')
    return value

def getAveragePower():
    value = int.from_bytes(data[33:35], 'little')
    return value

def getInternalTemperature():
    return int.from_bytes(data[38:40], 'little') / 10.0 -273.15

def getCycleCount():
    return int.from_bytes(data[34:36], 'little')

def getStateOfCharge():
    return int.from_bytes(data[42:44], 'little')

def getStateOfHealth():
    return int.from_bytes(data[44:46], 'little')

def getRequestChargingVoltage():
    return int.from_bytes(data[46:48], 'little')

def getRequestChargingCurrent():
    return int.from_bytes(data[48:50], 'little')

def getBTPDischargeSet():
    return int.from_bytes(data[50:52], 'little')

def getBTPChargeSet():
    return int.from_bytes(data[52:54], 'little')

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
    print("Display initialization failed:", e)

_thread.start_new_thread(vibrate_motor, ())
backlight_pin = Pin(42, Pin.OUT)
backlight_pin.value(1)

scrn = lv.screen_active()
scrn.set_style_bg_color(lv.color_hex(0x000000), 0)

label = lv.label(scrn)
label.set_text('Gauge example,all message output to serial')
label.center()
lv.task_handler()

def read_bq27220_register(reg):
    data = i2c.readfrom_mem(BQ27220_ADDRESS, reg, 2)
    return int.from_bytes(data, 'big')

def read_bq25896_register(reg):
    data = i2c.readfrom_mem(BQ25896_ADDRESS, reg, 1)
    return data[0]

def read_battery_info():
    voltage = read_bq27220_register(0x0C)
    remaining_capacity = read_bq27220_register(0x0D)
    temperature = read_bq27220_register(0x0E)
    full_charge_capacity = read_bq27220_register(0x0F)
    charge_status = read_bq25896_register(0x00)
    config = getOperationConfig()
    
    print(f"OperationConfigA Values: 0x{config.value:03X}")
    print(f"External Thermistor Selected: {'YES' if config.is_temps_set() else 'NO'}")
    print(f"BATT_GD Pin Polarity High: {'YES' if config.isBatgPolHigh() else 'NO'}")
    print(f"BATT_GD Function Enabled: {'YES' if config.isBatgEnEnabled() else 'NO'}")
    print(f"Can Enter SLEEP State: {'YES' if config.canEnterSleep() else 'NO'}")
    print(f"slpwakechg Function Enabled: {'YES' if config.isSlpwakechgEnabled() else 'NO'}")
    print(f"Write Temperature Function Enabled: {'YES' if config.isWrtempEnabled() else 'NO'}")
    print(f"Battery Insertion Detection Enabled: {'YES' if config.isBienableEnabled() else 'NO'}")
    print(f"Battery Insertion Pin Pull - Up Enabled: {'YES' if config.isBlPupEnEnabled() else 'NO'}")
    print(f"Pin Function Code (PFC) Mode: {config.getPfcCfg()}")
    print(f"Wake - Up Function Enabled: {'YES' if config.isWakeEnEnabled() else 'NO'}")
    print(f"Wake - Up Threshold 1: {config.getWkTh1()}")
    print(f"Wake - Up Threshold 0: {config.getWkTh0()}")
    print(f"\nOperationConfigB Values:0x{config.getConfigB()}")
    print(f"Default Seal Option Enabled: {'YES' if config.isDefaultSealEnabled() else 'NO'}")
    print(f"Non - Removable Option Set: {'YES' if config.isNonRemovableSet() else 'NO'}")
    print(f"INT_BREM Function Enabled: {'YES' if config.isIntBremEnabled() else 'NO'}")
    print(f"INT_BATL Function Enabled: {'YES' if config.isIntBatLEnabled() else 'NO'}")
    print(f"INT_STATE Function Enabled: {'YES' if config.isIntStateEnabled() else 'NO'}")
    print(f"INT_OCV Function Enabled: {'YES' if config.isIntOcvEnabled() else 'NO'}")
    print(f"INT_OT Function Enabled: {'YES' if config.isIntOtEnabled() else 'NO'}")
    print(f"INT_POL Function Enabled (High - Level Polarity): {'YES' if config.isIntPolHigh() else 'NO'}")
    print(f"INT_FOCV Function Enabled: {'YES' if config.isIntFocvEnabled() else 'NO'}")

def main():
    while True:
        start_meas_time = time.ticks_ms()
        
        if refresh():
            end_meas_time = time.ticks_ms()

            print("Polling time:", time.ticks_diff(end_meas_time, start_meas_time), "ms")
            
            print("\nStandard query:")
            print("\t- AtRate:", getAtRate(), "mA")
            print("\t- AtRateTimeToEmpty:", getAtRateTimeToEmpty(), "minutes")
            print("\t- Temperature:", getTemperature(), "℃")
            print("\t- BatteryVoltage:", getVoltage(), "mV")
            
            print("\t- InstantaneousCurrent:", getCurrent(), "mAh")
            print("\t- RemainingCapacity:", getRemainingCapacity(), "mAh")
            print("\t- FullChargeCapacity:", getFullChargeCapacity(), "mAh")
            print("\t- DesignCapacity:", getDesignCapacity(), "mAh")
            print("\t- TimeToEmpty:", getTimeToEmpty(), "minutes")
            print("\t- TimeToFull:", getTimeToFull(), "minutes")
            print("\t- StandbyCurrent:", getStandbyCurrent(), "mA")
            print("\t- StandbyTimeToEmpty:", getStandbyTimeToEmpty(), "minutes")
            print("\t- MaxLoadCurrent:", getMaxLoadCurrent(), "mA")
            print("\t- MaxLoadTimeToEmpty:", getMaxLoadTimeToEmpty(), "minute")
            print("\t- RawCoulombCount:", getRawCoulombCount(), "mAh")
            print("\t- AveragePower:", getAveragePower(), "mW")
            print("\t- InternalTemperature:", getInternalTemperature(), "℃")
            print("\t- CycleCount:", getCycleCount())
            print("\t- StateOfCharge:", getStateOfCharge(), "%")
            print("\t- StateOfHealth:", getStateOfHealth(), "%")
            print("\t- RequestChargingVoltage:", getRequestChargingVoltage(), "mV")
            print("\t- RequestChargingCurrent:", getRequestChargingCurrent(), "mA")
            print("\t- BTPDischargeSet:", getBTPDischargeSet(), "mAh")
            print("\t- BTPChargeSet:", getBTPChargeSet(), "mAh")
            
            status = getOperationStatus()
            battery_status = getBatteryStatus()

            print("\nOperation Status:")
            print("\t- getIsConfigUpdateMode:", "YES" if status.getIsConfigUpdateMode() else "NO")
            print("\t- getIsBtpThresholdExceeded:", "YES" if status.getIsBtpThresholdExceeded() else "NO")
            print("\t- getIsCapacityAccumulationThrottled:", "YES" if status.getIsCapacityAccumulationThrottled() else "NO")
            print("\t- getIsInitializationComplete:", "YES" if status.getIsInitializationComplete() else "NO")
            print("\t- getIsDischargeCycleCompliant:", "YES" if status.getIsDischargeCycleCompliant() else "NO")
            print("\t- getIsBatteryVoltageBelowEdv2:", "YES" if status.getIsBatteryVoltageBelowEdv2() else "NO")
            print("\t- getSecurityAccessLevel:", status.getSecurityAccessLevel())
            print("\t- getIsCalibrationModeEnabled:", "YES" if status.getIsCalibrationModeEnabled() else "NO")

            print("\nBattery Status:")
            if battery_status.isFullDischargeDetected():
                print("\t- Full discharge detected.")
            if battery_status.isOcvMeasurementUpdateComplete():
                print("\t- OCV measurement update is complete.")
            if battery_status.isOcvReadFailedDueToCurrent():
                print("\t- Status bit indicating that an OCV read failed due to current.")
                print("\tThis bit can only be set if a battery is present after receiving an OCV_CMD().")
            if battery_status.isInSleepMode():
                print("\t- The device operates in SLEEP mode")
            if battery_status.isOverTemperatureDuringCharging():
                print("\t- Over-temperature is detected during charging.")
            if battery_status.isOverTemperatureDuringDischarge():
                print("\t- Over-temperature detected during discharge condition.")
            if battery_status.isFullChargeDetected():
                print("\t- Full charge detected.")
            if battery_status.isChargeInhibited():
                print("\t- Charge Inhibit: If set, indicates that charging should not begin because the Temperature() is outside the range")
                print("\t[Charge Inhibit Temp Low, Charge Inhibit Temp High]. ")
            if battery_status.isChargingTerminationAlarm():
                print("\t- Termination of charging alarm. This flag is set and cleared based on the selected SOC Flag Config A option.")
            if battery_status.isGoodOcvMeasurement():
                print("\t- A good OCV measurement was made.")
            if battery_status.isBatteryInserted():
                print("\t- Detects inserted battery.")
            if battery_status.isBatteryPresent():
                print("\t- Battery presence detected.")
            if battery_status.isDischargeTerminationAlarm():
                print("\t- Termination discharge alarm. This flag is set and cleared according to the selected SOC Flag Config A option.")
            if battery_status.isSystemShutdownRequired():
                print("\t- System shutdown bit indicating that the system should be shut down. True when set. If set, the SOC_INT pin toggles once.")
            if battery_status.isInDischargeMode():
                print("\t- When set, the device is in DISCHARGE mode; when cleared, the device is in CHARGING or RELAXATION mode.")
            print("===============================================")
        time.sleep(3)

if __name__ == "__main__":
    read_battery_info()
    main()