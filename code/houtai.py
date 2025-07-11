import ctypes
from ctypes import wintypes
import time
import re

# 加载 user32.dll
user32 = ctypes.WinDLL('user32', use_last_error=True)
kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)

# 定义函数参数和返回值类型
user32.FindWindowW.argtypes = [wintypes.LPCWSTR, wintypes.LPCWSTR]
user32.FindWindowW.restype = wintypes.HWND

user32.PostMessageW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
user32.PostMessageW.restype = wintypes.BOOL

user32.SendMessageW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
user32.SendMessageW.restype = wintypes.LPARAM

user32.EnumWindows.argtypes = [ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, ctypes.POINTER(ctypes.c_int)), ctypes.POINTER(ctypes.c_int)]
user32.EnumWindows.restype = wintypes.BOOL

user32.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
user32.GetWindowTextW.restype = ctypes.c_int

user32.GetClassNameW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
user32.GetClassNameW.restype = ctypes.c_int

user32.IsWindowVisible.argtypes = [wintypes.HWND]
user32.IsWindowVisible.restype = wintypes.BOOL

user32.GetClientRect.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]
user32.GetClientRect.restype = wintypes.BOOL

user32.ClientToScreen.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.POINT)]
user32.ClientToScreen.restype = wintypes.BOOL

user32.SetForegroundWindow.argtypes = [wintypes.HWND]
user32.SetForegroundWindow.restype = wintypes.BOOL

# SendInput 相关定义
INPUT_MOUSE = 0
INPUT_KEYBOARD = 1
INPUT_HARDWARE = 2

KEYEVENTF_EXTENDEDKEY = 0x0001
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_UNICODE = 0x0004
KEYEVENTF_SCANCODE = 0x0008

MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
MOUSEEVENTF_MIDDLEDOWN = 0x0020
MOUSEEVENTF_MIDDLEUP = 0x0040
MOUSEEVENTF_WHEEL = 0x0800
MOUSEEVENTF_ABSOLUTE = 0x8000

class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", ctypes.c_long),
        ("dy", ctypes.c_long),
        ("mouseData", ctypes.c_ulong),
        ("dwFlags", ctypes.c_ulong),
        ("time", ctypes.c_ulong),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))
    ]

class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", ctypes.c_ushort),
        ("wScan", ctypes.c_ushort),
        ("dwFlags", ctypes.c_ulong),
        ("time", ctypes.c_ulong),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))
    ]

class HARDWAREINPUT(ctypes.Structure):
    _fields_ = [
        ("uMsg", ctypes.c_ulong),
        ("wParamL", ctypes.c_short),
        ("wParamH", ctypes.c_ushort)
    ]

class INPUT(ctypes.Structure):
    class _INPUT(ctypes.Union):
        _fields_ = [
            ("mi", MOUSEINPUT),
            ("ki", KEYBDINPUT),
            ("hi", HARDWAREINPUT)
        ]
    _anonymous_ = ("_input",)
    _fields_ = [
        ("type", ctypes.c_ulong),
        ("_input", _INPUT)
    ]

# 常量定义
WM_KEYDOWN = 0x0100
WM_KEYUP = 0x0101
WM_CHAR = 0x0102
WM_MOUSEMOVE = 0x0200
WM_LBUTTONDOWN = 0x0201
WM_LBUTTONUP = 0x0202
WM_RBUTTONDOWN = 0x0204
WM_RBUTTONUP = 0x0205
WM_MBUTTONDOWN = 0x0207
WM_MBUTTONUP = 0x0208
WM_MOUSEWHEEL = 0x020A

# 虚拟键码定义
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
VK_SPACE = 0x20
VK_RETURN = 0x0D
VK_TAB = 0x09
VK_BACK = 0x08
VK_ESCAPE = 0x1B
VK_CONTROL = 0x11
VK_MENU = 0x12  # Alt键
VK_SHIFT = 0x10
VK_LEFT = 0x25
VK_UP = 0x26
VK_RIGHT = 0x27
VK_DOWN = 0x28

