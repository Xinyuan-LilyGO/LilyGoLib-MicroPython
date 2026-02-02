import lvgl as lv
import time
import math
import random
import machine
from machine import I2C, Pin
from micropython import const

# XL9555 Register Addresses
XL9555_INPUT_PORT0 = const(0x00)
XL9555_INPUT_PORT1 = const(0x01)
XL9555_OUTPUT_PORT0 = const(0x02)
XL9555_OUTPUT_PORT1 = const(0x03)
XL9555_POLARITY_INVERSION_PORT0 = const(0x04)
XL9555_POLARITY_INVERSION_PORT1 = const(0x05)
XL9555_CONFIGURATION_PORT0 = const(0x06)
XL9555_CONFIGURATION_PORT1 = const(0x07)

# Default I2C address
XL9555_DEFAULT_ADDRESS = const(0x20)

class XL9555:
    """XL9555 GPIO Expander Class"""
    def __init__(self, i2c, address=XL9555_DEFAULT_ADDRESS):
        self.i2c = i2c
        self.address = address
        self._output_port0 = 0x00
        self._output_port1 = 0x00
        
    def _write_register(self, register, value):
        """Write a single byte to a register"""
        try:
            self.i2c.writeto_mem(self.address, register, bytes([value]))
            return True
        except Exception as e:
            print(f"写入XL9555寄存器失败: {e}")
            return False
        
    def _read_register(self, register):
        """Read a single byte from a register"""
        try:
            return self.i2c.readfrom_mem(self.address, register, 1)[0]
        except Exception as e:
            print(f"读取XL9555寄存器失败: {e}")
            return None
        
    def configure(self, pin, direction):
        """Configure GPIO pin direction
        Args:
            pin: Pin number (0-15)
            direction: 0 for output, 1 for input
        """
        if pin < 0 or pin > 15:
            raise ValueError("Pin must be between 0 and 15")
            
        if pin < 8:
            reg = XL9555_CONFIGURATION_PORT0
            bit = pin
        else:
            reg = XL9555_CONFIGURATION_PORT1
            bit = pin - 8
            
        current = self._read_register(reg)
        if current is None:
            print(f"无法读取配置寄存器 {reg}")
            return False
            
        if direction:
            current |= (1 << bit)
        else:
            current &= ~(1 << bit)
        
        return self._write_register(reg, current)
        
    def set_pin(self, pin, value):
        """Set output pin value
        Args:
            pin: Pin number (0-15)
            value: 0 for low, 1 for high
        """
        if pin < 0 or pin > 15:
            raise ValueError("Pin must be between 0 and 15")
            
        if pin < 8:
            reg = XL9555_OUTPUT_PORT0
            bit = pin
            self._output_port0 &= ~(1 << bit)
            if value:
                self._output_port0 |= (1 << bit)
            return self._write_register(reg, self._output_port0)
        else:
            reg = XL9555_OUTPUT_PORT1
            bit = pin - 8
            self._output_port1 &= ~(1 << bit)
            if value:
                self._output_port1 |= (1 << bit)
            return self._write_register(reg, self._output_port1)
            
    def get_pin(self, pin):
        """Get input pin value
        Args:
            pin: Pin number (0-15)
        Returns:
            Pin value (0 or 1)
        """
        if pin < 0 or pin > 15:
            raise ValueError("Pin must be between 0 and 15")
            
        if pin < 8:
            reg = XL9555_INPUT_PORT0
            bit = pin
        else:
            reg = XL9555_INPUT_PORT1
            bit = pin - 8
            
        current = self._read_register(reg)
        if current is None:
            return 0
            
        return (current >> bit) & 1
        
    def set_port(self, port, value):
        """Set entire port value
        Args:
            port: 0 for port0, 1 for port1
            value: 8-bit value for the port
        """
        if port == 0:
            reg = XL9555_OUTPUT_PORT0
            self._output_port0 = value
        else:
            reg = XL9555_OUTPUT_PORT1
            self._output_port1 = value
            
        return self._write_register(reg, value)
        
    def get_port(self, port):
        """Get entire port value
        Args:
            port: 0 for port0, 1 for port1
        Returns:
            8-bit value of the port
        """
        if port == 0:
            reg = XL9555_INPUT_PORT0
        else:
            reg = XL9555_INPUT_PORT1
            
        return self._read_register(reg)

recreate_main_page = None
encoder = None

# ES8311音频编解码器实例
audio_codec = None
# I2S音频输入实例
mic_i2s = None
# 音频缓冲区
audio_buffer = None
# PDM数据缓冲区
pdm_buffer = None

