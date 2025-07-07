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
import logging
import subprocess
import ctypes
import pygetwindow as gw  # 添加窗口控制库

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="auto_login.log",
)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter("%(levelname)s - %(message)s")
console.setFormatter(formatter)
logging.getLogger("").addHandler(console)

# 禁用安全特性
pyautogui.FAILSAFE = False

# 项目目录结构
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_DIR = os.path.join(os.path.dirname(ROOT_DIR), "image")
DATA_DIR = os.path.join(os.path.dirname(ROOT_DIR), "data")
DEBUG_DIR = os.path.join(os.path.dirname(ROOT_DIR), "debug")

# 创建调试目录
if not os.path.exists(DEBUG_DIR):
    os.makedirs(DEBUG_DIR)

# 配置参数
GAME_EXE_PATH = r"D:\新烈焰飞雪\烈焰飞雪\7hero.exe"  # 游戏可执行文件路径
GAME_TITLE = "烈焰飞雪"  # 游戏窗口标题
ENTER_GAME = os.path.join(IMAGE_DIR, "enter_game.png")
CONFIRM_SELECT = os.path.join(IMAGE_DIR, "confirm_select.png")
START_GAME = os.path.join(IMAGE_DIR, "start_game.png")
YES_BUTTON = os.path.join(IMAGE_DIR, "yes_button.png")
CONFIRM_BUTTON = os.path.join(IMAGE_DIR, "confirm_button.png")
ACCOUNT_BOX = os.path.join(IMAGE_DIR, "account_box.png")
PASSWORD_BOX = os.path.join(IMAGE_DIR, "password_box.png")
LOGIN_BUTTON = os.path.join(IMAGE_DIR, "login_button.png")
CARD_AREA = os.path.join(IMAGE_DIR, "card_area.png")
AUTO_HANGUP = os.path.join(IMAGE_DIR, "auto_hangup.png")
ACCOUNTS_FILE = os.path.join(DATA_DIR, "accounts.csv")
SERVER_1 = os.path.join(IMAGE_DIR, "server_1.png")
SERVER_FAILED = os.path.join(IMAGE_DIR, "server_failed.png")
FINISH_UPDATE = os.path.join(IMAGE_DIR, "finish_update.png")
HANDLE_SELECT = os.path.join(IMAGE_DIR, "handle_select.png")
CONFIRM = os.path.join(IMAGE_DIR, "confirm.png")
GAME_CONFIRM = os.path.join(IMAGE_DIR, "game_confirm.png")


# 鼠标事件常量
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_ABSOLUTE = 0x8000
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004


def click_at(x, y):
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


def activate_popup_window(title: str):
    hwnd = win32gui.FindWindow(None, title)
    if hwnd != 0:
        win32gui.SetForegroundWindow(hwnd)
        return True
    else:
        return False


# 调试参数
DELAY_MIN = 1.0
DELAY_MAX = 2.5
CONFIDENCE = 0.7  # 降低匹配阈值，提高识别成功率
CARD_CONFIDENCE = 0.6
LOADING_TIMEOUT = 3  # 启动等待时间改为3秒


def random_delay():
    """生成随机延迟，避免操作过于机械"""
    return random.uniform(DELAY_MIN, DELAY_MAX)


def find_image_on_screen(template_path, threshold=CONFIDENCE):
    """在屏幕上查找指定图像"""
    if not os.path.exists(template_path):
        logging.error(f"模板文件不存在: {template_path}")
        return None

    template = cv2.imread(template_path, cv2.IMREAD_COLOR)
    if template is None:
        logging.error(f"无法加载模板: {template_path}")
        return None

    try:
        # 同时尝试彩色和灰度匹配，取最高匹配度
        screenshot = np.array(ImageGrab.grab())
        screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)

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

        # 使用匹配度更高的结果
        if max_val_color > max_val_gray:
            max_val, max_loc = max_val_color, max_loc_color
        else:
            max_val, max_loc = max_val_gray, max_loc_gray

        if max_val >= threshold:
            h, w, _ = template.shape
            center_x = max_loc[0] + w // 2
            center_y = max_loc[1] + h // 2
            # logging.info(f"找到图像: {template_path}, 置信度: {max_val:.2f}")
            return (center_x, center_y, max_val)
        else:
            logging.debug(f"未找到图像: {template_path}, 最高匹配度: {max_val:.2f}")
            return None
    except Exception as e:
        logging.error(f"图像识别出错: {str(e)}")
        return None