# 鼠标键状态
MK_LBUTTON = 0x0001
MK_RBUTTON = 0x0002
MK_MBUTTON = 0x0010

def make_lparam(x, y):
    """将x,y坐标合成LPARAM"""
    return (y << 16) | (x & 0xFFFF)

def get_key_scan_code(vk_code):
    """获取按键的扫描码"""
    # 简化版本，返回常用按键的扫描码
    # 实际应用中可能需要使用MapVirtualKey API
    scan_codes = {
        VK_A: 0x1E, VK_B: 0x30, VK_C: 0x2E, VK_D: 0x20,
        VK_E: 0x12, VK_F: 0x21, VK_G: 0x22, VK_H: 0x23,
        VK_I: 0x17, VK_J: 0x24, VK_K: 0x25, VK_L: 0x26,
        VK_M: 0x32, VK_N: 0x31, VK_O: 0x18, VK_P: 0x19,
        VK_Q: 0x10, VK_R: 0x13, VK_S: 0x1F, VK_T: 0x14,
        VK_U: 0x16, VK_V: 0x2F, VK_W: 0x11, VK_X: 0x2D,
        VK_Y: 0x15, VK_Z: 0x2C,
        VK_0: 0x0B, VK_1: 0x02, VK_2: 0x03, VK_3: 0x04,
        VK_4: 0x05, VK_5: 0x06, VK_6: 0x07, VK_7: 0x08,
        VK_8: 0x09, VK_9: 0x0A,
        VK_SPACE: 0x39, VK_RETURN: 0x1C, VK_TAB: 0x0F,
        VK_BACK: 0x0E, VK_ESCAPE: 0x01,
        VK_LEFT: 0xCB, VK_UP: 0xC8, VK_RIGHT: 0xCD, VK_DOWN: 0xD0
    }
    return scan_codes.get(vk_code, 0)

def activate_window(hWnd):
    """激活指定窗口"""
    if user32.IsIconic(hWnd):  # 如果窗口最小化
        user32.ShowWindow(hWnd, 9)  # SW_RESTORE = 9，恢复窗口
    user32.SetForegroundWindow(hWnd)
    time.sleep(0.5)  # 给窗口时间获得焦点
    return True

def post_key(hWnd, vk_code, scan_code=None, with_char=True, use_send_input=False):
    """
    模拟按下和抬起一个键
    
    参数:
        hWnd: 窗口句柄
        vk_code: 虚拟键码
        scan_code: 扫描码，默认为None时会使用内置映射
        with_char: 是否发送WM_CHAR消息（用于字符输入）
        use_send_input: 是否使用SendInput API
    """
    if scan_code is None:
        scan_code = get_key_scan_code(vk_code)
    
    if use_send_input:
        # 使用SendInput API
        extra = ctypes.c_ulong(0)
        ii_keydown = KEYBDINPUT(
            wVk=vk_code,
            wScan=scan_code,
            dwFlags=KEYEVENTF_SCANCODE,
            time=0,
            dwExtraInfo=ctypes.pointer(extra)
        )
        ii_keyup = KEYBDINPUT(
            wVk=vk_code,
            wScan=scan_code,
            dwFlags=KEYEVENTF_SCANCODE | KEYEVENTF_KEYUP,
            time=0,
            dwExtraInfo=ctypes.pointer(extra)
        )
        x = INPUT(type=INPUT_KEYBOARD, ki=ii_keydown)
        y = INPUT(type=INPUT_KEYBOARD, ki=ii_keyup)
        
        # 发送按键按下
        user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))
        time.sleep(0.02)
        
        # 发送按键释放
        user32.SendInput(1, ctypes.pointer(y), ctypes.sizeof(y))
        time.sleep(0.02)
        
        return True
    else:
        # 使用PostMessage API
        # 构建lParam
        # 低16位：重复计数
        # 16-23位：扫描码
        # 24位：扩展键标志
        # 29位：上下文代码
        # 30位：先前键状态
        # 31位：转换状态
        
        # 按键按下
        lparam_down = 0x00000001 | (scan_code << 16)
        
        # 按键释放
        lparam_up = lparam_down | (1 << 30) | (1 << 31)
        
        # 发送按键按下消息
        user32.PostMessageW(hWnd, WM_KEYDOWN, vk_code, lparam_down)
        time.sleep(0.02)  # 模拟真实按键间隔
        
        # 发送字符消息（如果需要）
        if with_char and vk_code >= VK_A and vk_code <= VK_Z:
            # 计算对应的ASCII码
            char_code = vk_code
            user32.PostMessageW(hWnd, WM_CHAR, char_code, lparam_down)
            time.sleep(0.02)
        
        # 发送按键释放消息
        user32.PostMessageW(hWnd, WM_KEYUP, vk_code, lparam_up)
        time.sleep(0.02)
        
        return True

