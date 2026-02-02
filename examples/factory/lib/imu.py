import lvgl as lv
import time

recreate_main_page = None
encoder = None

def set_references(recreate_func, encoder_obj=None):
    global recreate_main_page, encoder
    recreate_main_page = recreate_func
    if encoder_obj is not None:
        encoder = encoder_obj

def imu():
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
    print("imu")
    time.sleep(2)
    # Clear the screen again to prepare for returning to original page
    scr = lv.screen_active()
    while True:
        child = scr.get_child(0)
        if child is None:
            break
        child.delete()
    
    # Return to original page by recreating all elements
    recreate_main_page()


