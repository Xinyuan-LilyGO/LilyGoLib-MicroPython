from machine import SPI, Pin, I2C
import sys
import lcd_bus
import st7796
import lvgl as lv
from micropython import const
import vibration
import _thread
import time
import fs_driver
import gc
import task_handler
import rotary

i2c = I2C(0, scl=Pin(2), sda=Pin(3), freq=400000)
vb = vibration.vibrationMotor(i2c)

def vibrate_motor():
    vb.vibrate(1, 200)

lv.init()

spi_bus = SPI.Bus(host = 1, mosi=34, miso=33, sck=35)
display_bus = lcd_bus.SPIBus(
    spi_bus=spi_bus,
    dc=37,
    cs=38,
    freq=80000000
)

# The rgb565_byte_swap parameter is likely causing the color inversion issue
# Setting it to False should fix the inversion
# We'll use the BYTE_ORDER_BGR to ensure correct color mapping
display = st7796.ST7796(
    data_bus=display_bus,
    display_width=320,
    display_height=480,
    reset_state=st7796.STATE_LOW,
    color_space=lv.COLOR_FORMAT.RGB565,
    color_byte_order=st7796.BYTE_ORDER_BGR,
    rgb565_byte_swap=True  # This should fix the color inversion
)

display.set_power(True)
display.init()
display.set_rotation(lv.DISPLAY_ROTATION._90)

# _thread.start_new_thread(vibrate_motor, ())

backlight_pin = Pin(42, Pin.OUT)
backlight_pin.value(1)

scr = lv.screen_active()
scr.set_style_bg_color(lv.color_hex(0xffffff), 0)  # Set background to white

fs_drv = lv.fs_drv_t()
fs_driver.fs_register(fs_drv, 'S')

task_handler.TaskHandler(33)

image_files = [
    'S:lib/bmp/img_logo_480x222.bmp',
#     'S:lib/bmp/img_radio.bmp',
    'S:lib/bmp/img_test.bmp',
    'S:lib/bmp/img_configuration.bmp',
    'S:lib/bmp/img_wifi.bmp',
    'S:lib/bmp/img_bluetooth.bmp',
    'S:lib/bmp/img_keyboard.bmp',
#     'S:lib/bmp/img_music.bmp',
    'S:lib/bmp/img_radio.bmp',
    'S:lib/bmp/img_msgchat.bmp',
    'S:lib/bmp/img_gps.bmp',
    'S:lib/bmp/img_monitoring.bmp',
    'S:lib/bmp/img_power.bmp',
#     'S:lib/bmp/img_microphone.bmp',
    'S:lib/bmp/img_gyroscope.bmp'
]

# Create logo image object
img_logo = lv.image(scr)
img_logo.set_src(image_files[0])
img_logo.align(lv.ALIGN.CENTER, 0, 0)

# Create a style that can invert colors
inv_style = lv.style_t()
inv_style.init()
# inv_style.set_bg_color(lv.color_hex(0xffffff))
inv_style.set_bg_opa(lv.OPA.COVER)
inv_style.set_blend_mode(lv.BLEND_MODE.DIFFERENCE)

# Apply inversion style to logo
img_logo.add_style(inv_style, 0)

gc.collect()
time.sleep(0.1)  # Show logo for 2 seconds

# Remove logo image
img_logo.delete()
gc.collect()
time.sleep(0.1)
    
# Skip displaying the other three images
# Directly proceed to color display after logo
gc.collect()
time.sleep(0.1)  # Keep logo shown for 2 seconds before proceeding

# Create a full-screen object for color display
color_obj = lv.obj(scr)
color_obj.set_size(500, 208)  # Match screen size after rotation
color_obj.set_pos(-10, 0)

bottom_color_obj = lv.obj(scr)
bottom_color_obj.set_size(500, 80)  # Match screen size after rotation
bottom_color_obj.set_pos(-10, 205)

# Create inversion style similar to images
inv_style = lv.style_t()
inv_style.init()
inv_style.set_bg_opa(lv.OPA.COVER)
inv_style.set_blend_mode(lv.BLEND_MODE.DIFFERENCE)
color_obj.add_style(inv_style, 0)
color_obj.set_style_bg_color(lv.color_hex(0xffffff), 0)
bottom_color_obj.add_style(inv_style, 0)
bottom_color_obj.set_style_bg_color(lv.color_hex(0xdcdcdc), 0)

# Add text to the bottom area
text_label = lv.label(scr)  # Put text_label back on screen instead of inside bottom_color_obj

# Define text list for rotary encoder switching
text_list = [
#     "NRF24",
    "Screen Test",
    "Setting",
    "Wireless",
    "BLE Keyboard",
    "Keyboard",
#     "Music",
    "LoRa",
    "LoRa Chat",
    "GPS",
    "Monitor",
    "Power"
#     "microphone",
#     "IMU"
]