def post_text(hWnd, text, use_send_input=False):
    """
    向窗口发送文本
    
    参数:
        hWnd: 窗口句柄
        text: 要发送的文本
        use_send_input: 是否使用SendInput API
    """
    for char in text:
        vk_code = ord(char.upper())
        # 只处理有映射的字符
        if VK_A <= vk_code <= VK_Z or VK_0 <= vk_code <= VK_9:
            post_key(hWnd, vk_code, use_send_input=use_send_input)
        elif char == ' ':
            post_key(hWnd, VK_SPACE, use_send_input=use_send_input)
        elif char == '\n':
            post_key(hWnd, VK_RETURN, use_send_input=use_send_input)
        # 可以扩展更多字符处理...
        time.sleep(0.05)  # 字符间间隔
    return True

def client_to_screen(hWnd, x, y):
    """将窗口客户区坐标转换为屏幕坐标"""
    point = wintypes.POINT(x, y)
    user32.ClientToScreen(hWnd, ctypes.byref(point))
    return point.x, point.y

def post_mouse_move(hWnd, x, y, use_send_input=False):
    """
    模拟鼠标移动到窗口内的指定位置
    
    参数:
        hWnd: 窗口句柄
        x, y: 相对于窗口客户区的坐标
        use_send_input: 是否使用SendInput API
    """
    if use_send_input:
        # 获取屏幕分辨率
        screen_width = user32.GetSystemMetrics(0)  # SM_CXSCREEN
        screen_height = user32.GetSystemMetrics(1)  # SM_CYSCREEN
        
        # 将客户区坐标转换为屏幕坐标
        screen_x, screen_y = client_to_screen(hWnd, x, y)
        
        # 转换为SendInput API所需的规范化坐标
        normalized_x = int((screen_x * 65535) / screen_width)
        normalized_y = int((screen_y * 65535) / screen_height)
        
        extra = ctypes.c_ulong(0)
        mi = MOUSEINPUT(
            dx=normalized_x,
            dy=normalized_y,
            mouseData=0,
            dwFlags=MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE,
            time=0,
            dwExtraInfo=ctypes.pointer(extra)
        )
        x = INPUT(type=INPUT_MOUSE, mi=mi)
        user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))
        time.sleep(0.02)
        return True
    else:
        lparam = make_lparam(x, y)
        user32.PostMessageW(hWnd, WM_MOUSEMOVE, 0, lparam)
        time.sleep(0.02)
        return True

