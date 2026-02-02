import lvgl as lv

# 导入依赖
recreate_main_page_func = None

def set_references(recreate_func):
    global recreate_main_page_func
    recreate_main_page_func = recreate_func

def recreate_main_page():
    # 直接调用主模块中定义的recreate_main_page函数，该函数已经包含了所有必要的参数
    if recreate_main_page_func is not None:
        recreate_main_page_func()
    else:
        # 如果没有设置引用，尝试直接在屏幕上重新创建UI
        scr = lv.screen_active()
        
        # Clear all current screen elements
        while True:
            child = scr.get_child(0)
            if child is None:
                break
            child.delete()
        
        # Set background to white
        scr.set_style_bg_color(lv.color_hex(0xffffff), 0)