class ES8311:
    """ES8311音频编解码器类"""
    def __init__(self, i2c, i2c_addr=0x18):
        self.i2c = i2c
        self.i2c_addr = i2c_addr
        self.is_open = False
        self.enabled = False
        self.hw_gain = 0.0
        self.bits = 16
        self.sample_rate = 44100
        self.channels = 1

    def write_reg(self, reg, value):
        """写入ES8311寄存器"""
        try:
            self.i2c.writeto_mem(self.i2c_addr, reg, bytes([value]))
            return True
        except OSError:
            print(f"写入ES8311寄存器失败: reg=0x{reg:02X}, value=0x{value:02X}")
            return False

    def read_reg(self, reg):
        """读取ES8311寄存器"""
        try:
            return self.i2c.readfrom_mem(self.i2c_addr, reg, 1)[0]
        except OSError:
            print(f"读取ES8311寄存器失败: reg=0x{reg:02X}")
            return None

    def set_bits_per_sample(self, bits):
        """设置采样位深度"""
        self.bits = bits
        dac_iface = self.read_reg(0x09)
        adc_iface = self.read_reg(0x0A)
        
        if dac_iface is None or adc_iface is None:
            print("无法读取I2S接口寄存器")
            return False
            
        if bits == 16:
            dac_iface |= 0x0c
            adc_iface |= 0x0c
        elif bits == 24:
            dac_iface |= 0x0f
            adc_iface |= 0x0f
        
        return self.write_reg(0x09, dac_iface) and self.write_reg(0x0A, adc_iface)

    def config_fmt(self, fmt):
        """配置音频格式"""
        adc_iface = self.read_reg(0x0A)
        
        if adc_iface is None:
            print("无法读取ADC接口寄存器")
            return False
            
        if fmt == 16:
            adc_iface |= 0x0c
        elif fmt == 24:
            adc_iface |= 0x0f
        
        return self.write_reg(0x0A, adc_iface)

    def set_rate(self, sample_rate):
        """设置采样率"""
        self.sample_rate = sample_rate
        # 设置采样率的具体实现依赖于ES8311的时钟配置
        # 这里简化处理，使用已知的工作配置
        
        success = True
        
        # 16kHz采样率配置
        if sample_rate == 16000:
            # 设置时钟管理器
            success &= self.write_reg(0x01, 0x03)  # 时钟管理
            success &= self.write_reg(0x02, 0x40)  # 时钟分频
            success &= self.write_reg(0x03, 0x0B)  # 时钟配置
            success &= self.write_reg(0x04, 0x03)  # 时钟配置
            success &= self.write_reg(0x05, 0xFF)  # 时钟配置
            success &= self.write_reg(0x06, 0x00)  # 时钟配置
            success &= self.write_reg(0x07, 0x01)  # 时钟配置
        else:
            # 默认配置
            success &= self.write_reg(0x01, 0x03)
            success &= self.write_reg(0x02, 0x40)
            
        return success

    def open_mic_mode(self, bits=16, channels=1, sample_rate=16000, mic_model=None):
        """打开麦克风模式
        Args:
            bits: 采样位深度
            channels: 声道数
            sample_rate: 采样率
            mic_model: 麦克风型号，例如"MIC-4103-G-G00"
        """
        print(f"初始化ES8311麦克风模式，型号: {mic_model}")
        
        # 初始化序列
        # 软复位
        if not self.write_reg(0x00, 0x20):
            print("ES8311软复位失败")
            return False
        
        time.sleep_ms(10)
        
        # 写入初始化序列
        init_seq = [
            (0x0D, 0xC0),  # 主控制器
            (0x00, 0x00),  # 复位寄存器
            (0x0D, 0x80),  # 取消软复位
            (0x0D, 0xC0),  # 激活
            (0x08, 0x03),  # 系统时钟配置
            (0x09, 0x07),  # DAC I2S接口配置
            (0x0A, 0x47),  # ADC I2S接口配置
            (0x0B, 0x00),  # DAC LRCK周期设置
            (0x0C, 0x00),  # ADC LRCK周期设置
            (0x10, 0x08),  # DAC音量设置
            (0x11, 0x08),  # DAC音量设置
            (0x12, 0x00),  # ADC音量设置
            (0x13, 0x00),  # ADC音量设置
            (0x14, 0x12),  # ADC PGA设置
            (0x15, 0x01),  # ADC PGA设置
            (0x16, 0x00),  # 模拟控制
            (0x17, 0x00),  # 模拟控制
            (0x18, 0x18),  # 模拟控制
            (0x1A, 0x00),  # 模拟控制
            (0x1B, 0x00),  # 模拟控制
            (0x1C, 0x00),  # 模拟控制
            (0x1D, 0x00),  # 模拟控制
            (0x1E, 0x01),  # 模拟控制
            (0x1F, 0x00),  # 模拟控制
            (0x20, 0x00),  # 模拟控制
            (0x21, 0x00),  # 模拟控制
            (0x22, 0x00),  # 模拟控制
            (0x23, 0x00),  # 模拟控制
            (0x24, 0x00),  # 模拟控制
            (0x25, 0x00),  # 模拟控制
            (0x26, 0x00),  # 模拟控制
            (0x27, 0x00),  # 模拟控制
            (0x28, 0x00),  # 模拟控制
            (0x29, 0x00),  # 模拟控制
            (0x2A, 0x00),  # 模拟控制
            (0x2B, 0x00),  # 模拟控制
            (0x2C, 0x00),  # 模拟控制
            (0x2D, 0x00),  # 模拟控制
            (0x2E, 0x00),  # 模拟控制
            (0x2F, 0x00),  # 模拟控制
            (0x30, 0x00),  # 模拟控制
            (0x31, 0x00),  # 模拟控制
            (0x32, 0x00),  # 模拟控制
            (0x33, 0x00),  # 模拟控制
            (0x34, 0x00),  # 模拟控制
            (0x35, 0x00),  # 模拟控制
            (0x36, 0x00),  # 模拟控制
            (0x37, 0x00),  # 模拟控制
            (0x38, 0x00),  # 模拟控制
            (0x39, 0x00),  # 模拟控制
            (0x3A, 0x00),  # 模拟控制
            (0x3B, 0x00),  # 模拟控制
            (0x3C, 0x00),  # 模拟控制
            (0x3D, 0x00),  # 模拟控制
            (0x3E, 0x00),  # 模拟控制
            (0x3F, 0x00),  # 模拟控制
            (0x40, 0x00),  # 模拟控制
            (0x41, 0x00),  # 模拟控制
            (0x42, 0x00),  # 模拟控制
            (0x43, 0x00),  # 模拟控制
            (0x44, 0x00),  # 模拟控制
            (0x45, 0x00),  # 模拟控制
            (0x46, 0x00),  # 模拟控制
            (0x47, 0x00),  # 模拟控制
            (0x48, 0x00),  # 模拟控制
            (0x49, 0x00),  # 模拟控制
            (0x4A, 0x00),  # 模拟控制
            (0x4B, 0x00),  # 模拟控制
            (0x4C, 0x00),  # 模拟控制
            (0x4D, 0x00),  # 模拟控制
            (0x4E, 0x00),  # 模拟控制
            (0x4F, 0x00),  # 模拟控制
        ]
        
        for reg, value in init_seq:
            if not self.write_reg(reg, value):
                print(f"初始化序列失败: reg=0x{reg:02X}, value=0x{value:02X}")
                return False
        
        # 设置参数
        if not self.set_bits_per_sample(bits):
            print("设置采样位深度失败")
            return False
        
        if not self.set_rate(sample_rate):
            print("设置采样率失败")
            return False
        
        # 配置I2S为输入模式
        adc_iface_value = self.read_reg(0x0A)
        if adc_iface_value is not None:
            adc_iface_value |= (1 << 6)  # 启用ADC I2S
            success = self.write_reg(0x0A, adc_iface_value)
            if not success:
                print("配置ADC I2S接口失败")
                return False
        else:
            print("无法读取ADC接口寄存器")
            return False
        
        # 启用ADC
        power_reg = self.read_reg(0x02)
        if power_reg is not None:
            power_reg |= (1 << 0)  # 启用ADC
            if not self.write_reg(0x02, power_reg):
                print("启用ADC失败")
                return False
        else:
            print("无法读取电源寄存器")
            return False
        
        self.is_open = True
        self.enabled = True
        print("ES8311麦克风模式初始化成功")
        return True