def post_mouse_click(hWnd, x, y, button='left', count=1, use_send_input=False):
    """
    模拟鼠标点击
    
    参数:
        hWnd: 窗口句柄
        x, y: 相对于窗口客户区的坐标
        button: 鼠标按钮，'left'、'right' 或 'middle'
        count: 点击次数
        use_send_input: 是否使用SendInput API
    """
    if use_send_input:
        # 获取屏幕分辨率
        screen_width = user32.GetSystemMetrics(0)  # SM_CXSCREEN
        screen_height = user32.GetSystemMetrics(1)  # SM_CYSCREEN
        
        # 将客户区坐标转换为屏幕坐标
        screen_x, screen_y = client_to_screen(hWnd, x, y)
        
        # 转换为SendInput API所需的规范化坐标
        normalized_x = int((screen_x * 65535) / screen_width)
        normalized_y = int((screen_y * 65535) / screen_height)
        
        # 根据按钮类型选择消息
        if button == 'left':
            down_flags = MOUSEEVENTF_LEFTDOWN
            up_flags = MOUSEEVENTF_LEFTUP
        elif button == 'right':
            down_flags = MOUSEEVENTF_RIGHTDOWN
            up_flags = MOUSEEVENTF_RIGHTUP
        elif button == 'middle':
            down_flags = MOUSEEVENTF_MIDDLEDOWN
            up_flags = MOUSEEVENTF_MIDDLEUP
        else:
            return False
        
        # 执行点击
        for _ in range(count):
            extra = ctypes.c_ulong(0)
            
            # 移动到位置
            mi_move = MOUSEINPUT(
                dx=normalized_x,
                dy=normalized_y,
                mouseData=0,
                dwFlags=MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE,
                time=0,
                dwExtraInfo=ctypes.pointer(extra)
            )
            x_move = INPUT(type=INPUT_MOUSE, mi=mi_move)
            user32.SendInput(1, ctypes.pointer(x_move), ctypes.sizeof(x_move))
            time.sleep(0.02)
            
            # 按下按钮
            mi_down = MOUSEINPUT(
                dx=normalized_x,
                dy=normalized_y,
                mouseData=0,
                dwFlags=down_flags | MOUSEEVENTF_ABSOLUTE,
                time=0,
                dwExtraInfo=ctypes.pointer(extra)
            )
            x_down = INPUT(type=INPUT_MOUSE, mi=mi_down)
            user32.SendInput(1, ctypes.pointer(x_down), ctypes.sizeof(x_down))
            time.sleep(0.05)
            
            # 释放按钮
            mi_up = MOUSEINPUT(
                dx=normalized_x,
                dy=normalized_y,
                mouseData=0,
                dwFlags=up_flags | MOUSEEVENTF_ABSOLUTE,
                time=0,
                dwExtraInfo=ctypes.pointer(extra)
            )
            x_up = INPUT(type=INPUT_MOUSE, mi=mi_up)
            user32.SendInput(1, ctypes.pointer(x_up), ctypes.sizeof(x_up))
            time.sleep(0.05)
        
        return True
    else:
        lparam = make_lparam(x, y)
        
        # 根据按钮类型选择消息
        if button == 'left':
            down_msg = WM_LBUTTONDOWN
            up_msg = WM_LBUTTONUP
            wparam = MK_LBUTTON
        elif button == 'right':
            down_msg = WM_RBUTTONDOWN
            up_msg = WM_RBUTTONUP
            wparam = MK_RBUTTON
        elif button == 'middle':
            down_msg = WM_MBUTTONDOWN
            up_msg = WM_MBUTTONUP
            wparam = MK_MBUTTON
        else:
            return False
        
        # 执行点击
        for _ in range(count):
            # 移动到位置
            user32.PostMessageW(hWnd, WM_MOUSEMOVE, 0, lparam)
            time.sleep(0.02)
            
            # 按下按钮
            user32.PostMessageW(hWnd, down_msg, wparam, lparam)
            time.sleep(0.05)
            
            # 释放按钮
            user32.PostMessageW(hWnd, up_msg, 0, lparam)
            time.sleep(0.05)
        
        return True

