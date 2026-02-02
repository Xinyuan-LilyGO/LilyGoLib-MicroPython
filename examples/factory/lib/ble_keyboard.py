import lvgl as lv
import time
import _thread
from hid_services import Keyboard
import keypad
from machine import Pin, I2C

recreate_main_page = None
encoder = None

class Device:
    def __init__(self, state_label=None):
        self.key0 = 0x00
        self.key1 = 0x00
        self.key2 = 0x00
        self.key3 = 0x00
        self.modifier = 0x00  
        self.last_advertise_time = 0
        self.advertise_interval = 30  
        self.max_advertise_time = 120 
        self.advertise_start_time = 0
        self.caps_lock = False
        self.state_label = state_label

        try:
            i2c = I2C(0, scl=Pin(2), sda=Pin(3), freq=400000)
            self.kb = keypad.TCA8418(i2c)
            self.kb.setup_keypad()
            #print("Keypad initialized successfully")
        except Exception as e:
            #print(f"Keypad initialization failed: {e}")
            self.kb = None

        try:
            self.keyboard = Keyboard("Keyboard")
            # Set a callback function to catch changes of device state
            self.keyboard.set_state_change_callback(self.keyboard_state_callback)
            # Start our device
            self.keyboard.start()
            #print("BLE Keyboard initialized successfully")
        except Exception as e:
            #print(f"BLE Keyboard initialization failed: {e}")
            self.keyboard = None

    # Function that catches device status events
    def keyboard_state_callback(self):
        if self.keyboard is None:
            return
            
        state = self.keyboard.get_state()
        #print(f"Keyboard state changed: {state}")
        
        if state is Keyboard.DEVICE_IDLE:
            print("Device is idle")
        elif state is Keyboard.DEVICE_ADVERTISING:
            print("Device is advertising")
        elif state is Keyboard.DEVICE_CONNECTED:
            if self.state_label: 
                self.state_label.set_text("STATE: Connected")
            print("Device is connected")
            self.keyboard.stop_advertising()
        else:
            print(f"Unknown device state: {state}")

    def keyboard_event_callback(self, bytes):
        pass
        #print("Keyboard state callback with bytes: ", bytes)

    def start_advertising_with_retry(self):
        if self.keyboard is None:
            #print("Keyboard not initialized, cannot advertise")
            return False
            
        current_time = time.time()
        if self.keyboard.get_state() is Keyboard.DEVICE_ADVERTISING:
            if current_time - self.advertise_start_time > self.max_advertise_time:
                #print("Max advertise time reached, restarting...")
                self.keyboard.stop_advertising()
                time.sleep(1)

        if (self.keyboard.get_state() is Keyboard.DEVICE_IDLE and 
            current_time - self.last_advertise_time > self.advertise_interval):
            #print("Starting BLE advertising...")
            try:
                self.keyboard.start_advertising()
                self.last_advertise_time = current_time
                self.advertise_start_time = current_time
                return True
            except Exception as e:
                #print(f"Advertising failed: {e}")
                return False
        return False

    # Convert keypad character to HID keycode with modifier support
    def char_to_hid_code(self, char):
        modifier = 0x00
        if char.isupper():
            modifier = 0x02 
            char = char.lower()

        if char == 'w': return (0x1A, modifier)
        if char == 'a': return (0x04, modifier)
        if char == 's': return (0x16, modifier)
        if char == 'd': return (0x07, modifier)
        if char == 'q': return (0x14, modifier)
        if char == 'e': return (0x08, modifier)
        if char == 'r': return (0x15, modifier)
        if char == 't': return (0x17, modifier)
        if char == 'y': return (0x1C, modifier)
        if char == 'u': return (0x18, modifier)
        if char == 'i': return (0x0C, modifier)
        if char == 'o': return (0x12, modifier)
        if char == 'p': return (0x13, modifier)
        if char == 'f': return (0x09, modifier)
        if char == 'g': return (0x0A, modifier)
        if char == 'h': return (0x0B, modifier)
        if char == 'j': return (0x0D, modifier)
        if char == 'k': return (0x0E, modifier)
        if char == 'l': return (0x0F, modifier)
        if char == 'z': return (0x1D, modifier)
        if char == 'x': return (0x1B, modifier)
        if char == 'c': return (0x06, modifier)
        if char == 'v': return (0x19, modifier)
        if char == 'b': return (0x05, modifier)
        if char == 'n': return (0x11, modifier)
        if char == 'm': return (0x10, modifier)

        if char == '1': return (0x1E, modifier)
        if char == '2': return (0x1F, modifier)
        if char == '3': return (0x20, modifier)
        if char == '4': return (0x21, modifier)
        if char == '5': return (0x22, modifier)
        if char == '6': return (0x23, modifier)
        if char == '7': return (0x24, modifier)
        if char == '8': return (0x25, modifier)
        if char == '9': return (0x26, modifier)
        if char == '0': return (0x27, modifier)

        if char == ' ': return (0x2C, 0x00)
        if char == '\n': return (0x28, 0x00)
        if char == '\b': return (0x2A, 0x00) 
        if char == '*': return (0x25, 0x00)
        if char == '/': return (0x24, 0x00)
        if char == '+': return (0x2E, 0x00)
        if char == '-': return (0x2D, 0x00)
        if char == '=': return (0x2E, 0x00)

        if char == ':': return (0x33, 0x02) 
        if char == "'": return (0x34, 0x00)
        if char == '"': return (0x34, 0x02)  
        if char == '@': return (0x1F, 0x02)  
        if char == '$': return (0x21, 0x02) 
        if char == ';': return (0x33, 0x00)
        if char == '?': return (0x38, 0x02) 
        if char == '!': return (0x1E, 0x02)  
        if char == ',': return (0x36, 0x00)
        if char == '.': return (0x37, 0x00)
        if char == '<': return (0x36, 0x02)  
        if char == '>': return (0x37, 0x02) 
        if char == '(': return (0x26, 0x02)  
        if char == ')': return (0x27, 0x02)  
        
        if char.lower() == 'caps': 
            self.caps_lock = not self.caps_lock
            print(f"Caps Lock: {'ON' if self.caps_lock else 'OFF'}")
            return (0x39, 0x00)  
        
        if char.lower() == 'shift': return (0x00, 0x02)  
        if char.lower() == 'ctrl': return (0x00, 0x01)   
        if char.lower() == 'alt': return (0x00, 0x04)    
        if char.lower() == 'tab': return (0x2B, 0x00)    
        if char.lower() == 'esc': return (0x29, 0x00)   
        if char.lower() == 'backspace': return (0x2A, 0x00)  
        
        return (0x00, 0x00)

    def process_keypad_input(self, key_string):
        if key_string is None:
            return ([0x00, 0x00, 0x00, 0x00], 0x00)
        
        if key_string == '\n':  
            return ([0x28, 0x00, 0x00, 0x00], 0x00)
        elif key_string == ' ':  
            return ([0x2C, 0x00, 0x00, 0x00], 0x00)
        elif key_string == '\b':  
            return ([0x2A, 0x00, 0x00, 0x00], 0x00)

        keys = key_string.strip().split()
        key_codes = [0x00, 0x00, 0x00, 0x00]
        total_modifier = 0x00
        
        for i, key in enumerate(keys[:4]): 
            if key:
                key_code, modifier = self.char_to_hid_code(key)
                key_codes[i] = key_code
                total_modifier |= modifier 
        
        return key_codes, total_modifier

    def send_key_report(self, key_codes, modifier=0x00):
        if self.keyboard is None:
            return False
            
        try:
            if self.keyboard.get_state() is Keyboard.DEVICE_CONNECTED:
                if modifier:
                    self.keyboard.set_modifiers(
                        left_control=(modifier & 0x01) >> 0,
                        left_shift=(modifier & 0x02) >> 1,
                        left_alt=(modifier & 0x04) >> 2,
                        left_gui=(modifier & 0x08) >> 3
                    )
                else:
                    self.keyboard.set_modifiers(0, 0, 0, 0)
                
                self.keyboard.set_keys(key_codes[0], key_codes[1], key_codes[2], key_codes[3])
                self.keyboard.notify_hid_report()
                
                modifier_str = ""
                if modifier & 0x02:
                    modifier_str += "Shift+"
                if modifier & 0x01:
                    modifier_str += "Ctrl+"
                if modifier & 0x04:
                    modifier_str += "Alt+"
                    
                #print(f"Sending keys: {modifier_str}{[hex(k) for k in key_codes if k != 0]}")
                return True
            else:
                #print("Device not connected, cannot send key report")
                return False
        except Exception as e:
            #print(f"Error sending key report: {e}")
            return False

    def clear_keys(self):
        self.key0, self.key1, self.key2, self.key3 = 0x00, 0x00, 0x00, 0x00
        self.modifier = 0x00
        if self.keyboard and self.keyboard.get_state() is Keyboard.DEVICE_CONNECTED:
            self.keyboard.set_keys(0x00, 0x00, 0x00, 0x00)
            self.keyboard.set_modifiers(0, 0, 0, 0)
            self.keyboard.notify_hid_report()

    def process_keyboard(self):
        if self.keyboard and self.keyboard.get_state() is Keyboard.DEVICE_IDLE:
            self.start_advertising_with_retry()

        key_string = None
        if self.kb:
            try:
                key_string = self.kb.get_key()
            except Exception as e:
                pass
                #print(f"Error reading keypad: {e}")

        if key_string is not None:
            print(f"Key pressed: {key_string}")
            key_codes, modifier = self.process_keypad_input(key_string)
            self.key0, self.key1, self.key2, self.key3 = key_codes
            self.modifier = modifier

            if any(key_codes) or modifier:
                if not self.send_key_report(key_codes, modifier):
                    if self.keyboard and self.keyboard.get_state() is Keyboard.DEVICE_IDLE:
                        #print("Key pressed but device not connected, starting advertising...")
                        self.start_advertising_with_retry()
            else:
                self.clear_keys()
        else:
            if any([self.key0, self.key1, self.key2, self.key3]) or self.modifier:
                self.clear_keys()
        
        if self.keyboard and self.keyboard.get_state() is Keyboard.DEVICE_CONNECTED:
            return 20  
        else:
            return 100  

    def send_char(self, char):
        if self.keyboard is None:
            return
            
        if char == " ":
            mod = 0
            code = 0x2C
        elif ord("a") <= ord(char) <= ord("z"):
            mod = 0
            code = 0x04 + ord(char) - ord("a")
        elif ord("A") <= ord(char) <= ord("Z"):
            mod = 1
            code = 0x04 + ord(char) - ord("A")
        else:
            code, mod = self.char_to_hid_code(char)
            if code == 0x00:
                #print(f"Unsupported character: {char}")
                return

        self.keyboard.set_keys(code)
        self.keyboard.set_modifiers(left_shift=mod)
        self.keyboard.notify_hid_report()
        time.sleep_ms(2)

        self.keyboard.set_keys()
        self.keyboard.set_modifiers()
        self.keyboard.notify_hid_report()
        time.sleep_ms(2)

    def send_string(self, st):
        for c in st:
            self.send_char(c)
            
    def stop(self):
        if self.keyboard:
            self.keyboard.stop()