def set_references(recreate_func, encoder_obj=None):
    global recreate_main_page, encoder
    recreate_main_page = recreate_func
    if encoder_obj is not None:
        encoder = encoder_obj

def init_audio_codec():
    """初始化音频编解码器和I2S输入"""
    global audio_codec, mic_i2s, audio_buffer, pdm_buffer
    
    try:
        # 创建I2C接口（ES8311使用I2C地址0x18）
        # 根据引脚图，I2C使用GPIO2(SCL)和GPIO3(SDA)
        i2c = machine.I2C(0, scl=machine.Pin(2), sda=machine.Pin(3), freq=400000)
        
        # 初始化XL9555 GPIO扩展器 (I2C地址0x20)
        try:
            xl9555 = XL9555(i2c)
            
            # 配置XL9555的GPIO引脚
            # 假设麦克风电源控制引脚为GPIO0，麦克风时钟控制引脚为GPIO1
            xl9555.configure(0, 0)  # GPIO0设为输出
            xl9555.configure(1, 0)  # GPIO1设为输出
            
            # 开启麦克风电源
            xl9555.set_pin(0, 1)
            
            # 启用麦克风时钟
            xl9555.set_pin(1, 1)
            
            print("XL9555 GPIO扩展器初始化成功")
        except Exception as e:
            print(f"XL9555初始化错误: {e}")
            return False
        
        # 创建ES8311实例 (I2C地址0x18)
        audio_codec = ES8311(i2c)
        
        # 配置并打开音频编解码器
        # 针对MIC-4103-G-G00麦克风进行优化配置
        success = audio_codec.open_mic_mode(bits=16, channels=1, sample_rate=16000, mic_model="MIC-4103-G-G00")
        
        if not success:
            print("ES8311麦克风模式初始化失败")
            return False
        
        # 尝试初始化I2S音频输入
        try:
            # 使用标准machine.I2S接收模式，配置为PDM麦克风输入
            # 根据引脚图和ES8311配置I2S引脚
            # PDM麦克风只能工作在16kHz，使用I2S通道0
            mic_i2s = I2S(
                0,  # I2S ID 必须为0 (根据PDM.cpp中的MIC_I2S_PORT定义)
                sck=Pin(11),     # 串行时钟 (GPIO11)
                ws=Pin(18),      # 左右时钟 (GPIO18)
                sd=Pin(17),      # 串行数据输入 (GPIO17) - 用于麦克风输入
                mode=I2S.RX,     # 接收模式
                bits=16,
                format=I2S.MONO,
                rate=16000,      # 16kHz采样率 (根据PDM.cpp中的MIC_I2S_SAMPLE_RATE)
                ibuf=1024,       # 输入缓冲区大小
                # 注意：标准MicroPython I2S不支持PDM模式，我们使用RX模式来获取原始数据
            )
            audio_buffer = bytearray(1024)  # 1KB缓冲区
            pdm_buffer = bytearray(512)     # PDM数据缓冲区
            
            print("I2S音频输入初始化成功")
        except Exception as i2s_error:
            print(f"I2S初始化失败: {i2s_error}")
            print("使用模拟数据模式")
            mic_i2s = None
            audio_buffer = None
            pdm_buffer = None
        
        print("音频编解码器初始化成功")
        return True
            
    except Exception as e:
        print(f"音频编解码器初始化错误: {e}")
        return False