def post_mouse_wheel(hWnd, x, y, delta=120, use_send_input=False):
    """
    模拟鼠标滚轮滚动
    
    参数:
        hWnd: 窗口句柄
        x, y: 相对于窗口客户区的坐标
        delta: 滚动量，正值表示向上滚动，负值表示向下滚动
        use_send_input: 是否使用SendInput API
    """
    if use_send_input:
        # 获取屏幕分辨率
        screen_width = user32.GetSystemMetrics(0)  # SM_CXSCREEN
        screen_height = user32.GetSystemMetrics(1)  # SM_CYSCREEN
        
        # 将客户区坐标转换为屏幕坐标
        screen_x, screen_y = client_to_screen(hWnd, x, y)
        
        # 转换为SendInput API所需的规范化坐标
        normalized_x = int((screen_x * 65535) / screen_width)
        normalized_y = int((screen_y * 65535) / screen_height)
        
        extra = ctypes.c_ulong(0)
        mi = MOUSEINPUT(
            dx=normalized_x,
            dy=normalized_y,
            mouseData=delta,
            dwFlags=MOUSEEVENTF_WHEEL | MOUSEEVENTF_ABSOLUTE,
            time=0,
            dwExtraInfo=ctypes.pointer(extra)
        )
        x = INPUT(type=INPUT_MOUSE, mi=mi)
        user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))
        time.sleep(0.05)
        return True
    else:
        lparam = make_lparam(x, y)
        wparam = (delta << 16) & 0xFFFF0000  # 高位字包含滚动量
        
        user32.PostMessageW(hWnd, WM_MOUSEWHEEL, wparam, lparam)
        time.sleep(0.05)
        return True

def find_window(title=None, class_name=None, timeout=5, retry_interval=0.5, exact_match=False, regex=False, visible_only=True):
    """
    查找窗口，支持多种匹配方式和重试机制
    
    参数:
        title: 窗口标题，支持模糊匹配、正则匹配或精确匹配
        class_name: 窗口类名
        timeout: 超时时间（秒）
        retry_interval: 重试间隔（秒）
        exact_match: 是否精确匹配
        regex: 是否使用正则表达式匹配
        visible_only: 是否只考虑可见窗口
        
    返回:
        窗口句柄或None
    """
    start_time = time.time()
    
    while True:
        # 使用 FindWindow 进行基本查找
        hWnd = user32.FindWindowW(class_name if class_name else None, title if title else None)
        
        # 如果找到了窗口，检查是否符合条件
        if hWnd:
            if not visible_only or user32.IsWindowVisible(hWnd):
                # 检查标题匹配条件
                if title:
                    window_title = get_window_title(hWnd)
                    if (exact_match and window_title == title) or \
                       (regex and re.search(title, window_title)) or \
                       (not exact_match and not regex and title in window_title):
                        return hWnd
                else:
                    return hWnd
        
        # 如果未找到或不符合条件，尝试枚举所有窗口
        hWnd = find_window_by_enum(title, class_name, exact_match, regex, visible_only)
        if hWnd:
            return hWnd
        
        # 检查是否超时
        if time.time() - start_time > timeout:
            return None
            
        # 等待后重试
        time.sleep(retry_interval)

def find_window_by_enum(title=None, class_name=None, exact_match=False, regex=False, visible_only=True):
    """
    通过枚举所有窗口来查找符合条件的窗口
    
    返回:
        窗口句柄或None
    """
    windows = []
    
    def enum_windows_callback(hWnd, lparam):
        if visible_only and not user32.IsWindowVisible(hWnd):
            return True
            
        if title:
            window_title = get_window_title(hWnd)
            if (exact_match and window_title == title) or \
               (regex and re.search(title, window_title)) or \
               (not exact_match and not regex and title in window_title):
                windows.append(hWnd)
        elif class_name:
            window_class = get_window_class(hWnd)
            if (exact_match and window_class == class_name) or \
               (regex and re.search(class_name, window_class)) or \
               (not exact_match and not regex and class_name in window_class):
                windows.append(hWnd)
        else:
            # 如果没有提供标题或类名，不添加窗口
            pass
            
        return True
    
    # 注意这里不再传递windows参数，而是使用None
    user32.EnumWindows(ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, ctypes.POINTER(ctypes.c_int))(enum_windows_callback), None)
    
    # 返回第一个找到的窗口或None
    return windows[0] if windows else None

def get_window_title(hWnd):
    """获取窗口标题"""
    length = user32.GetWindowTextLengthW(hWnd)
    buf = ctypes.create_unicode_buffer(length + 1)
    user32.GetWindowTextW(hWnd, buf, length + 1)
    return buf.value