current_text_index = 0  # Default to 0

# Create text style
text_style = lv.style_t()
text_style.init()
text_style.set_text_color(lv.color_hex(0xffffff))  # Black text
text_style.set_text_font(lv.font_montserrat_36)
text_style.set_blend_mode(lv.BLEND_MODE.NORMAL)  # Ensure normal blend mode
text_label.add_style(text_style, 0)

# Set initial text
text_label.set_text(text_list[current_text_index])

# Get bottom_color_obj's position and size to calculate text_label's position
# bottom_color_obj is at position (-10, 205) with size (500, 80)
# Calculate center position relative to screen: screen_width/2
# Y position should be bottom_color_obj's y + 2px margin
text_label.align_to(bottom_color_obj, lv.ALIGN.TOP_MID, 0, 2)

# Create four containers with gray background
start_x = 5  # Starting x position
start_y = 70  # Starting y position
container_width = 150
container_height = 125
spacing = 10
visible_containers = 3  # Number of containers visible on screen

total_containers = 11  # Total number of containers (14 real + 1 dummy for spacing)

# Create a list to store container references
containers = []

for i in range(total_containers):
    # Calculate x position for current container
    x_pos = start_x + i * (container_width + spacing)
    
    container = lv.obj(scr)
    container.set_size(container_width, container_height)  # Set size
    container.set_pos(x_pos, start_y)  # Set position
    
    if i < 10:  # Real containers with images
        container.set_style_bg_color(lv.color_hex(0xffffff), 0)  # Set background color to white
        container.set_style_bg_opa(lv.OPA.COVER, 0)  # Make background opaque
        container.set_style_radius(10, 0)  # Set corner radius to 10 pixels
        container.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)  # Disable scrollbars
        
        # Add shadow to create 3D effect
        container.set_style_shadow_width(5, 0)  # Shadow width
        container.set_style_shadow_color(lv.color_hex(0xdddddd), 0)  # Light gray shadow
        container.set_style_shadow_offset_y(3, 0)  # Shadow offset down
        container.set_style_shadow_offset_x(3, 0)  # Shadow offset right
        container.set_style_shadow_opa(lv.OPA._50, 0)  # Shadow opacity
        
        # Create image object inside container
        img = lv.image(container)
        img.set_src(image_files[i+1])  # Use images from index 1 onwards
        img.set_size(container_width, container_height)  # Set image size same as container
        img.align(lv.ALIGN.CENTER, 0, 0)  # Center image in container
        img.set_style_radius(13, 0)
        
        # Apply inversion style to image for correct color display
        inv_style = lv.style_t()
        inv_style.init()
        inv_style.set_bg_opa(lv.OPA.COVER)
        inv_style.set_blend_mode(lv.BLEND_MODE.DIFFERENCE)
        img.add_style(inv_style, 0)
    else:  # Dummy container (no image, just spacing)
        container.set_style_bg_opa(lv.OPA.TRANSP, 0)  # Make background transparent
        container.set_style_border_opa(lv.OPA.TRANSP, 0)  # No border
        container.set_style_shadow_opa(lv.OPA.TRANSP, 0)  # No shadow
    
    # Add container to the list
    containers.append(container)

# Add selection box to the first container by default
current_container_index = 0  # Index 0 is the first container (0-based)

# Create a selection box style object
selection_style = lv.style_t()
selection_style.init()
selection_style.set_border_width(3)  # Set border width to 3 pixels
selection_style.set_border_color(lv.color_hex(0xffffff))  # Set border color to red for visibility
selection_style.set_border_opa(lv.OPA.COVER)  # Make border fully opaque
selection_style.set_border_side(lv.BORDER_SIDE.FULL)  # Show border on all sides

# Function to add selection box style to a container
def add_selection_box(container):
    # Add the selection box style object to the container
    container.add_style(selection_style, 0)

# Function to remove selection box style from a container
def remove_selection_box(container):
    # Remove the selection box style object from the container
    container.remove_style(selection_style, 0)

# Add selection box to the first container
add_selection_box(containers[current_container_index])

# Initialize container position variables
current_container_index = 0  # Index of the currently selected container (0-13)
container_offset = 0  # Offset for container movement (0-14)

# Initialize rotary encoder
encoder = rotary.RotaryEncoder(40, 41, 7)

# Function to move all containers based on offset with proper wrapping
def move_containers(offset):
    for i, container in enumerate(containers):
        # Calculate new x position with wrap-around logic
        wrapped_index = (i - offset) % total_containers
        
        # Calculate position based on wrapped index
        new_x = start_x + wrapped_index * (container_width + spacing)
        
        # Handle the case where we need to show containers from the beginning again
        if wrapped_index < (i - offset):
            new_x += total_containers * (container_width + spacing)
        
        container.set_pos(new_x, start_y)

