from micropython import const
import time

REG_CFG = const(0x01)
REG_INT_STAT = const(0x02)
REG_KEY_LCK_EC = const(0x03)
REG_KEY_EVENT_A = const(0x04)
REG_KP_GPIO1 = const(0x1D)
REG_KP_GPIO2 = const(0x1E)
REG_KP_GPIO3 = const(0x1F)

CFG_INT_CFG = const(1 << 4)
CFG_OVR_FLOW_IEN = const(1 << 3)
CFG_KE_IEN = const(1 << 0)

TCA8418_ADDR = const(0x34)
FIFO_SIZE = 10

RAW_KEY_MAP = {
    0x01: 'q', 0x02: 'w', 0x03: 'e', 0x04: 'r', 0x05: 't',
    0x06: 'y', 0x07: 'u', 0x08: 'i', 0x09: 'o', 0x0A: 'p',
    0x0B: 'a', 0x0C: 's', 0x0D: 'd', 0x0E: 'f', 0x0F: 'g',
    0x10: 'h', 0x11: 'j', 0x12: 'k', 0x13: 'l', 0x14: '\n',
    
    0x15: '', 0x16: 'z', 0x17: 'x', 0x18: 'c', 0x19: 'v',
    0x1A: 'b', 0x1B: 'n', 0x1C: 'm', 0x1D: 'CAP', 0x1e: '\b',
    0x1f: ' '
}

Q_P_NUM_MAP = {
    'q': '1', 'w': '2', 'e': '3', 'r': '4', 't': '5',
    'y': '6', 'u': '7', 'i': '8', 'o': '9', 'p': '0',
    
    'a': '*', 's': '/', 'd': '+', 'f': '-', 'g': '=',
    'h': ':', 'j': "'", 'k': '"', 'l': '@',
    
    'z': '-', 'x': '$', 'c': ';', 'v': '?', 'b': '!',
    'n': ',', 'm': '.'
}

rows_pin = [0, 1, 2, 3]
cols_pin = [8, 9, 10, 11, 12, 13, 14, 15, 16, 17]


class TCA8418:
    def __init__(self, i2c, address=TCA8418_ADDR, rows=4, cols=10):
        self.i2c = i2c
        self.addr = address
        self.rows = rows
        self.cols = cols
        self._init_device()
        self._pressed_keys = set() 

    def _write_reg(self, reg, value):
        self.i2c.writeto_mem(self.addr, reg, bytes([value]))

    def _read_reg(self, reg, n=1):
        return self.i2c.readfrom_mem(self.addr, reg, n)

    def _init_device(self):
        cfg = CFG_INT_CFG | CFG_OVR_FLOW_IEN | CFG_KE_IEN
        self._write_reg(REG_CFG, cfg)
        self._write_reg(REG_INT_STAT, 0xFF)
        time.sleep_ms(5)

    def setup_keypad(self, rows_pins=rows_pin, cols_pins=cols_pin):
        mask = 0
        for p in rows_pins + cols_pins:
            if 0 <= p <= 17:
                mask |= (1 << p)

        self._write_reg(REG_KP_GPIO1, mask & 0xFF)
        self._write_reg(REG_KP_GPIO2, (mask >> 8) & 0xFF)
        self._write_reg(REG_KP_GPIO3, (mask >> 16) & 0xFF)
        self._write_reg(REG_INT_STAT, 0xFF)
        time.sleep_ms(5)

    def get_key_events(self):
        out = []
        klec = self._read_reg(REG_KEY_LCK_EC)[0]
        count = klec & 0x0F
        if count == 0:
            return out

        for i in range(FIFO_SIZE):
            val = self._read_reg(REG_KEY_EVENT_A + i)[0]
            if val == 0:
                continue
            pressed = bool(val & 0x80)
            raw = val & 0x7F
            out.append((raw, pressed))

        self._write_reg(REG_INT_STAT, 0xFF)
        return out

    def get_key(self, delay_ms=50):
        events = self.get_key_events()

        for raw, pressed in events:
            if pressed:
                self._pressed_keys.add(raw)
            else:
                self._pressed_keys.discard(raw)

        self._caps_on = 0x1D in self._pressed_keys  # CAP
        self._num_on = 0x1F in self._pressed_keys   # SPACE

        output = []
        for raw in self._pressed_keys:
            key_char = RAW_KEY_MAP.get(raw)
            if not key_char or key_char == 'CAP':
                continue 
            if self._num_on and key_char in Q_P_NUM_MAP:
                key_char = Q_P_NUM_MAP[key_char]
            elif self._caps_on and key_char.isalpha():
                key_char = key_char.upper()

            output.append(key_char)

        if output:
            return ' '.join(output)
#             print())

        time.sleep(0.11)