def get_window_class(hWnd):
    """获取窗口类名"""
    buf = ctypes.create_unicode_buffer(256)
    user32.GetClassNameW(hWnd, buf, 256)
    return buf.value

def get_window_client_size(hWnd):
    """获取窗口客户区大小"""
    rect = wintypes.RECT()
    if user32.GetClientRect(hWnd, ctypes.byref(rect)):
        return rect.right, rect.bottom
    return 0, 0

def list_windows(visible_only=True):
    """列出所有符合条件的窗口，用于调试"""
    windows = []
    
    def enum_windows_callback(hWnd, lparam):
        if visible_only and not user32.IsWindowVisible(hWnd):
            return True
            
        title = get_window_title(hWnd)
        class_name = get_window_class(hWnd)
        if title or class_name:
            windows.append((hWnd, title, class_name))
            
        return True
    
    user32.EnumWindows(ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, ctypes.POINTER(ctypes.c_int))(enum_windows_callback), None)
    
    return windows

def main():
    """演示后台键盘鼠标操作的主函数"""
    print("准备演示后台键盘鼠标操作...")
    print("请确保目标窗口已打开（例如记事本）")
    time.sleep(2)
    
    # 查找目标窗口（示例：记事本）
    print("正在查找目标窗口...")
    hWnd = find_window(title="记事本", timeout=10)
    
    if not hWnd:
        print("找不到目标窗口！")
        print("当前可见窗口列表:")
        for hwnd, title, class_name in list_windows(visible_only=True):
            print(f"  句柄: {hwnd}, 标题: '{title}', 类名: '{class_name}'")
        return
    
    print(f"已找到窗口: {get_window_title(hWnd)} (句柄: {hWnd})")
    
    # 获取窗口大小
    width, height = get_window_client_size(hWnd)
    print(f"窗口客户区大小: {width} x {height}")
    
    # 尝试激活窗口
    print("尝试激活窗口...")
    activate_window(hWnd)
    
    # 输出当前激活的窗口标题，用于验证
    active_hwnd = user32.GetForegroundWindow()
    active_title = get_window_title(active_hwnd)
    print(f"当前激活的窗口: {active_title}")
    
    # 检查是否成功激活目标窗口
    if active_hwnd != hWnd:
        print("警告: 未能成功激活目标窗口！后台输入可能无效。")
    
    print("开始演示后台操作...")
    time.sleep(1)
    
    # 1. 使用SendInput输入文本
    print("演示1: 使用SendInput后台输入文本")
    post_text(hWnd, "Hello, World!\n这是一个后台输入的示例。", use_send_input=True)
    time.sleep(1)
    
    # 2. 使用PostMessage模拟按键（按下A键）
    print("演示2: 使用PostMessage后台按键")
    post_key(hWnd, VK_A, use_send_input=False)
    time.sleep(1)
    
    # 3. 使用SendInput模拟鼠标点击（在窗口中心）
    print("演示3: 使用SendInput后台鼠标点击")
    center_x, center_y = width // 2, height // 2
    post_mouse_click(hWnd, center_x, center_y, use_send_input=True)
    time.sleep(1)
    
    # 4. 使用PostMessage模拟右键点击
    print("演示4: 使用PostMessage后台右键点击")
    post_mouse_click(hWnd, center_x, center_y, button='right', use_send_input=False)
    time.sleep(1)
    
    # 5. 使用SendInput模拟鼠标滚轮
    print("演示5: 使用SendInput后台鼠标滚轮")
    post_mouse_wheel(hWnd, center_x, center_y, delta=120, use_send_input=True)  # 向上滚动
    time.sleep(0.5)
    post_mouse_wheel(hWnd, center_x, center_y, delta=-120, use_send_input=True)  # 向下滚动
    time.sleep(1)
    
    # 6. 使用PostMessage输入更多文本
    print("演示6: 使用PostMessage继续输入文本")
    post_text(hWnd, "\n\n操作完成！", use_send_input=False)
    
    print("演示完成！")

if __name__ == "__main__":
    main()