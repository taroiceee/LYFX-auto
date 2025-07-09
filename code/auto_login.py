import pyautogui
import time
import cv2
import numpy as np
from PIL import ImageGrab
import win32gui
import win32con
import csv
import random
import os
import argparse
import subprocess
import ctypes
import pydirectinput
import pygetwindow as gw
import pytesseract
from datetime import datetime

# 禁用安全特性
pyautogui.FAILSAFE = False

# 项目目录结构
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_DIR = os.path.join(os.path.dirname(ROOT_DIR), "image")
DATA_DIR = os.path.join(os.path.dirname(ROOT_DIR), "data")
OCR_DEBUG_DIR = os.path.join(os.path.dirname(ROOT_DIR), "debug/ocr")
LOGS_DIR = os.path.join(os.path.dirname(ROOT_DIR), "logs")  # 新增日志目录

# 创建OCR调试目录和日志目录
os.makedirs(OCR_DEBUG_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)  # 确保日志目录存在

# 配置参数
GAME_EXE_PATH = r"D:\新烈焰飞雪\烈焰飞雪\7hero.exe"  # 游戏可执行文件路径
GAME_TITLE = "烈焰飞雪"  # 游戏窗口标题
IMAGE_PATHS = {
    "ENTER_GAME": os.path.join(IMAGE_DIR, "enter_game.png"),
    "CONFIRM_SELECT": os.path.join(IMAGE_DIR, "confirm_select.png"),
    "START_GAME": os.path.join(IMAGE_DIR, "start_game.png"),
    "YES_BUTTON": os.path.join(IMAGE_DIR, "yes_button.png"),
    "CONFIRM_BUTTON": os.path.join(IMAGE_DIR, "confirm_button.png"),
    "ACCOUNT_BOX": os.path.join(IMAGE_DIR, "account_box.png"),
    "PASSWORD_BOX": os.path.join(IMAGE_DIR, "password_box.png"),
    "LOGIN_BUTTON": os.path.join(IMAGE_DIR, "login_button.png"),
    "CARD_AREA": os.path.join(IMAGE_DIR, "card_area.png"),
    "AUTO_HANGUP": os.path.join(IMAGE_DIR, "auto_hangup.png"),
    "SERVER_1": os.path.join(IMAGE_DIR, "server_1.png"),
    "SERVER_FAILED": os.path.join(IMAGE_DIR, "server_failed.png"),
    "FINISH_UPDATE": os.path.join(IMAGE_DIR, "finish_update.png"),
    "HANDLE_SELECT": os.path.join(IMAGE_DIR, "handle_select.png"),
    "CONFIRM": os.path.join(IMAGE_DIR, "confirm.png"),
    "GAME_CONFIRM": os.path.join(IMAGE_DIR, "game_confirm.png"),
    "WENXINTISHI_TITLE": os.path.join(IMAGE_DIR, "wenxintishi_title.png"),
    "SHILINGTISHI": os.path.join(IMAGE_DIR, "shilingtishi.png"),
    "ZHANGHAO": os.path.join(IMAGE_DIR, "zhanghao.png"),
    "DIANJIZHUCE": os.path.join(IMAGE_DIR, "dianjizhuce.png"),
}

# OCR配置
# 如果Tesseract不在系统PATH中，需要指定路径
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
OCR_LANGUAGE = "chi_sim+eng"

# 鼠标事件常量
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_ABSOLUTE = 0x8000
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004

# 全局模板缓存
TEMPLATE_CACHE = {}

# 调试参数
DELAY_MIN = 1.0
DELAY_MAX = 2.5
CONFIDENCE = 0.87  # 提高匹配阈值
CARD_CONFIDENCE = 0.6
LOADING_TIMEOUT = 5

# 新增：登录结果记录，使用字典记录每个账号的失败步骤
login_results = {"success": [], "failed": {}}  # 格式：{username: "失败步骤"}


def record_failure(username, step):
    """记录登录失败信息"""
    login_results["failed"][username] = step
    print(f"账号 {username} 登录失败: {step}")
    return False


