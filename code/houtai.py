import ctypes
from ctypes import wintypes
import time
import re

# 加载 user32.dll
user32 = ctypes.WinDLL("user32", use_last_error=True)

# 定义必要的API和参数类型
user32.FindWindowW.argtypes = [wintypes.LPCWSTR, wintypes.LPCWSTR]
user32.FindWindowW.restype = wintypes.HWND

user32.FindWindowExW.argtypes = [
    wintypes.HWND,
    wintypes.HWND,
    wintypes.LPCWSTR,
    wintypes.LPCWSTR,
]
user32.FindWindowExW.restype = wintypes.HWND

user32.PostMessageW.argtypes = [
    wintypes.HWND,
    wintypes.UINT,
    wintypes.WPARAM,
    wintypes.LPARAM,
]
user32.PostMessageW.restype = wintypes.BOOL

user32.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
user32.GetWindowTextW.restype = ctypes.c_int

user32.GetClassNameW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
user32.GetClassNameW.restype = ctypes.c_int

user32.IsWindowVisible.argtypes = [wintypes.HWND]
user32.IsWindowVisible.restype = wintypes.BOOL

user32.GetClientRect.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]
user32.GetClientRect.restype = wintypes.BOOL

user32.MapVirtualKeyW.argtypes = [wintypes.UINT, wintypes.UINT]
user32.MapVirtualKeyW.restype = wintypes.UINT

user32.EnumWindows.argtypes = [
    ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, ctypes.POINTER(ctypes.c_int)),
    ctypes.POINTER(ctypes.c_int),
]
user32.EnumWindows.restype = wintypes.BOOL

# 消息常量
WM_KEYDOWN = 0x0100
WM_KEYUP = 0x0101
WM_CHAR = 0x0102
WM_MOUSEMOVE = 0x0200
WM_LBUTTONDOWN = 0x0201
WM_LBUTTONUP = 0x0202
WM_RBUTTONDOWN = 0x0204
WM_RBUTTONUP = 0x0205
WM_MOUSEWHEEL = 0x020A

# 虚拟键码
VK_A = 0x41
VK_B = 0x42
VK_C = 0x43
VK_D = 0x44
VK_E = 0x45
VK_F = 0x46
VK_G = 0x47
VK_H = 0x48
VK_I = 0x49
VK_J = 0x4A
VK_K = 0x4B
VK_L = 0x4C
VK_M = 0x4D
VK_N = 0x4E
VK_O = 0x4F
VK_P = 0x50
VK_Q = 0x51
VK_R = 0x52
VK_S = 0x53
VK_T = 0x54
VK_U = 0x55
VK_V = 0x56
VK_W = 0x57
VK_X = 0x58
VK_Y = 0x59
VK_Z = 0x5A
VK_0 = 0x30
VK_1 = 0x31
VK_2 = 0x32
VK_3 = 0x33
VK_4 = 0x34
VK_5 = 0x35
VK_6 = 0x36
VK_7 = 0x37
VK_8 = 0x38
VK_9 = 0x39
VK_SPACE = 0x20
VK_RETURN = 0x0D
VK_BACK = 0x08
VK_TAB = 0x09
VK_CONTROL = 0x11  # Ctrl键

# 鼠标状态
MK_LBUTTON = 0x0001
MK_RBUTTON = 0x0002


def get_scan_code(vk_code):
    """使用系统函数获取正确的扫描码"""
    return user32.MapVirtualKeyW(vk_code, 0)  # 0表示获取扫描码


def make_key_lparam(vk_code, is_down):
    """构造键盘消息的LPARAM参数"""
    scan_code = get_scan_code(vk_code)
    # 位布局:
    # 0-15: 重复计数(1)
    # 16-23: 扫描码
    # 24: 扩展键标志(0)
    # 25-28: 保留(0)
    # 29: 上下文代码(0)
    # 30: 先前键状态(0=按下前未按下, 1=按下前已按下)
    # 31: 转换状态(0=按下, 1=释放)
    lparam = 0x0001  # 重复计数
    lparam |= scan_code << 16  # 扫描码
    if not is_down:
        lparam |= 1 << 30  # 先前键状态(已按下)
        lparam |= 1 << 31  # 转换状态(释放)
    return lparam


def make_mouse_lparam(x, y):
    """构造鼠标消息的LPARAM参数（客户区坐标）"""
    return (y << 16) | (x & 0xFFFF)