# def safe_grab(region, output_path):
#     """安全的截图函数，处理可能的坐标错误"""
#     try:
#         # 确保区域坐标有效
#         left, top, right, bottom = region
#         if right <= left or bottom <= top:
#             logging.warning(f"无效的截图区域: {region}，调整为默认大小")
#             left = max(0, left)
#             top = max(0, top)
#             right = left + 100
#             bottom = top + 100

#         # 确保文件扩展名正确
#         filename, ext = os.path.splitext(output_path)
#         if not ext:
#             output_path = f"{filename}.png"

#         # ImageGrab.grab((left, top, right, bottom)).save(output_path)
#         # logging.info(f"成功保存截图: {output_path}")
#     except Exception as e:
#         logging.error(f"截图失败: {str(e)}")
#         # 保存全屏幕截图作为备选
#         try:
#             # 再次确保扩展名正确
#             filename, ext = os.path.splitext(output_path)
#             if not ext:
#                 output_path = f"{filename}.png"
#             ImageGrab.grab().save(output_path)
#         except Exception as e:
#             logging.error(f"保存全屏截图失败: {str(e)}")


def click_on_image(
    template_path, click_count=1, button="left", debug=True, max_attempts=2
):
    """查找并点击指定图像，支持重试机制"""
    for attempt in range(max_attempts):
        pos = find_image_on_screen(template_path)

        if pos:
            x, y, confidence = pos
            logging.info(
                f"找到图像: {template_path}, 坐标: ({x}, {y}), 置信度: {confidence:.2f}"
            )

            # 移动并点击
            pyautogui.moveTo(x, y, duration=0.2)
            pyautogui.click(button=button, clicks=click_count, interval=0.2)

            # 调试截图
            if debug:
                width, height = 100, 100
                left = max(0, x - width // 2)
                top = max(0, y - height // 2)
                right = left + width
                bottom = top + height

                # 正确处理文件名和扩展名
                base_name = os.path.basename(template_path)
                file_name, ext = os.path.splitext(base_name)
                if not ext:
                    ext = ".png"
                screenshot_name = f"clicked_{file_name}_attempt{attempt+1}{ext}"

                # safe_grab((left, top, right, bottom), os.path.join(DEBUG_DIR, screenshot_name))

            delay = random_delay()
            logging.debug(f"点击后等待: {delay:.2f}秒")
            time.sleep(delay)
            return True
        else:
            if attempt < max_attempts - 1:
                logging.warning(
                    f"第{attempt+1}次尝试未找到图像: {template_path}，等待5秒后重试"
                )
                time.sleep(5)  # 等待5秒
                if attempt == 0:
                    logging.info("第二次尝试点击")
            else:
                logging.error(f"经过{max_attempts}次尝试，未找到图像: {template_path}")
                if debug:
                    # 正确处理文件名和扩展名
                    base_name = os.path.basename(template_path)
                    file_name, ext = os.path.splitext(base_name)
                    if not ext:
                        ext = ".png"
                    screenshot_name = f"not_found_{file_name}{ext}"

                    # safe_grab((0, 0, pyautogui.size().width, pyautogui.size().height),
                    #           os.path.join(DEBUG_DIR, screenshot_name))
                return False


def wait_for_image(template_path, timeout=LOADING_TIMEOUT, threshold=CONFIDENCE):
    """等待图像出现，超时返回False"""
    logging.info(f"等待图像出现: {template_path}, 超时时间: {timeout}秒")
    start_time = time.time()

    while time.time() - start_time < timeout:
        pos = find_image_on_screen(template_path, threshold)
        if pos:
            return pos

        time.sleep(2)  # 每2秒检查一次

    logging.warning(f"等待图像超时: {template_path}")
    return None


def find_card_area():
    """查找卡牌选择区域"""
    logging.info("查找卡牌区域...")
    return find_image_on_screen(CARD_AREA, CARD_CONFIDENCE)


def select_first_card():
    """选择第一个卡牌（通过相对位置）"""
    card_area = find_card_area()

    if not card_area:
        logging.error("未找到卡牌区域！")
        return False

    x, y, _ = card_area
    template = cv2.imread(CARD_AREA)
    h, w, _ = template.shape

    # 计算第一个卡牌的相对位置
    card_width = w // 3
    first_card_x = x - w // 2 + card_width // 2
    first_card_y = y

    # 调试模式下绘制选择区域
    # logging.info(
    #     f"卡牌区域: 左上角=({x-w//2}, {y-h//2}), 右下角=({x+w//2}, {y+h//2})"
    # )
    # logging.info(f"第一个卡牌位置: ({first_card_x}, {first_card_y})")

    # 绘制卡牌区域边界
    pyautogui.moveTo(x - w // 2, y - h // 2, duration=0.2)
    pyautogui.moveTo(x + w // 2, y - h // 2, duration=0.2)
    pyautogui.moveTo(x + w // 2, y + h // 2, duration=0.2)
    pyautogui.moveTo(x - w // 2, y + h // 2, duration=0.2)
    pyautogui.moveTo(x, y, duration=0.2)

    # 移动到第一个卡牌位置
    pyautogui.moveTo(first_card_x, first_card_y, duration=0.5)
    time.sleep(1)

    # 双击第一个卡牌
    pyautogui.doubleClick()
    logging.info("已选择第一个卡牌！")
    time.sleep(random_delay())
    return True


def type_text(text, interval=0.05):
    """模拟键盘输入文本"""
    logging.info(f"输入文本: {text}")
    pyautogui.typewrite(text, interval=interval)
    delay = random_delay() * 0.5
    logging.debug(f"输入后等待: {delay:.2f}秒")
    time.sleep(delay)


def clear_input_box():
    """清空输入框内容并验证"""
    logging.info("清空输入框...")

    # 尝试清空输入框（最多3次重试）
    # for attempt in range(3):
    # 针对游戏界面优化的输入框清空方法
    # 将光标移动到最右侧（假设最多30个字符）
    for _ in range(10):
        pyautogui.press("backspace")
        time.sleep(0.02)
    for _ in range(10):
        pyautogui.press("delete")
        time.sleep(0.02)
    logging.info("已左右删除20个字符")

    # 验证是否已清空（通过再次全选查看是否有内容被选中）
    # pyautogui.hotkey('ctrl', 'a')
    # time.sleep(0.2)

    # 按下退格键，如果有内容被选中则会删除，产生退格音效
    # pyautogui.press('backspace')
    # time.sleep(0.2)

    # 检查剪贴板（如果有内容被复制，说明未清空）
    # try:
    #     pyautogui.hotkey('ctrl', 'c')  # 复制选中内容
    #     time.sleep(0.2)
    #     import pyperclip
    #     clipboard_content = pyperclip.paste()
    #     if not clipboard_content.strip():
    #         logging.info("输入框已清空")
    #         return True
    #     else:
    #         logging.warning(f"第{attempt+1}次尝试后输入框仍未清空，残留内容: {clipboard_content[:20]}...")
    # except Exception as e:
    #     logging.warning(f"无法检查剪贴板: {str(e)}")

    # 如果是最后一次尝试仍未清空，记录错误
    # if attempt == 2:
    # logging.error("输入框无法完全清空！")
    # return False

    # return False


def input_account_password(username, password):
    """输入账号和密码"""
    # 定位账号输入框
    if not click_on_image(ACCOUNT_BOX):
        return False

    # 清空输入框并验证
    if not clear_input_box():
        logging.error("账号输入框清空失败，继续执行但可能导致输入异常")

    # 输入账号
    type_text(username)

    # 定位密码输入框
    if not click_on_image(PASSWORD_BOX):
        return False

    # 清空并验证
    if not clear_input_box():
        logging.error("密码输入框清空失败，继续执行但可能导致输入异常")

    # 输入密码
    type_text(password)

    # 点击登录按钮
    return click_on_image(LOGIN_BUTTON)


def activate_game_window(title=GAME_TITLE, max_attempts=5):
    """激活游戏窗口，增加重试机制和详细调试信息"""
    logging.info(f"尝试激活游戏窗口: {title}")

    for attempt in range(max_attempts):
        try:
            # 尝试查找窗口
            hwnd = win32gui.FindWindow(None, title)

            if hwnd == 0:
                # 未找到窗口，打印调试信息
                logging.warning(
                    f"尝试 {attempt+1}/{max_attempts}: 未找到游戏窗口: {title}"
                )
                continue

            # 找到窗口，打印窗口信息
            logging.info(f"找到窗口: {title}, 句柄: {hwnd}")

            # 获取窗口状态
            is_minimized = win32gui.IsIconic(hwnd)
            is_visible = win32gui.IsWindowVisible(hwnd)
            logging.info(f"窗口状态: 最小化={is_minimized}, 可见={is_visible}")

            # 如果窗口最小化，则恢复
            if is_minimized:
                logging.info("窗口处于最小化状态，尝试恢复")
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                time.sleep(0.5)

            # 激活窗口
            logging.info("尝试将窗口置于前台")
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(1)

            # 验证窗口是否成功激活
            active_hwnd = win32gui.GetForegroundWindow()
            if active_hwnd == hwnd:
                logging.info(f"已成功激活游戏窗口: {title}")
                return True
            else:
                logging.warning(f"窗口未成功激活，当前前台窗口句柄: {active_hwnd}")

        except Exception as e:
            logging.error(f"尝试 {attempt+1}/{max_attempts}: 激活窗口出错: {str(e)}")
            time.sleep(2)

    logging.error(f"经过 {max_attempts} 次尝试，仍未找到或激活游戏窗口: {title}")
    return False


def activate_popup_window(title="温馨提示"):
    """激活弹窗窗口"""
    logging.info(f"尝试激活弹窗窗口: {title}")

    hwnd = win32gui.FindWindow(None, title)
    if hwnd == 0:
        logging.error(f"未找到弹窗窗口: {title}")
        return False

    is_minimized = win32gui.IsIconic(hwnd)
    if is_minimized:
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)

    win32gui.SetForegroundWindow(hwnd)
    time.sleep(2)  # 给系统时间激活

    logging.info(f"已激活窗口: {title}")
    return True


def start_game():
    """通过文件路径启动游戏"""
    try:
        # 检查文件是否存在
        if not os.path.exists(GAME_EXE_PATH):
            logging.error(f"游戏文件不存在: {GAME_EXE_PATH}")
            return False

        # 启动游戏
        subprocess.Popen(GAME_EXE_PATH)
        logging.info(f"已成功启动游戏，等待{LOADING_TIMEOUT}秒...")
        time.sleep(LOADING_TIMEOUT)  # 等待游戏启动
        return True
    except Exception as e:
        logging.error(f"启动游戏出错: {str(e)}")
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
    # 查找手动更新按钮并点击
    handle_pos = find_image_on_screen(HANDLE_SELECT)
    if not handle_pos:
        logging.error("未找到handle_select截图")
        return False
    if not click_on_image(HANDLE_SELECT):
        logging.error("点击handle_select失败")
        return False

    # 查找confirm截图并点击
    confirm_pos = find_image_on_screen(CONFIRM)
    if not confirm_pos:
        logging.error("未找到confirm截图")
        return False
    if not click_on_image(CONFIRM):
        logging.error("点击confirm失败")
        return False

    time.sleep(2)  # 等待2秒
    return True


# 自动获取服务器
def find_server(timeout=10, interval=1):
    """尝试在timeout秒内查找服务器，每interval秒查找一次"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        server_pos = find_image_on_screen(SERVER_1)
        if server_pos:
            x, y, confidence = server_pos
            logging.info(f"已检测到服务器，坐标: ({x}, {y})，置信度: {confidence:.2f}")
            if not click_on_image(CONFIRM_SELECT):
                logging.error("点击确认选择失败")
                return False
            return True
        else:
            server_failed = find_image_on_screen(SERVER_FAILED)
            if server_failed:
                logging.info("自动获取服务器失败，准备手动更新")
                if not handle_update():
                    logging.error("手动更新失败")
                    return False
            else:
                logging.debug("服务器未找到，继续查找...")
            time.sleep(interval)
    return None  # 超时未找到


def login_account(username, password):
    """登录单个账号的完整流程"""

    # 1. 通过文件路径启动游戏
    logging.info("步骤1: 启动游戏...")
    if not start_game():
        return False

    # 等待游戏窗口出现
    max_attempts = 3
    for attempt in range(max_attempts):
        hwnd = win32gui.FindWindow(None, GAME_TITLE)
        if hwnd != 0:
            logging.info("已检测到游戏窗口")
            break
        time.sleep(2)
    else:
        logging.warning("未检测到游戏窗口，继续执行后续步骤...")

    # 2. 点击"进入游戏"按钮
    logging.info("步骤2: 进入游戏...")
    if not wait_for_image(ENTER_GAME):
        return False

    if not click_on_image(ENTER_GAME):
        return False

    # 3. 点击"确认选择"按钮
    logging.info("步骤3: 检查服务器")
    max_attempts = 3
    attempts = 0

    while attempts < max_attempts:
        result = find_server(timeout=30, interval=2)
        if result is True:
            logging.info("服务器检测成功")
            break  # 跳出循环，继续执行后续步骤
        elif result is False:
            logging.error("查找过程中出现错误，退出")
            break  # 出错跳出循环，后面不执行步骤4
        else:
            logging.info(f"第{attempts+1}次尝试超时，进行手动更新")
            if not handle_update():
                logging.error("手动更新失败，退出")
                break
            attempts += 1
    else:
        logging.error(f"达到最大尝试次数{max_attempts}，仍未检测到服务器，退出")
        return False

    # 4. 等待进度条加载完毕，点击"开始游戏"
    logging.info("步骤4: 等待加载并开始游戏...")

    # 查找更新完成进度条
    start_time = time.time()
    finish_update = None

    while time.time() - start_time < 30:
        finish_update = find_image_on_screen(FINISH_UPDATE)
        if finish_update:
            x, y, confidence = finish_update
            logging.info(
                f"已检测到 '更新完成'，坐标: ({x}, {y})，置信度: {confidence:.2f}"
            )
            time.sleep(2)  # 等待2秒

            # 更新后再开始游戏
            start_game_button = find_image_on_screen(START_GAME)
            if start_game_button:
                x, y, confidence = start_game_button
                logging.info(
                    f"已检测到 '开始游戏'，坐标: ({x}, {y})，置信度: {confidence:.2f}"
                )
            else:
                logging.warning("未检测到 '开始游戏'")
                return False

            if not click_on_image(START_GAME):
                logging.error("点击开始游戏按钮失败")
                return False
            else:
                logging.info("成功点击开始游戏按钮")
            # 找到并处理完成后跳出循环
            break
        else:
            logging.debug("未找到 '更新完成'，继续查找...")
            time.sleep(2)  # 等待2秒后再次查找
    else:  # while循环超时后执行
        logging.warning("超时30秒未检测到 '更新完成'")
        return False  # 超时返回失败

    # === 步骤5：点击“是(进入按钮)” ===
    logging.info("步骤5: 点击是(进入按钮)...")
    logging.info("等待3秒后开始寻找是按钮...")
    time.sleep(3)  # 等待3秒

    start_time = time.time()
    window_found = False

    while time.time() - start_time < 30:
        if activate_popup_window("温馨提示"):
            window_found = True
            logging.info("已找到‘温馨提示’窗口,开始查找按钮")
            time.sleep(2)  # 确保窗口激活完全
            break
        else:
            logging.debug("未找到‘温馨提示’窗口，5秒后继续查找...")
            time.sleep(5)

    if not window_found:
        logging.error("超时30秒未找到‘温馨提示’窗口，无法继续操作")
        return False

    pos = find_image_on_screen(YES_BUTTON)
    if pos:
        x, y, confidence = pos
        logging.info(f"[步骤5] 找到'是'按钮位置: ({x}, {y})，置信度: {confidence:.2f}")
        # 移动鼠标到目标，给系统一点反应时间
        pyautogui.moveTo(x, y, duration=0.3)
        time.sleep(0.2)
        # 使用低级API点击，提升兼容性
        click_at(x, y)
        time.sleep(random_delay())  # 你已有的随机等待函数
    else:
        logging.error("[步骤5] 未找到'是'按钮图像")
        return False

    # 6. 点击"确认"按钮
    logging.info("步骤6: 点击确认...")
    if not click_on_image(CONFIRM_BUTTON):
        return False

    # 7. 输入账号和密码
    logging.info("步骤7: 输入账号密码...")
    if not input_account_password(username, password):
        return False

    # 8. 等待登录完成，选择第一个卡牌
    logging.info("步骤8: 选择第一个卡牌...")
    if not select_first_card():
        return False

    # 9. 如果游戏界面有确定按钮,点击确定
    logging.info("步骤9: 检测游戏界面")
    game_confirm = find_image_on_screen(GAME_CONFIRM)
    if game_confirm:
        x, y, confidence = game_confirm
        logging.info(
            f"[步骤9] 找到'确定'按钮位置: ({x}, {y})，置信度: {confidence:.2f}"
        )
        # 移动鼠标到目标，给系统一点反应时间
        pyautogui.moveTo(x, y, duration=0.3)
        time.sleep(0.2)
        # 使用低级API点击，提升兼容性
        click_at(x, y)
        time.sleep(random_delay())  # 你已有的随机等待函数
    else:
        logging.error("[步骤9] 未找到'确定'按钮,继续下一步")

    # 10. 最小化窗口
    logging.info("步骤10: 已登录,即将缩小窗口")
    if __name__ == "__main__":
        result = minimize_current_window()
    print(f"窗口最小化{'成功' if result else '失败'}")

    # 10. 按下V快捷键
    # logging.info("步骤10: 按下V快捷键...")
    # pyautogui.press('v')
    # delay = random_delay()
    # logging.debug(f"按下V后等待: {delay:.2f}秒")
    # time.sleep(delay)

    # # 11. 点击"自动挂机"按钮
    # logging.info("步骤11: 开启自动挂机...")
    # if not click_on_image(AUTO_HANGUP):
    #     logging.warning("未找到自动挂机按钮，可能已自动开始")

    # logging.info(f"账号 {username} 已成功进入自动挂机状态！")
    # return True


def test_image_recognition(image_path):
    """测试单个图像识别功能"""
    logging.info(f"测试图像识别: {image_path}")

    if not os.path.exists(image_path):
        logging.error(f"图像文件不存在: {image_path}")
        return

    pos = find_image_on_screen(image_path)
    if pos:
        x, y, confidence = pos
        logging.info(f"识别成功! 坐标: ({x}, {y}), 置信度: {confidence:.2f}")

        # 移动鼠标到识别位置
        pyautogui.moveTo(x, y, duration=0.5)
        time.sleep(2)

        # 截取识别区域
        width, height = 100, 100
        left = max(0, x - width // 2)
        top = max(0, y - height // 2)
        right = left + width
        bottom = top + height

        # 正确处理文件名和扩展名
        base_name = os.path.basename(image_path)
        file_name, ext = os.path.splitext(base_name)
        if not ext:
            ext = ".png"
        screenshot_name = f"test_{file_name}{ext}"

        # safe_grab((left, top, right, bottom), os.path.join(DEBUG_DIR, screenshot_name))
    else:
        logging.error(f"识别失败: {image_path}")
        # 保存全屏截图用于调试
        base_name = os.path.basename(image_path)
        file_name, ext = os.path.splitext(base_name)
        if not ext:
            ext = ".png"
        screenshot_name = f"test_fail_{file_name}{ext}"

        # safe_grab((0, 0, pyautogui.size().width, pyautogui.size().height),
        #           os.path.join(DEBUG_DIR, screenshot_name))


def get_mouse_position():
    """获取当前鼠标位置（用于调试）"""
    logging.info("将鼠标移动到目标位置，按Ctrl+C停止...")
    try:
        while True:
            x, y = pyautogui.position()
            print(f"当前坐标: ({x}, {y})", end="\r")
            time.sleep(0.1)
    except KeyboardInterrupt:
        logging.info("\n已停止获取坐标")
        return x, y


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="游戏自动登录脚本")
    parser.add_argument("--debug", action="store_true", help="启用调试模式")
    parser.add_argument("--test", type=str, help="测试特定图像识别")
    parser.add_argument("--position", action="store_true", help="获取鼠标位置")
    args = parser.parse_args()

    # 测试模式
    if args.test:
        image_path = os.path.join(IMAGE_DIR, args.test)
        test_image_recognition(image_path)
        return

    # 获取鼠标位置模式
    if args.position:
        get_mouse_position()
        return

    # 检查账号文件
    if not os.path.exists(ACCOUNTS_FILE):
        logging.error(f"账号文件不存在: {ACCOUNTS_FILE}")
        return

    with open(ACCOUNTS_FILE, "r", encoding="utf-8") as file:
        reader = csv.reader(file)
        accounts = list(reader)

    total = len(accounts)
    logging.info(f"准备登录 {total} 个账号...")

    # 遍历账号列表
    for i, (username, password) in enumerate(accounts, 1):
        logging.info(f"\n===== 开始登录账号 {i}/{total}: {username} =====")

        # 激活游戏窗口（如果已打开）
        # activate_game_window()

        success = login_account(username, password)

        if success and i < total:
            delay = random_delay() * 3
            logging.info(f"等待 {delay:.2f} 秒后登录下一个账号...")
            time.sleep(delay)


if __name__ == "__main__":
    print("脚本将在3秒后开始，请不要操作电脑...")
    time.sleep(3)
    main()