def get_cached_template(template_path):
    """获取缓存的模板图像，避免重复加载"""
    if template_path not in TEMPLATE_CACHE:
        TEMPLATE_CACHE[template_path] = cv2.imread(template_path, cv2.IMREAD_COLOR)
    return TEMPLATE_CACHE[template_path]


def click_at(x, y):
    """使用Windows API模拟鼠标点击"""
    # 获取屏幕尺寸
    screen_width = ctypes.windll.user32.GetSystemMetrics(0)
    screen_height = ctypes.windll.user32.GetSystemMetrics(1)

    # 转换为0~65535的绝对坐标
    abs_x = int(x * 65535 / screen_width)
    abs_y = int(y * 65535 / screen_height)

    # 移动鼠标到指定位置（绝对坐标）
    ctypes.windll.user32.mouse_event(
        MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE, abs_x, abs_y, 0, 0
    )
    time.sleep(0.05)

    # 按下左键
    ctypes.windll.user32.mouse_event(MOUSEEVENTF_LEFTDOWN, abs_x, abs_y, 0, 0)
    time.sleep(0.05)

    # 松开左键
    ctypes.windll.user32.mouse_event(MOUSEEVENTF_LEFTUP, abs_x, abs_y, 0, 0)
    time.sleep(0.1)


def activate_window(title: str):
    """激活指定标题的窗口"""
    hwnd = win32gui.FindWindow(None, title)
    if hwnd != 0:
        # 如果窗口最小化，则恢复
        if win32gui.IsIconic(hwnd):
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(hwnd)
        time.sleep(0.5)  # 给系统时间切换焦点
        return True
    return False


def random_delay():
    """生成随机延迟，避免操作过于机械"""
    return random.uniform(DELAY_MIN, DELAY_MAX)


def ocr_text(image_path, lang=OCR_LANGUAGE):
    """使用OCR识别图像中的文字"""
    if not os.path.exists(image_path):
        return ""

    try:
        image = cv2.imread(image_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        text = pytesseract.image_to_string(thresh, lang=lang)
        return text.strip()
    except Exception as e:
        print(f"OCR识别出错: {str(e)}")
        return ""


def find_image_on_screen(
    template_path, threshold=CONFIDENCE, save_debug=True, color_filter=None
):
    """在屏幕上查找指定图像，结合多种匹配方式，支持颜色过滤"""
    if not os.path.exists(template_path):
        print(f"模板文件不存在: {template_path}")
        return None

    template = get_cached_template(template_path)
    if template is None:
        print(f"无法加载模板: {template_path}")
        return None

    try:
        # 截取屏幕
        screenshot = np.array(ImageGrab.grab())
        screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)

        # 应用颜色过滤（如果指定）
        if color_filter:
            lower, upper = color_filter
            # 转换到HSV颜色空间进行颜色过滤
            hsv = cv2.cvtColor(screenshot, cv2.COLOR_BGR2HSV)
            mask = cv2.inRange(hsv, lower, upper)
            screenshot = cv2.bitwise_and(screenshot, screenshot, mask=mask)

            # 同样处理模板图像
            template_hsv = cv2.cvtColor(template, cv2.COLOR_BGR2HSV)
            template_mask = cv2.inRange(template_hsv, lower, upper)
            template = cv2.bitwise_and(template, template, mask=template_mask)

        # 彩色匹配
        result_color = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        min_val_color, max_val_color, min_loc_color, max_loc_color = cv2.minMaxLoc(
            result_color
        )

        # 灰度匹配
        template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
        result_gray = cv2.matchTemplate(
            screenshot_gray, template_gray, cv2.TM_CCOEFF_NORMED
        )
        min_val_gray, max_val_gray, min_loc_gray, max_loc_gray = cv2.minMaxLoc(
            result_gray
        )

        # 二值化匹配
        _, template_binary = cv2.threshold(template_gray, 127, 255, cv2.THRESH_BINARY)
        _, screenshot_binary = cv2.threshold(
            screenshot_gray, 127, 255, cv2.THRESH_BINARY
        )
        result_binary = cv2.matchTemplate(
            screenshot_binary, template_binary, cv2.TM_CCOEFF_NORMED
        )
        min_val_bin, max_val_bin, min_loc_bin, max_loc_bin = cv2.minMaxLoc(
            result_binary
        )

        # 使用最高匹配度
        max_val = max(max_val_color, max_val_gray, max_val_bin)
        if max_val == max_val_color:
            max_loc = max_loc_color
        elif max_val == max_val_gray:
            max_loc = max_loc_gray
        else:
            max_loc = max_loc_bin

        if max_val >= threshold:
            h, w = template.shape[:2]
            center_x = max_loc[0] + w // 2
            center_y = max_loc[1] + h // 2

            # 保存识别区域用于调试
            if save_debug:
                region = screenshot[
                    max_loc[1] : max_loc[1] + h, max_loc[0] : max_loc[0] + w
                ]
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                template_name = os.path.splitext(os.path.basename(template_path))[0]
                debug_filename = f"debug_{timestamp}_{template_name}.png"
                debug_path = os.path.join(OCR_DEBUG_DIR, debug_filename)
                cv2.imwrite(debug_path, region)
                print(f"已保存识别区域: {debug_path}, 置信度: {max_val:.2f}")

            return (center_x, center_y, max_val)
        else:
            print(f"未找到图像: {template_path}, 最高匹配度: {max_val:.2f}")
            return None
    except Exception as e:
        print(f"图像识别出错: {str(e)}")
        return None