def find_window(title=None, class_name=None, timeout=10, exact=False):
    """查找窗口句柄（纯后台，不激活）"""
    print(f"查找窗口 - 标题: {title}, 类名: {class_name}, 精确匹配: {exact}")

    start_time = time.time()
    while time.time() - start_time < timeout:
        hWnd = user32.FindWindowW(class_name, title)
        if hWnd:
            print(f"找到窗口: {hWnd}, 标题: {get_window_title(hWnd)}")
            return hWnd

        # 尝试模糊匹配
        if not exact and title:
            all_windows = list_windows()
            for hwnd, win_title, win_class in all_windows:
                if title in win_title:
                    print(f"通过模糊匹配找到窗口: {hwnd}, 标题: {win_title}")
                    return hwnd

        time.sleep(0.5)

    print(f"未找到窗口 - 标题: {title}, 类名: {class_name}")
    return None


def find_child_window(parent_hwnd, class_name=None, title=None):
    """查找子窗口句柄"""
    print(f"查找子窗口 - 父窗口: {parent_hwnd}, 类名: {class_name}, 标题: {title}")
    hwnd = user32.FindWindowExW(parent_hwnd, None, class_name, title)

    if hwnd:
        print(f"找到子窗口: {hwnd}, 标题: {get_window_title(hwnd)}")
    else:
        print(f"未找到子窗口")

    return hwnd


def list_windows(visible_only=True):
    """列出所有窗口，用于调试"""
    windows = []

    def enum_callback(hwnd, lparam):
        if visible_only and not user32.IsWindowVisible(hwnd):
            return True

        title = get_window_title(hwnd)
        class_name = get_window_class(hwnd)

        if title or class_name:
            windows.append((hwnd, title, class_name))

        return True

    user32.EnumWindows(
        ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, ctypes.POINTER(ctypes.c_int))(
            enum_callback
        ),
        None,
    )
    return windows


def get_window_title(hwnd):
    """获取窗口标题"""
    buf = ctypes.create_unicode_buffer(256)
    user32.GetWindowTextW(hwnd, buf, 256)
    return buf.value


def get_window_class(hwnd):
    """获取窗口类名"""
    buf = ctypes.create_unicode_buffer(256)
    user32.GetClassNameW(hwnd, buf, 256)
    return buf.value


def post_key(hwnd, vk_code):
    """发送键盘按键（纯后台）"""
    # 发送按下消息
    lparam_down = make_key_lparam(vk_code, is_down=True)
    success_down = user32.PostMessageW(hwnd, WM_KEYDOWN, vk_code, lparam_down)
    time.sleep(0.05)

    # 发送释放消息
    lparam_up = make_key_lparam(vk_code, is_down=False)
    success_up = user32.PostMessageW(hwnd, WM_KEYUP, vk_code, lparam_up)
    time.sleep(0.05)

    return success_down and success_up


def post_unicode_char(hwnd, char_code):
    """发送Unicode字符（支持中文等特殊字符）"""
    # 使用WM_CHAR消息直接发送Unicode字符
    lparam = 0x0001  # 重复计数为1
    success = user32.PostMessageW(hwnd, WM_CHAR, char_code, lparam)
    time.sleep(0.1)  # 中文输入需要更长间隔
    return success


def post_text(hwnd, text):
    """发送文本（支持中文）"""
    print(f"发送文本: '{text}'")
    for char in text:
        # 对于ASCII字符使用普通按键方式
        if ord(char) < 128:
            vk_code = ord(char.upper()) if char.isalpha() else None

            # 处理特殊字符
            if char == " ":
                vk_code = VK_SPACE
            elif char == "\n":
                vk_code = VK_RETURN
            elif char == "\t":
                vk_code = VK_TAB
            elif char == "\b":
                vk_code = VK_BACK
            elif char.isdigit():
                vk_code = ord(char)

            if vk_code:
                post_key(hwnd, vk_code)
        else:
            # 对于Unicode字符（如中文）使用WM_CHAR直接发送
            post_unicode_char(hwnd, ord(char))
        time.sleep(0.1)


def post_mouse_move(hwnd, x, y):
    """鼠标移动（相对窗口客户区）"""
    print(f"鼠标移动到: ({x}, {y})")
    lparam = make_mouse_lparam(x, y)
    return user32.PostMessageW(hwnd, WM_MOUSEMOVE, 0, lparam)