# Function to update container selection and position based on new index
def update_container_selection(new_index):
    global current_container_index, container_offset
    
    # Update text first
    global current_text_index
    current_text_index = new_index % len(text_list)
    text_label.set_text(text_list[current_text_index])
    text_label.align_to(bottom_color_obj, lv.ALIGN.TOP_MID, 0, 2)
    
    # Remove selection box from current container
    remove_selection_box(containers[current_container_index])
    
    # Update current container index
    current_container_index = new_index
    
    # Calculate appropriate container offset based on current container index
    # We want to keep the selected container in the middle when possible
    if current_container_index <= 1:
        # For first two containers, no offset needed
        container_offset = 0
    elif current_container_index >= 10:
        # For last two containers, set offset to show them properly
        container_offset = 10
    else:
        # For containers in between, center the selected container
        container_offset = current_container_index - 1
    
    # Move containers to new position
    move_containers(container_offset)
    
    # Add selection box to new current container
    add_selection_box(containers[current_container_index])

# Local implementation of recreate_main_page that doesn't require parameters
def local_recreate_main_page():
    global scr, color_obj, bottom_color_obj, text_label, containers
    global current_container_index, container_offset, text_list, current_text_index
    global start_x, start_y, container_width, container_height, spacing, total_containers, image_files
    global selection_style, add_selection_box, move_containers
    
    # Clear all current screen elements
    while True:
        child = scr.get_child(0)
        if child is None:
            break
        child.delete()
    
    # Set background to white
    scr.set_style_bg_color(lv.color_hex(0xffffff), 0)
    
    # Recreate full-screen objects for color display
    color_obj = lv.obj(scr)
    color_obj.set_size(500, 208)  # Match screen size after rotation
    color_obj.set_pos(-10, 0)

    bottom_color_obj = lv.obj(scr)
    bottom_color_obj.set_size(500, 80)  # Match screen size after rotation
    bottom_color_obj.set_pos(-10, 205)

    # Create inversion style similar to images
    inv_style = lv.style_t()
    inv_style.init()
    inv_style.set_bg_opa(lv.OPA.COVER)
    inv_style.set_blend_mode(lv.BLEND_MODE.DIFFERENCE)
    color_obj.add_style(inv_style, 0)
    color_obj.set_style_bg_color(lv.color_hex(0xffffff), 0)
    bottom_color_obj.add_style(inv_style, 0)
    bottom_color_obj.set_style_bg_color(lv.color_hex(0xdcdcdc), 0)

    # Recreate text label
    text_label = lv.label(scr)
    
    # Recreate text style
    text_style = lv.style_t()
    text_style.init()
    text_style.set_text_color(lv.color_hex(0xffffff))  # Black text
    text_style.set_text_font(lv.font_montserrat_36)
    text_style.set_blend_mode(lv.BLEND_MODE.NORMAL)  # Ensure normal blend mode
    text_label.add_style(text_style, 0)

    # Set current text
    text_label.set_text(text_list[current_text_index])
    text_label.align_to(bottom_color_obj, lv.ALIGN.TOP_MID, 0, 2)

    # Recreate containers
    containers = []

    for i in range(total_containers):
        # Calculate x position for current container
        x_pos = start_x + i * (container_width + spacing)
        
        container = lv.obj(scr)
        container.set_size(container_width, container_height)  # Set size
        container.set_pos(x_pos, start_y)  # Set position
        
        if i < 11:  # Real containers with images
            container.set_style_bg_color(lv.color_hex(0xffffff), 0)  # Set background color to white
            container.set_style_bg_opa(lv.OPA.COVER, 0)  # Make background opaque
            container.set_style_radius(10, 0)  # Set corner radius to 10 pixels
            container.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)  # Disable scrollbars
            
            # Add shadow
            container.set_style_shadow_width(5, 0)
            container.set_style_shadow_color(lv.color_hex(0xdddddd), 0)
            container.set_style_shadow_offset_y(3, 0)
            container.set_style_shadow_offset_x(3, 0)
            container.set_style_shadow_opa(lv.OPA._50, 0)
            
            # Create image object inside container
            img = lv.image(container)
            img.set_src(image_files[i+1])  # Use images from index 1 onwards
            img.set_size(container_width, container_height)  # Set image size same as container
            img.align(lv.ALIGN.CENTER, 0, 0)  # Center image in container
            img.set_style_radius(13, 0)
            
            # Apply inversion style to image for correct color display
            inv_style = lv.style_t()
            inv_style.init()
            inv_style.set_bg_opa(lv.OPA.COVER)
            inv_style.set_blend_mode(lv.BLEND_MODE.DIFFERENCE)
            img.add_style(inv_style, 0)
        else:  # Dummy container (no image, just spacing)
            container.set_style_bg_opa(lv.OPA.TRANSP, 0)  # Make background transparent
            container.set_style_border_opa(lv.OPA.TRANSP, 0)  # No border
            container.set_style_shadow_opa(lv.OPA.TRANSP, 0)  # No shadow
        
        # Add container to the list
        containers.append(container)

    # Add selection box to the current container
    add_selection_box(containers[current_container_index])

    # Move containers to the correct position
    move_containers(container_offset)