def set_references(recreate_func, encoder_obj=None):
    global recreate_main_page, encoder
    recreate_main_page = recreate_func
    if encoder_obj is not None:
        encoder = encoder_obj

def ble_keyboard():
    # Clear all current screen elements
    scr = lv.screen_active()
    # Remove all children from the screen
    while True:
        child = scr.get_child(0)
        if child is None:
            break
        child.delete()
    
    # Create the color object for screen test
    color_obj = lv.obj(scr)
    color_obj.set_size(480, 320)  # Match screen size after rotation
    color_obj.align(lv.ALIGN.CENTER, 0, 0)
    
    # Create inversion style similar to images
    inv_style = lv.style_t()
    inv_style.init()
    inv_style.set_bg_opa(lv.OPA.COVER)
    inv_style.set_blend_mode(lv.BLEND_MODE.DIFFERENCE)
    color_obj.add_style(inv_style, 0)
    
    color_obj.set_style_bg_color(lv.color_hex(0xffffff), 0)
    
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

    # Add black rectangle in the middle left
    black_rect = lv.obj(scr)
    black_rect.set_size(120, 120)
    black_rect.set_pos(60, 110)
    black_rect.set_style_bg_color(lv.color_hex(0x000000), 0)
    black_rect.set_style_border_width(2, 0)
    black_rect.set_style_border_color(lv.color_hex(0xffffff), 0)

    # Add 100% text inside black rectangle
    percentage_label = lv.label(black_rect)
    percentage_label.set_text("100%")
    percentage_label.set_style_text_font(lv.font_montserrat_28, 0)  # Use smaller font that's more likely available
    percentage_label.set_style_text_color(lv.color_hex(0xffffff), 0)
    percentage_label.align(lv.ALIGN.CENTER, 0, 0)

    # Add text on the right side
    # Model line
    model_label = lv.label(scr)
    model_label.set_text("Model: BLE Keyboard Mode")
    model_label.set_style_text_font(lv.font_montserrat_18, 0)
    model_label.set_style_text_color(lv.color_hex(0xffffff), 0)
    model_label.set_pos(200, 120)

    # DeviceName line
    device_name_label = lv.label(scr)
    device_name_label.set_text("DeviceName: Keyboard")
    device_name_label.set_style_text_font(lv.font_montserrat_18, 0)
    device_name_label.set_style_text_color(lv.color_hex(0xffffff), 0)
    device_name_label.set_pos(200, 160)

    # STATE line
    state_label = lv.label(scr)
    state_label.set_text("STATE: Disconnected")
    state_label.set_style_text_font(lv.font_montserrat_18, 0)
    state_label.set_style_text_color(lv.color_hex(0xffffff), 0)
    state_label.set_pos(200, 200)

    # Position selection box over first item (back button) by default
    current_selection = 0
    x, y = item_positions[current_selection]
    width, height = item_sizes[current_selection]
    selection_box.set_size(width, height)
    selection_box.set_pos(x, y)

    # Initialize BLE Keyboard Device
    d = Device(state_label)

    while True:
        lv.task_handler()
        
        delay_ms = d.process_keyboard()

        key = encoder.update()
        
        if key == "down":
            # Move selection down
            current_selection = (current_selection + 1) % 1
            # Move and resize selection box to new position
            x, y = item_positions[current_selection]
            width, height = item_sizes[current_selection]
            selection_box.set_size(width, height)
            selection_box.set_pos(x, y)
            
        elif key == "up":
            # Move selection up
            current_selection = (current_selection - 1) % 1
            # Move and resize selection box to new position
            x, y = item_positions[current_selection]
            width, height = item_sizes[current_selection]
            selection_box.set_size(width, height)
            selection_box.set_pos(x, y)
            
        elif key == "enter":
            # Check if back button is selected
            if current_selection == 0:
                if d.keyboard:
                    d.keyboard.stop()
                break  # Exit the loop to return to main page
        
        time.sleep_ms(delay_ms)
        
    # Clear the screen again to prepare for returning to original page
    scr = lv.screen_active()
    while True:
        child = scr.get_child(0)
        if child is None:
            break
        child.delete()
    
    # Return to original page by recreating all elements
    recreate_main_page()