def find_text_on_screen(target_text, template_path=None, threshold=CONFIDENCE):
    """先模板匹配定位区域，再用OCR识别文字"""
    # 1. 模板匹配定位大致区域
    pos = find_image_on_screen(template_path, threshold)
    if not pos:
        return None

    x, y, _ = pos
    template = get_cached_template(template_path)
    h, w = template.shape[:2]

    # 2. 截取定位区域进行OCR识别
    screenshot = np.array(ImageGrab.grab())
    screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
    region = screenshot[y : y + h, x : x + w]

    # 保存区域图像用于OCR
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    template_name = os.path.splitext(os.path.basename(template_path))[0]
    debug_filename = f"ocr_{timestamp}_{template_name}.png"
    debug_path = os.path.join(OCR_DEBUG_DIR, debug_filename)
    cv2.imwrite(debug_path, region)

    # 3. OCR识别并比较文字
    recognized_text = ocr_text(debug_path)
    print(f"OCR识别结果: '{recognized_text}', 目标文本: '{target_text}'")

    # 简单文本相似度匹配
    if target_text in recognized_text:
        return (x, y, 1.0)
    else:
        return None


def click_on_image(template_path, click_count=1, button="left", max_attempts=2):
    """查找并点击指定图像，支持重试机制"""
    for attempt in range(max_attempts):
        pos = find_image_on_screen(template_path)

        if pos:
            x, y, confidence = pos
            print(
                f"找到图像: {template_path}, 坐标: ({x}, {y}), 置信度: {confidence:.2f}"
            )

            # 移动并点击
            pyautogui.moveTo(x, y, duration=0.2)
            pyautogui.click(button=button, clicks=click_count, interval=0.2)

            delay = random_delay()
            time.sleep(delay)
            return True
        else:
            if attempt < max_attempts - 1:
                time.sleep(5)
            else:
                return False


def click_on_image_with_ocr(
    template_path, target_text, click_count=1, button="left", max_attempts=2
):
    """结合模板匹配和OCR的点击函数"""
    for attempt in range(max_attempts):
        pos = find_text_on_screen(target_text, template_path)

        if pos:
            x, y, _ = pos

            # 移动并点击
            pyautogui.moveTo(x, y, duration=0.2)
            pyautogui.click(button=button, clicks=click_count, interval=0.2)

            delay = random_delay()
            print(f"点击后等待: {delay:.2f}秒")
            time.sleep(delay)
            return True
        else:
            if attempt < max_attempts - 1:
                print(f"第{attempt+1}次尝试未找到图像: {template_path}，等待5秒后重试")
                time.sleep(5)  # 等待5秒
                if attempt == 0:
                    print("第二次尝试点击")
            else:
                print(f"经过{max_attempts}次尝试，未找到图像: {template_path}")
                return False