# ES8311类定义（基于ES8311 driver）
class ES8311:
    def __init__(self, i2c, i2c_addr=0x18):
        self.i2c = i2c
        self.i2c_addr = i2c_addr
        self.is_open = False
        self.enabled = False
        self.sample_rate = 16000
        self.bits = 16
        
    def write_reg(self, reg, value):
        """Write a value to an ES8311 register"""
        try:
            self.i2c.writeto_mem(self.i2c_addr, reg, bytes([value]))
            return True
        except OSError:
            return False

    def read_reg(self, reg):
        """Read a value from an ES8311 register"""
        try:
            return self.i2c.readfrom_mem(self.i2c_addr, reg, 1)[0]
        except OSError:
            return None
    
    def config_fmt(self, fmt):
        """配置I2S格式"""
        dac_iface = self.read_reg(0x09)
        adc_iface = self.read_reg(0x0A)
        
        if dac_iface is None or adc_iface is None:
            print("无法读取I2S接口寄存器")
            return False
        
        # 正常I2S格式
        dac_iface &= 0xFC
        adc_iface &= 0xFC
        
        return self.write_reg(0x09, dac_iface) and self.write_reg(0x0A, adc_iface)
        
    def set_bits_per_sample(self, bits):
        """设置采样位深度"""
        self.bits = bits
        dac_iface = self.read_reg(0x09)
        adc_iface = self.read_reg(0x0A)
        
        if dac_iface is None or adc_iface is None:
            print("无法读取I2S接口寄存器")
            return False
            
        if bits == 16:
            dac_iface |= 0x0c
            adc_iface |= 0x0c
        elif bits == 24:
            dac_iface |= 0x0f
            adc_iface |= 0x0f
        
        return self.write_reg(0x09, dac_iface) and self.write_reg(0x0A, adc_iface)
    
    def set_rate(self, sample_rate):
        """设置采样率"""
        self.sample_rate = sample_rate
        # 设置采样率的具体实现依赖于ES8311的时钟配置
        # 这里简化处理，使用已知的工作配置
        
        success = True
        
        # 16kHz采样率配置
        if sample_rate == 16000:
            # 设置时钟管理器
            success &= self.write_reg(0x01, 0x03)  # 时钟管理
            success &= self.write_reg(0x02, 0x40)  # 时钟分频
            success &= self.write_reg(0x03, 0x0B)  # 时钟配置
            success &= self.write_reg(0x04, 0x03)  # 时钟配置
            success &= self.write_reg(0x05, 0xFF)  # 时钟配置
            success &= self.write_reg(0x06, 0x00)  # 时钟配置
            success &= self.write_reg(0x07, 0x01)  # 时钟配置
        else:
            # 默认配置
            success &= self.write_reg(0x01, 0x03)
            success &= self.write_reg(0x02, 0x40)
            
        return success
            
    def open_mic_mode(self, bits=16, channels=1, sample_rate=16000):
        """打开麦克风模式"""
        if self.is_open:
            return True
        
        try:
            # 基本寄存器配置
            self.write_reg(0x44, 0x08)  # GPIO配置
            self.write_reg(0x44, 0x08)  # 重复写入确保可靠性
            
            # 复位芯片
            self.write_reg(0x00, 0x80)
            time.sleep(0.1)  # 等待复位完成
            
            # 配置基本参数
            if not self.set_bits_per_sample(bits):
                print("设置采样位深度失败")
                return False
                
            if not self.set_rate(sample_rate):
                print("设置采样率失败")
                return False
                
            if not self.config_fmt(0):  # 正常I2S格式
                print("配置I2S格式失败")
                return False
            
            # 配置为麦克风输入模式
            # 系统寄存器配置
            self.write_reg(0x0B, 0x40)  # 系统寄存器 - 启用ADC
            self.write_reg(0x0C, 0x00)
            self.write_reg(0x0D, 0x01)
            self.write_reg(0x0E, 0x02)
            self.write_reg(0x10, 0x00)
            self.write_reg(0x11, 0x00)
            self.write_reg(0x12, 0x00)
            self.write_reg(0x14, 0x1A)
            
            # ADC配置
            self.write_reg(0x15, 0x40)  # ADC控制
            self.write_reg(0x16, 0x24)  # ADC采样率
            self.write_reg(0x17, 0xBF)  # ADC配置
            self.write_reg(0x31, 0x00)  # DAC寄存器初始化
            self.write_reg(0x32, 0x00)
            self.write_reg(0x37, 0x10)
            
            # 配置I2S为输入模式
            adc_iface_value = self.read_reg(0x0A)
            if adc_iface_value is not None:
                adc_iface_value |= (1 << 6)  # 启用ADC I2S
                success = self.write_reg(0x0A, adc_iface_value)
                if not success:
                    print("配置ADC I2S接口失败")
                    return False
            else:
                print("无法读取ADC接口寄存器")
                return False
            
            # 启动系统
            self.write_reg(0x0B, 0x4F)  # 启动系统，启用ADC
            
            # 等待系统稳定
            time.sleep(0.1)
            
            self.is_open = True
            print("ES8311麦克风模式配置成功")
            return True
            
        except Exception as e:
            print(f"ES8311麦克风模式配置错误: {e}")
            return False