# Import the separated functions with aliases to avoid name conflicts
import lib.screen_test as screen_test_module
import lib.wireless as wireless_module
import lib.ble_keyboard as ble_keyboard_module
import lib.keyboard as keyboard_module
import lib.music as music_module
import lib.radio as radio_module
import lib.lora_chat as lora_chat_module
import lib.gps as gps_module
import lib.monitor as monitor_module
import lib.power as power_module
import lib.microphone as microphone_module
import lib.imu as imu_module

import lib.display_backlight as display_backlight_module
import lib.system_info as system_info_module
import lib.devices_status as devices_status_module
import lib.charger as charger_module
import lib.setting as setting_module

import lib.recreate_main_page as recreate_main_page_module

# Set up the references for the separated functions only once
# using our local implementation
screen_test_module.set_references(local_recreate_main_page, encoder)
wireless_module.set_references(local_recreate_main_page, encoder)
ble_keyboard_module.set_references(local_recreate_main_page, encoder)
keyboard_module.set_references(local_recreate_main_page, encoder)
music_module.set_references(local_recreate_main_page, encoder)
radio_module.set_references(local_recreate_main_page, encoder)
lora_chat_module.set_references(local_recreate_main_page, encoder)
gps_module.set_references(local_recreate_main_page, encoder)
monitor_module.set_references(local_recreate_main_page, encoder)
power_module.set_references(local_recreate_main_page, encoder)
microphone_module.set_references(local_recreate_main_page, encoder)
imu_module.set_references(local_recreate_main_page, encoder)

display_backlight_module.set_references(local_recreate_main_page, encoder, setting_module.setting)
system_info_module.set_references(local_recreate_main_page, encoder, setting_module.setting)
devices_status_module.set_references(local_recreate_main_page, encoder, setting_module.setting)
charger_module.set_references(local_recreate_main_page, encoder, setting_module.setting)
setting_module.set_references(local_recreate_main_page, encoder, display_backlight_module.display_backlight,system_info_module.system_info,devices_status_module.devices_status,charger_module.charger)

# Create function aliases for easy access
screen_test = screen_test_module.screen_test
wireless = wireless_module.wireless
ble_keyboard = ble_keyboard_module.ble_keyboard
keyboard = keyboard_module.keyboard
music = music_module.music
radio = radio_module.radio
lora_chat = lora_chat_module.lora_chat
gps = gps_module.gps
monitor = monitor_module.monitor
power = power_module.power
microphone = microphone_module.microphone
imu = imu_module.imu

display_backlight = display_backlight_module.display_backlight
system_info = system_info_module.system_info
devices_status = devices_status_module.devices_status
charger = charger_module.charger
setting = setting_module.setting
recreate_main_page = local_recreate_main_page

# Handle encoder input to switch text and move containers
while True:
    key = encoder.update()
    
    if key == "down":
        # Rotate down - select next container
        new_index = (current_container_index + 1) % 10  # Only 14 real containers (0-13)
        update_container_selection(new_index)

    elif key == "up":
        # Rotate up - select previous container
        new_index = (current_container_index - 1) % 10  # Only 14 real containers (0-13)
        update_container_selection(new_index)

    elif key == "enter":
        # Check if current selection is "Screen Test"
        if current_text_index == text_list.index("Screen Test"):
            screen_test()
        elif current_text_index == text_list.index("Setting"):
            setting()
        elif current_text_index == text_list.index("Wireless"):
            wireless()
        elif current_text_index == text_list.index("BLE Keyboard"):
            ble_keyboard()
        elif current_text_index == text_list.index("Keyboard"):
            keyboard()
#         elif current_text_index == text_list.index("Music"):
#             music()
        elif current_text_index == text_list.index("LoRa"):
            radio()
        elif current_text_index == text_list.index("LoRa Chat"):
            lora_chat()
        elif current_text_index == text_list.index("GPS"):
            gps()
        elif current_text_index == text_list.index("Monitor"):
            monitor()
        elif current_text_index == text_list.index("Power"):
            power()
#         elif current_text_index == text_list.index("microphone"):
#             microphone()
#         elif current_text_index == text_list.index("IMU"):
#             imu()