def wait_for_image(template_path, timeout=LOADING_TIMEOUT, threshold=CONFIDENCE):
    """等待图像出现，超时返回False"""
    print(f"等待图像出现: {template_path}, 超时时间: {timeout}秒")
    start_time = time.time()

    while time.time() - start_time < timeout:
        pos = find_image_on_screen(template_path, threshold)
        if pos:
            return pos

        time.sleep(2)

    print(f"等待图像超时: {template_path}")
    return None


def get_window_rect(title):
    """获取窗口位置和大小"""
    hwnd = win32gui.FindWindow(None, title)
    if hwnd == 0:
        return None

    # 获取窗口客户区（不包括边框和标题栏）
    rect = win32gui.GetClientRect(hwnd)
    left, top = win32gui.ClientToScreen(hwnd, (rect[0], rect[1]))
    right, bottom = win32gui.ClientToScreen(hwnd, (rect[2], rect[3]))

    return (left, top, right, bottom)


def click_on_game_element(template_path, window_title=GAME_TITLE, target_text=None):
    """在游戏窗口中点击元素，自动处理坐标转换"""
    print(
        f"尝试点击游戏元素: {template_path}, 窗口: {window_title}, 目标文本: {target_text}"
    )

    # 激活窗口
    if not activate_window(window_title):
        print(f"无法激活窗口: {window_title}")
        return False

    # 获取游戏窗口位置
    window_rect = get_window_rect(window_title)
    if not window_rect:
        print(f"无法获取窗口位置: {window_title}")
        return False

    left, top, right, bottom = window_rect
    window_width = right - left
    window_height = bottom - top

    # 查找元素
    pos = find_image_on_screen(template_path)
    print(f"不通过target_text:'查找{template_path}:{pos}")

    if not pos:
        if target_text:
            pos = find_text_on_screen(target_text, template_path)
            print(f"通过target_text:'{target_text}'查找{template_path}:{pos}")
        else:
            print(f"未找到目标图像: {template_path}")
            return False

    x, y, _ = pos

    # 打印调试信息
    print(f"屏幕坐标: ({x}, {y})")
    print(f"窗口坐标: ({x - left}, {y - top})")
    print(f"窗口位置: ({left}, {top}, {right}, {bottom})")

    # 移动并点击
    pyautogui.moveTo(x, y, duration=0.5)
    time.sleep(0.5)

    # 确认鼠标位置
    current_x, current_y = pyautogui.position()
    print(f"移动后鼠标位置: ({current_x}, {current_y})")

    # 点击
    pyautogui.click()
    time.sleep(random_delay())

    return True


def find_card_area():
    """查找卡牌选择区域"""
    print("查找卡牌区域...")
    return find_image_on_screen(IMAGE_PATHS["CARD_AREA"], CARD_CONFIDENCE)


def select_first_card():
    """选择第一个卡牌（通过相对位置）"""
    card_area = find_card_area()

    if not card_area:
        print("未找到卡牌区域！")
        return False

    x, y, _ = card_area
    template = get_cached_template(IMAGE_PATHS["CARD_AREA"])
    h, w = template.shape[:2]

    # 计算第一个卡牌的相对位置
    card_width = w // 3
    first_card_x = x - w // 2 + card_width // 2
    first_card_y = y

    # 移动到第一个卡牌位置
    pyautogui.moveTo(first_card_x, first_card_y, duration=0.5)
    time.sleep(1)

    # 双击第一个卡牌
    pyautogui.doubleClick()
    print("已选择第一个卡牌！")
    time.sleep(random_delay())
    return True


def type_text(text, interval=0.05):
    """模拟键盘输入文本"""
    print(f"输入文本: {text}")
    pyautogui.typewrite(text, interval=interval)
    delay = random_delay() * 0.5
    print(f"输入后等待: {delay:.2f}秒")
    time.sleep(delay)