def post_mouse_drag(hwnd, start_x, start_y, end_x, end_y):
    """鼠标拖拽（从起点到终点）"""
    print(f"鼠标拖拽: 从({start_x}, {start_y})到({end_x}, {end_y})")

    # 移动到起点
    post_mouse_move(hwnd, start_x, start_y)
    time.sleep(0.1)

    # 按下左键
    lparam_start = make_mouse_lparam(start_x, start_y)
    success_down = user32.PostMessageW(hwnd, WM_LBUTTONDOWN, MK_LBUTTON, lparam_start)
    time.sleep(0.1)

    # 逐步移动到终点（模拟真实拖拽）
    steps = 10  # 分10步移动，使拖拽更平滑
    for i in range(steps + 1):
        x = start_x + int((end_x - start_x) * i / steps)
        y = start_y + int((end_y - start_y) * i / steps)
        post_mouse_move(hwnd, x, y)
        time.sleep(0.05)

    # 释放左键
    lparam_end = make_mouse_lparam(end_x, end_y)
    success_up = user32.PostMessageW(hwnd, WM_LBUTTONUP, 0, lparam_end)
    time.sleep(0.1)

    return success_down and success_up


def post_mouse_click(hwnd, x, y, is_right=False):
    """鼠标点击（相对窗口客户区，纯后台）"""
    button = "右键" if is_right else "左键"
    print(f"{button}点击: ({x}, {y})")

    lparam = make_mouse_lparam(x, y)

    # 移动到目标位置
    post_mouse_move(hwnd, x, y)
    time.sleep(0.05)

    # 按下
    down_msg = WM_RBUTTONDOWN if is_right else WM_LBUTTONDOWN
    down_param = MK_RBUTTON if is_right else MK_LBUTTON
    success_down = user32.PostMessageW(hwnd, down_msg, down_param, lparam)
    time.sleep(0.05)

    # 释放
    up_msg = WM_RBUTTONUP if is_right else WM_LBUTTONUP
    success_up = user32.PostMessageW(hwnd, up_msg, 0, lparam)
    time.sleep(0.05)

    return success_down and success_up


def main():
    # 打印所有可见窗口，用于调试
    print("\n当前所有可见窗口:")
    for i, (hwnd, title, class_name) in enumerate(list_windows()):
        print(f"{i+1}. 句柄: {hwnd}, 标题: '{title}', 类名: '{class_name}'")

    # 查找记事本窗口
    print("\n查找记事本窗口...")

    # 尝试多种可能的标题匹配
    possible_titles = ["记事本 - Notepad",".*记事本"]
    main_hwnd = None

    for title in possible_titles:
        exact = False if title.startswith(".*") else True
        search_title = title.replace(".*", "")

        main_hwnd = find_window(title=search_title, exact=exact)
        if main_hwnd:
            break

    if not main_hwnd:
        print("\n未找到记事本窗口！")
        print("请检查：")
        print("1. 记事本是否已打开")
        print("2. 记事本窗口标题是否与上述列表中的任何一项匹配")
        return

    # 查找记事本的编辑区子窗口（实际接收输入的区域）
    edit_hwnd = find_child_window(main_hwnd, class_name="Edit")
    if not edit_hwnd:
        print("未找到编辑区子窗口，使用主窗口尝试")
        edit_hwnd = main_hwnd

    # 纯后台操作演示
    print("\n开始后台操作...")

    # 1. 清空现有内容（Ctrl+A全选，然后删除）
    print("清空现有内容...")
    post_key(edit_hwnd, VK_CONTROL)  # 按下Ctrl
    post_key(edit_hwnd, VK_A)  # 按下A
    post_key(edit_hwnd, VK_CONTROL)  # 释放Ctrl
    post_key(edit_hwnd, VK_BACK)  # 删除选中内容
    time.sleep(1)

    # 2. 输入"你好世界"
    print("输入'你好世界'...")
    post_text(edit_hwnd, "你好世界")
    time.sleep(1)

    # 3. 鼠标拖拽选中"你好世界"
    # 假设文本在窗口客户区的位置：
    # 中文每个字符大约占16-20像素宽度，16像素高度
    start_x, start_y = 20, 20  # 文本起始位置
    end_x, end_y = 20 + 80, 20  # 文本结束位置（4个中文字符，每个约20像素）

    print("拖拽选中文本...")
    post_mouse_drag(edit_hwnd, start_x, start_y, end_x, end_y)
    time.sleep(1)

    print("操作完成，所有操作均在后台执行")


if __name__ == "__main__":
    main()