# 音频级别可视化相关变量
audio_bars = []
audio_levels = [0] * 16  # 存储16个音频条的级别
max_bars = 16
bar_width = 10
bar_spacing = 3
visualization_area_y = 120
visualization_area_height = 100

# 全局音频数据缓存
last_audio_level = 0
last_update_time = 0
audio_data_cache = None
audio_update_interval = 0.05  # 50ms更新间隔

def pdm_to_pcm(pdm_data, sample_rate=16000):
    """
    将PDM数据转换为PCM数据
    PDM是一种1位数字音频格式，需要转换为16位PCM进行分析
    """
    if not pdm_data or len(pdm_data) < 4:
        return None
        
    # 简化的PDM到PCM转换
    # 在实际应用中，这个转换会更复杂，需要使用滤波器
    pcm_data = bytearray(len(pdm_data) // 8)  # PDM是1位，PCM是16位，所以PCM数据量是PDM的1/16
    
    # 简单的PDM解码 - 使用积分器将1位PDM数据转换为多位PCM数据
    accumulator = 0
    bit_index = 0
    pcm_index = 0
    
    for byte_index in range(len(pdm_data)):
        byte_value = pdm_data[byte_index]
        
        # 处理每个字节的8位
        for bit_pos in range(8):
            if bit_index % 64 == 0:  # 每64位输出一个PCM样本
                # 限幅
                if accumulator > 32767:
                    accumulator = 32767
                elif accumulator < -32768:
                    accumulator = -32768
                
                # 存储PCM样本（小端序）
                pcm_data[pcm_index] = accumulator & 0xFF
                if pcm_index + 1 < len(pcm_data):
                    pcm_data[pcm_index + 1] = (accumulator >> 8) & 0xFF
                pcm_index += 2
                
                accumulator = 0
                if pcm_index >= len(pcm_data):
                    break
            
            # 提取PDM位 (LSB first)
            pdm_bit = (byte_value >> bit_pos) & 1
            # 积分器 - 简单的1阶低通滤波器
            if pdm_bit:
                accumulator += 512  # 正脉冲，增加累加器
            else:
                accumulator -= 512  # 负脉冲，减少累加器
                
            bit_index += 1
        
        if pcm_index >= len(pcm_data):
            break
    
    return pcm_data

def calculate_audio_level(audio_data):
    """计算音频数据的RMS级别"""
    if not audio_data or len(audio_data) < 2:
        return 0
    
    # 计算RMS（Root Mean Square）音频级别
    sum_squares = 0
    count = 0
    
    for i in range(0, len(audio_data) - 1, 2):
        if i + 1 < len(audio_data):
            # 16位音频数据，小端序
            sample = audio_data[i] | (audio_data[i + 1] << 8)
            # 转换为有符号数
            if sample >= 0x8000:
                sample -= 0x10000
            sum_squares += sample * sample
            count += 1
    
    if count == 0:
        return 0
    
    rms = math.sqrt(sum_squares / count)
    # 归一化到0-100范围
    level = int((rms / 32768.0) * 100)
    return max(0, min(100, level))

def read_microphone_data():
    """从I2S读取PDM麦克风音频数据"""
    global mic_i2s, audio_buffer, pdm_buffer
    
    if mic_i2s is None or pdm_buffer is None:
        return None
    
    try:
        # 读取PDM数据
        bytes_read = mic_i2s.readinto(pdm_buffer)
        if bytes_read > 0:
            # 将PDM数据转换为PCM进行分析
            pcm_data = pdm_to_pcm(pdm_buffer[:bytes_read])
            return pcm_data
        return None
    except Exception as e:
        print(f"读取麦克风数据错误: {e}")
        return None

def get_audio_level(bar_index):
    """获取音频级别
    如果有真实的麦克风数据，则使用真实数据
    否则使用模拟的波形数据
    """
    global audio_levels, max_bars, mic_i2s, last_audio_level, audio_data_cache, last_update_time, audio_update_interval
    
    # 检查是否需要更新音频数据
    current_time = time.ticks_ms() / 1000.0
    
    # 如果I2S可用且距离上次更新超过指定间隔
    if mic_i2s is not None and (current_time - last_update_time >= audio_update_interval):
        try:
            # 分配一个小的缓冲区
            buffer_size = 512  # 512字节缓冲
            audio_buffer = bytearray(buffer_size)
            
            # 读取音频数据
            bytes_read = mic_i2s.readinto(audio_buffer)
            
            if bytes_read > 0:
                # 将读取的数据转换为音频级别
                # 这里使用简化的方法，实际应用中可能需要更复杂的处理
                # 计算音频数据的RMS（均方根）作为级别指示
                sum_squares = 0
                sample_count = 0
                
                # 转换为16位整数数组并计算RMS
                for i in range(0, bytes_read, 2):
                    if i+1 < bytes_read:
                        # 小端序，组合两个字节为16位整数
                        sample = audio_buffer[i] | (audio_buffer[i+1] << 8)
                        # 转换为有符号数
                        if sample > 32767:
                            sample -= 65536
                        
                        sum_squares += sample * sample
                        sample_count += 1
                
                if sample_count > 0:
                    # 计算RMS并归一化为0-100范围
                    rms = math.sqrt(sum_squares / sample_count)
                    # 归一化RMS值到0-100范围
                    level = min(100, int(rms * 100 / 32768))
                    
                    # 更新缓存和时间戳
                    last_audio_level = level
                    audio_data_cache = level
                    last_update_time = current_time
                    
                    # 为不同的条状图添加一些频率分离效果
                    # 这里简化为基于条状图索引的滤波效果
                    filter_factor = 0.5 + 0.5 * math.sin(bar_index * 0.5 + time.time() * 2)
                    filtered_level = int(level * filter_factor)
                    
                    return max(5, min(95, filtered_level))  # 保持最小值避免完全静音
        except Exception as e:
            print("读取I2S数据失败:", str(e))
    
    # 如果没有真实数据更新，使用之前的数据或模拟数据
    if audio_data_cache is not None:
        # 为不同的条状图添加一些频率分离效果
        filter_factor = 0.5 + 0.5 * math.sin(bar_index * 0.5 + time.time() * 2)
        filtered_level = int(audio_data_cache * filter_factor)
        return max(5, min(95, filtered_level))  # 保持最小值避免完全静音
    
    # 如果无法读取真实音频，使用模拟数据作为后备
    return get_simulated_audio_level(bar_index)

def get_simulated_audio_level(bar_index):
    """获取模拟音频级别（后备方案）"""
    # 每个条状图都有不同的变化模式
    current_time = time.time()
    
    # 为每个条状图添加不同的相位偏移，让它们不完全同步
    time_factor = (current_time + bar_index * 0.1) % 3  # 3秒周期，相位偏移
    
    # 使用多个波形的组合来模拟更自然的音频变化
    base_level = 0
    
    if time_factor < 0.5:
        # 短促脉冲
        base_level = random.randint(70, 100)
    elif time_factor < 1.2:
        # 中等持续声音，带有一些随机变化
        base_level = random.randint(40, 80) + int(10 * math.sin(time_factor * 3))
    elif time_factor < 2.0:
        # 过渡期，有波动
        base_level = random.randint(20, 60) + int(15 * math.sin(time_factor * 2 + 1))
    else:
        # 背景噪声，轻微起伏
        base_level = random.randint(5, 25) + int(10 * math.sin(time_factor * 4 + 2))
    
    # 为每个条状图添加一些随机性，但保持基本趋势
    noise = random.randint(-10, 10)
    level = max(0, min(100, base_level + noise))
    
    return level

def create_audio_bars(parent):
    global audio_bars
    
    # 清空之前的条状图
    audio_bars.clear()
    
    # 计算总宽度和起始位置（相对于父容器）
    total_width = max_bars * bar_width + (max_bars - 1) * bar_spacing
    start_x = (300 - total_width) // 2  # 容器宽度300，居中显示
    
    # 创建音频条状图
    for i in range(max_bars):
        bar = lv.obj(parent)
        bar.set_size(bar_width, visualization_area_height)  # 初始高度为最大高度
        bar.set_pos(start_x + i * (bar_width + bar_spacing), 0)  # Y位置从0开始（容器顶部）
        
        # 设置条的样式
        bar.set_style_bg_color(lv.color_hex(0x00ff00), 0)  # 绿色
        bar.set_style_bg_opa(lv.OPA.COVER, 0)
        bar.set_style_radius(2, 0)  # 圆角
        bar.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
        
        audio_bars.append(bar)
    
    return audio_bars

def update_audio_bars(bar_index):
    """更新音频可视化条形图
    bar_index: 当前需要更新的条形图索引
    """
    # 获取整体音频级别
    global_level = get_audio_level(bar_index)
    
    # 更新每个条的高度（固定位置，上下起伏）
    for i, bar in enumerate(audio_bars):
        # 获取每个条自己的音频级别
        # 通过添加相位偏移来模拟频谱分析
        # 当前条使用传入的bar_index，其他条使用各自的索引
        current_level = get_audio_level(i)
        
        # 为每个条添加一些随机变化，模拟真实音频频谱
        # 不同条使用不同的偏移和比例
        bar_offset = (i - max_bars // 2) * 2  # 中心条偏移较小，两边偏移较大
        bar_factor = 0.8 + 0.4 * (i / max_bars)  # 不同条的比例因子
        
        # 为每个条添加不同的频率响应模拟
        import random
        time_factor = time.time() % 1.0  # 1秒循环
        phase_offset = i * 0.2 + time_factor * 2  # 每条有不同的相位偏移
        frequency_response = 0.5 + 0.5 * math.sin(phase_offset)
        
        # 计算当前条的高度
        adjusted_level = min(100, max(0, global_level * bar_factor * frequency_response + bar_offset))
        height = int((adjusted_level / 100.0) * visualization_area_height)
        
        if height < 3:
            height = 3  # 最小高度，避免看不见
        
        # 设置条的高度和位置（从底部向上）
        bar.set_size(bar_width, height)
        bar.set_pos(bar.get_x(), visualization_area_height - height)
        
        # 根据高度设置颜色
        if height > visualization_area_height * 0.7:
            bar.set_style_bg_color(lv.color_hex(0xff0000), 0)  # 红色 - 高音量
        elif height > visualization_area_height * 0.4:
            bar.set_style_bg_color(lv.color_hex(0xffff00), 0)  # 黄色 - 中等音量
        else:
            bar.set_style_bg_color(lv.color_hex(0x00ff00), 0)  # 绿色 - 低音量


def microphone():
    # Clear all current screen elements
    scr = lv.screen_active()
    # Remove all children from the screen
    while True:
        child = scr.get_child(0)
        if child is None:
            break
        child.delete()
    
    # Set background to black
    scr.set_style_bg_color(lv.color_hex(0x000000), 0)
    
    # 初始化ES8311音频编解码器和I2S
    if not init_audio_codec():
        print("音频编解码器初始化失败")
    
    # 添加详细初始化状态显示
    init_status_label = lv.label(scr)
    init_status_label.set_style_text_font(lv.font_montserrat_12, 0)
    
    if audio_codec and audio_codec.is_open:
        if mic_i2s is not None:
            init_status_label.set_text("PDM MIC: ACTIVE")
            init_status_label.set_style_text_color(lv.color_hex(0x00ff00), 0)  # 绿色
        else:
            init_status_label.set_text("PDM MIC: SIMULATED")
            init_status_label.set_style_text_color(lv.color_hex(0xffff00), 0)  # 黄色
    else:
        init_status_label.set_text("PDM MIC: ERROR")
        init_status_label.set_style_text_color(lv.color_hex(0xff0000), 0)  # 红色
        
    init_status_label.set_pos(10, 5)  # 顶部左侧
    
    # 添加I2S状态显示
    i2s_status_label = lv.label(scr)
    i2s_status_label.set_style_text_font(lv.font_montserrat_10, 0)
    
    if mic_i2s is not None:
        i2s_status_label.set_text("I2S: SCK=11, WS=17, SD=17, 16kHz/16-bit/Mono, RX Buffer=1024")
        i2s_status_label.set_style_text_color(lv.color_hex(0x00ff00), 0)  # 绿色
    else:
        i2s_status_label.set_text("I2S: FALLBACK MODE")
        i2s_status_label.set_style_text_color(lv.color_hex(0xffff00), 0)  # 黄色
        
    i2s_status_label.set_pos(10, 20)  # 顶部左侧，在初始化状态下方
    
    # 添加I2C状态显示
    i2c_status_label = lv.label(scr)
    i2c_status_label.set_style_text_font(lv.font_montserrat_10, 0)
    
    if audio_codec and audio_codec.is_open:
        i2c_status_label.set_text("I2C: SDA=3, SCL=2, ADDR=0x18")
        i2c_status_label.set_style_text_color(lv.color_hex(0x00ff00), 0)  # 绿色
    else:
        i2c_status_label.set_text("I2C: FALLBACK MODE")
        i2c_status_label.set_style_text_color(lv.color_hex(0xffff00), 0)  # 黄色
        
    i2c_status_label.set_pos(10, 35)  # 顶部左侧，在I2S状态下方
    
    # Create a separate selection box object that will overlay on top of items
    selection_box = lv.obj(scr)
    selection_box.set_style_border_width(4, 0)  # Thick white border
    selection_box.set_style_border_color(lv.color_hex(0xffffff), 0)
    selection_box.set_style_border_opa(lv.OPA.COVER, 0)
    selection_box.set_style_bg_opa(lv.OPA.TRANSP, 0)  # Transparent background
    selection_box.set_style_radius(3, 0)  # Slightly rounded corners
    selection_box.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)  # Disable scrollbar

    # Create labels for each selection item (no containers needed)
    selection_items = []
    item_positions = []
    item_sizes = []  # Store different sizes for selection box
    
    # Item 0: Back button (lv.SYMBOL.LEFT)
    symbol_left_label = lv.label(scr)
    symbol_left_label.set_text(lv.SYMBOL.LEFT)
    symbol_left_label.set_style_text_font(lv.font_montserrat_20, 0)
    symbol_left_label.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    symbol_left_label.set_pos(20, 55)
    selection_items.append(symbol_left_label)
    item_positions.append((12, 50))  # Adjusted position: left 3px total, up 4px total
    item_sizes.append((30, 30))  # Smaller size for back button
    
    # 创建音频可视化区域
    audio_container = lv.obj(scr)
    audio_container.set_size(300, visualization_area_height + 40)
    audio_container.set_pos(10, visualization_area_y - 20)
    audio_container.set_style_bg_color(lv.color_hex(0x111111), 0)  # 深灰背景
    audio_container.set_style_bg_opa(lv.OPA.COVER, 0)
    audio_container.set_style_radius(10, 0)  # 圆角
    audio_container.set_style_border_width(2, 0)
    audio_container.set_style_border_color(lv.color_hex(0x444444), 0)
    audio_container.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
    
    # 添加标题
    title_label = lv.label(scr)
    title_label.set_text("Microphone")
    title_label.set_style_text_font(lv.font_montserrat_20, 0)
    title_label.set_style_text_color(lv.color_hex(0xffffff), 0)  # White text
    title_label.set_pos(110, 20)  # 居中显示
    
    # 添加状态显示
    status_label = lv.label(scr)
    status_label.set_text("LISTENING...")
    status_label.set_style_text_font(lv.font_montserrat_14, 0)
    status_label.set_style_text_color(lv.color_hex(0x00ff00), 0)  # Green text
    status_label.set_pos(130, 90)
    
    # 创建音频条状图
    create_audio_bars(audio_container)
    
    # Position selection box over first item (back button) by default
    current_selection = 0
    x, y = item_positions[current_selection]
    width, height = item_sizes[current_selection]
    selection_box.set_size(width, height)
    selection_box.set_pos(x, y)
    
    # Handle encoder input in setting page
    while True:
        key = encoder.update()
        
        if key == "down":
            # Move selection down
            old_selection = current_selection
            current_selection = (current_selection + 1) % 1
            
        elif key == "up":
            # Move selection up
            old_selection = current_selection
            current_selection = (current_selection - 1) % 1
            

        elif key == "enter":
            # Check if back button is selected
            if current_selection == 0:
                break  # Exit the loop to return to main page
            # For other selections, you can add specific handling here
            if current_selection == 1:
                pass
        
        # 更新音频可视化
        update_audio_bars(0)  # 传递一个参数，条形图的索引（从0开始）
        time.sleep_ms(50)  # 50ms更新一次，约20FPS
            
                
    # Return to original page by recreating all elements
    recreate_main_page()