def clear_input_box():
    """清空输入框内容"""
    for _ in range(10):
        pyautogui.press("backspace")
        time.sleep(0.02)
    for _ in range(10):
        pyautogui.press("delete")
        time.sleep(0.02)


def input_account_password(username, password):
    """输入账号和密码"""
    # 定位账号输入框
    if not click_on_image(IMAGE_PATHS["ACCOUNT_BOX"]):
        # 如果识别图片失败,就定位"账号"点击注册",计算之间的距离
        # zh = find_image_on_screen(IMAGE_PATHS["ZHANGHAO"])
        # djzc = find_image_on_screen(IMAGE_PATHS["DIANJIZHUCE"])
        # print("zh", zh)
        # print("djzc", djzc)
        return False

    # 清空输入框
    clear_input_box()

    # 输入账号
    type_text(username)

    # 定位密码输入框
    if not click_on_image(IMAGE_PATHS["PASSWORD_BOX"]):
        return False

    # 清空输入框
    clear_input_box()

    # 输入密码
    type_text(password)

    # 点击登录按钮（使用OCR验证）
    # return click_on_image_with_ocr(IMAGE_PATHS["LOGIN_BUTTON"], "登录")
    return click_on_image(IMAGE_PATHS["LOGIN_BUTTON"])


def start_game():
    """通过文件路径启动游戏"""
    try:
        if not os.path.exists(GAME_EXE_PATH):
            print(f"游戏文件不存在: {GAME_EXE_PATH}")
            return False

        subprocess.Popen(GAME_EXE_PATH)
        print(f"已成功启动游戏，等待{LOADING_TIMEOUT}秒...")
        time.sleep(LOADING_TIMEOUT)  # 等待游戏启动
        return True
    except Exception as e:
        print(f"启动游戏出错: {str(e)}")
        return False


def minimize_current_window():
    """最小化当前活动窗口"""
    try:
        # 等待一小段时间确保窗口已激活
        time.sleep(1)

        # 获取当前活动窗口并最小化
        current_window = gw.getActiveWindow()
        current_window.minimize()
        return True
    except:
        return False


# 手动更新服务器
def handle_update():
    """处理服务器手动更新"""
    # 查找手动更新按钮并点击
    if not click_on_image(IMAGE_PATHS["HANDLE_SELECT"]):
        print("点击handle_select失败")
        return False

    # 查找confirm截图并点击
    if not click_on_image(IMAGE_PATHS["CONFIRM"]):
        print("点击confirm失败")
        return False

    time.sleep(2)
    return True


# 自动获取服务器
def find_server(timeout=10, interval=1):
    """尝试在timeout秒内查找服务器，每interval秒查找一次"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        server_pos = find_image_on_screen(IMAGE_PATHS["SERVER_1"])
        if server_pos:
            if not click_on_image(IMAGE_PATHS["CONFIRM_SELECT"]):
                print("点击确认选择失败")
                return False
            return True
        else:
            server_failed = find_image_on_screen(IMAGE_PATHS["SERVER_FAILED"])
            if server_failed:
                print("自动获取服务器失败，准备手动更新")
                if not handle_update():
                    print("手动更新失败")
                    return False
            else:
                print("服务器未找到，继续查找...")
                time.sleep(interval)
    return None  # 超时未找到


def login_account(username, password):
    """登录单个账号的完整流程"""

    # 1. 通过文件路径启动游戏
    print("步骤1: 启动游戏...")
    if not start_game():
        return record_failure(username, "启动游戏失败")

    # 等待游戏窗口出现
    max_attempts = 10
    for attempt in range(max_attempts):
        hwnd = win32gui.FindWindow(None, GAME_TITLE)
        if hwnd != 0:
            print("已检测到游戏窗口")
            break
        time.sleep(2)
    else:
        print("未检测到游戏窗口，登录下一账号...")
        return record_failure(username, "未检测到游戏窗口")

    # 2. 点击"进入游戏"按钮
    print("步骤2: 进入游戏...")
    if not wait_for_image(IMAGE_PATHS["ENTER_GAME"]):
        return record_failure(username, "未找到'进入游戏'按钮")

    if not click_on_image(IMAGE_PATHS["ENTER_GAME"]):
        return record_failure(username, "点击'进入游戏'按钮失败")

    # 3. 点击"确认选择"按钮
    print("步骤3: 检查服务器")
    max_attempts = 3
    attempts = 0

    while attempts < max_attempts:
        result = find_server(timeout=30, interval=2)
        if result is True:
            print("服务器检测成功")
            break  # 跳出循环，继续执行后续步骤
        elif result is False:
            print("查找过程中出现错误，退出")
            return record_failure(username, "查找服务器过程中出现错误")
        else:
            print(f"第{attempts+1}次尝试超时，进行手动更新")
            if not handle_update():
                print("手动更新失败，退出")
                return record_failure(username, "手动更新服务器失败")
            attempts += 1
    else:
        print(f"达到最大尝试次数{max_attempts}，仍未检测到服务器，退出")
        return record_failure(username, "检测服务器超时")

    # 4. 等待进度条加载完毕，点击"开始游戏"
    print("步骤4: 等待加载并开始游戏...")

    # 查找更新完成进度条
    start_time = time.time()
    # finish_update = None
    finish_update = find_image_on_screen(IMAGE_PATHS["FINISH_UPDATE"])
    print(f"1.查找更新完成进度条{finish_update}")

    while time.time() - start_time < 30:
        finish_update = find_image_on_screen(IMAGE_PATHS["FINISH_UPDATE"])
        print(f"2.查找更新完成进度条{finish_update}")

        if finish_update:
            time.sleep(3)
            print(f"等待3秒")
            # 更新后再开始游戏
            start_game_button = find_image_on_screen(IMAGE_PATHS["START_GAME"])
            if not start_game_button:
                print(f"1.未找到更新完成")
                return record_failure(username, "未找到'开始游戏'按钮")

            if not click_on_image(IMAGE_PATHS["START_GAME"]):
                print(f"2.未点击进入游戏")
                return record_failure(username, "点击'开始游戏'按钮失败")
            break
        else:
            print("未找到 '更新完成'，继续查找...")
            time.sleep(2)  # 等待2秒后再次查找
    else:  # while循环超时后执行
        print("超时30秒未检测到 '更新完成'")
        return record_failure(username, "等待更新完成超时")

    # === 步骤5：点击“是(进入按钮)” ===
    # 温馨提示窗口不适用pyautogui.moveTo,应该用低级的移动方法
    print("步骤5: 点击是(进入按钮)...")
    print("等待2秒后开始寻找是按钮...")
    time.sleep(2)  # 等待2秒

    start_time = time.time()
    window_found = False

    while time.time() - start_time < 30:
        if activate_window("温馨提示"):
            window_found = True
            print("已找到‘温馨提示’窗口,开始查找按钮")
            time.sleep(1)  # 确保窗口激活完全
            break
        else:
            print("未找到‘温馨提示’窗口，3秒后继续查找...")
            time.sleep(3)

    if not window_found:
        print("超时30秒未找到‘温馨提示’窗口，无法继续操作")
        return record_failure(username, "未找到‘温馨提示’窗口")

    if not click_on_game_element(IMAGE_PATHS["YES_BUTTON"], "温馨提示", "是(进入)"):
        print("点击'是'按钮失败")
        return record_failure(username, "点击'是(进入)'按钮失败")

    # 6. 点击"确认"按钮
    print("步骤6: 点击确认...")
    if not click_on_image(IMAGE_PATHS["CONFIRM_BUTTON"]):
        return record_failure(username, "点击'确认'按钮失败")

    # 7. 输入账号和密码
    print("步骤7: 输入账号密码...")
    if not input_account_password(username, password):
        return record_failure(username, "输入账号密码失败")

    # 8. 等待登录完成，选择第一个卡牌
    print("步骤8: 选择第一个卡牌...")
    if not select_first_card():
        return record_failure(username, "选择第一个卡牌失败")

    # 9. 如果游戏界面有确定按钮,点击确定
    print("步骤9: 检测游戏界面")
    game_confirm = find_image_on_screen(IMAGE_PATHS["GAME_CONFIRM"])
    if game_confirm:
        x, y, _ = game_confirm
        pyautogui.moveTo(x, y, duration=0.3)
        time.sleep(0.2)
        # 使用低级API点击，提升兼容性
        click_at(x, y)
        time.sleep(random_delay())
    else:
        print("[步骤9] 未找到'确定'按钮,继续下一步")

    # 10. 最小化窗口
    print("步骤10: 已登录,即将缩小窗口")
    result = minimize_current_window()
    print(f"窗口最小化{'成功' if result else '失败'}")

    # 记录登录成功
    login_results["success"].append(username)
    print(f"账号 {username} 登录成功!")
    return True


def test_image_recognition(image_name):
    """测试单个图像识别功能"""
    if image_name in IMAGE_PATHS:
        image_path = IMAGE_PATHS[image_name]
    else:
        image_path = os.path.join(IMAGE_DIR, image_name)

    print(f"测试图像识别: {image_path}")
    if not os.path.exists(image_path):
        print(f"图像文件不存在: {image_path}")
        return

    pos = find_image_on_screen(image_path)
    if pos:
        x, y, confidence = pos
        print(f"识别成功! 坐标: ({x}, {y}), 置信度: {confidence:.2f}")

        # 移动鼠标到识别位置
        pyautogui.moveTo(x, y, duration=0.5)
        time.sleep(2)
    else:
        pass


def get_mouse_position():
    """获取当前鼠标位置（用于调试）"""
    print("将鼠标移动到目标位置，按Ctrl+C停止...")
    try:
        while True:
            x, y = pyautogui.position()
            print(f"当前坐标: ({x}, {y})", end="\r")
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n已停止获取坐标")
        return x, y


def save_login_results():
    """保存登录结果到日志文件"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(LOGS_DIR, f"login_results_{timestamp}.txt")

    with open(log_file, "w", encoding="utf-8") as f:
        f.write("=" * 50 + "\n")
        f.write(f"登录结果统计 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 50 + "\n\n")

        f.write("成功登录的账号:\n")
        f.write("-" * 30 + "\n")
        for idx, account in enumerate(login_results["success"], 1):
            f.write(f"{idx}. {account}\n")
        f.write(f"\n成功总数: {len(login_results['success'])}\n\n")

        f.write("登录失败的账号:\n")
        f.write("-" * 30 + "\n")
        for idx, (account, step) in enumerate(login_results["failed"].items(), 1):
            f.write(f"{idx}. {account} - 失败步骤: {step}\n")
        f.write(f"\n失败总数: {len(login_results['failed'])}\n\n")

        f.write("=" * 50 + "\n")
        f.write(
            f"总账号数: {len(login_results['success']) + len(login_results['failed'])}\n"
        )

    print(f"\n登录结果已保存至: {log_file}")


def print_login_summary():
    """打印登录结果摘要"""
    print("\n" + "=" * 50)
    print("登录结果统计")
    print("=" * 50)

    print("\n成功登录的账号:")
    print("-" * 30)
    for idx, account in enumerate(login_results["success"], 1):
        print(f"{idx}. {account}")
    print(f"\n成功总数: {len(login_results['success'])}")

    print("\n登录失败的账号:")
    print("-" * 30)
    for idx, (account, step) in enumerate(login_results["failed"].items(), 1):
        print(f"{idx}. {account} - 失败步骤: {step}")
    print(f"\n失败总数: {len(login_results['failed'])}")

    print("\n" + "=" * 50)
    print(f"总账号数: {len(login_results['success']) + len(login_results['failed'])}")
    print("=" * 50 + "\n")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="游戏自动登录脚本")
    parser.add_argument("--debug", action="store_true", help="启用调试模式")
    parser.add_argument("--test", type=str, help="测试特定图像识别")
    parser.add_argument("--position", action="store_true", help="获取鼠标位置")
    args = parser.parse_args()

    # 测试模式
    if args.test:
        test_image_recognition(args.test)
        return

    # 获取鼠标位置模式
    if args.position:
        get_mouse_position()
        return

    # 检查账号文件
    ACCOUNTS_FILE = os.path.join(DATA_DIR, "accounts.csv")
    if not os.path.exists(ACCOUNTS_FILE):
        print(f"账号文件不存在: {ACCOUNTS_FILE}")
        return

    with open(ACCOUNTS_FILE, "r", encoding="utf-8") as file:
        reader = csv.reader(file)
        accounts = list(reader)

    total = len(accounts)
    print(f"准备登录 {total} 个账号...")

    # 遍历账号列表
    for i, (username, password) in enumerate(accounts, 1):
        print(f"\n===== 开始登录账号 {i}/{total}: {username} =====")

        # 当前账号连续20次失败就终止脚本

        max_attempts = 20  # 每个账号最多尝试20次
        consecutive_failures = 0  # 连续失败次数

        while consecutive_failures < max_attempts:
            success = login_account(username, password)

            if success:
                print(f"账号 {username} 登录成功，准备下一个账号")
                break  # 成功登录，跳出重试循环
            else:
                consecutive_failures += 1
                print(f"账号 {username} 第 {consecutive_failures} 次登录失败")

                if consecutive_failures < max_attempts:
                    # 关闭当前游戏窗口
                    if activate_window("烈焰飞雪：征战[1服-锐不可当](VER:1.2.2153)"):
                        print("关闭游戏窗口...")
                        pyautogui.hotkey("alt", "f4")  # 发送Alt+F4关闭窗口
                        time.sleep(3)  # 等待3秒

                    print(f"将在 {LOADING_TIMEOUT} 秒后重试...")
                    time.sleep(LOADING_TIMEOUT)
                else:
                    print(
                        f"账号 {username} 连续 {max_attempts} 次登录失败，终止所有账号的登录"
                    )
                    # 打印登录结果摘要
                    print_login_summary()
                    # 保存登录结果到日志文件
                    save_login_results()
                    return  # 终止所有账号的登录

        # 账号成功登录或者达到最大重试次数后，等待一段时间再处理下一个账号
        if consecutive_failures < max_attempts and i < total:
            delay = random_delay() * 3
            print(f"等待 {delay:.2f} 秒后登录下一个账号...")
            time.sleep(delay)

    # 打印登录结果摘要
    print_login_summary()
    # 保存登录结果到日志文件
    save_login_results()


# 调用此脚本函数
def autoL():
    """
    封装的自动登录主函数，供外部调用。
    直接调用原有main()的核心登录逻辑。
    """
    # 重置登录结果
    global login_results
    login_results = {"success": [], "failed": {}}

    # 这里复用main()里的账号读取和登录流程
    # 但不使用argparse，直接执行登录流程

    # 检查账号文件
    ACCOUNTS_FILE = os.path.join(DATA_DIR, "accounts.csv")
    if not os.path.exists(ACCOUNTS_FILE):
        print(f"账号文件不存在: {ACCOUNTS_FILE}")
        return False

    with open(ACCOUNTS_FILE, "r", encoding="utf-8") as file:
        reader = csv.reader(file)
        accounts = list(reader)

    total = len(accounts)
    print(f"准备登录 {total} 个账号...")

    # 遍历账号列表
    for i, (username, password) in enumerate(accounts, 1):
        print(f"\n===== 开始登录账号 {i}/{total}: {username} =====")

        success = login_account(username, password)

        if not success:
            print(f"账号 {username} 登录失败，跳过...")
            continue

        if i < total:
            delay = random_delay() * 3
            print(f"等待 {delay:.2f} 秒后登录下一个账号...")
            time.sleep(delay)

    # 打印登录结果摘要
    print_login_summary()

    # 保存登录结果到日志文件
    save_login_results()

    return True


# 独立运行此脚本(勿删)
if __name__ == "__main__":
    print("脚本将在3秒后开始，请不要操作电脑...")
    time.sleep(3)
    main()
