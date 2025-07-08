# 管理员权限检测
import ctypes
import sys
import os


def is_admin():
    """
    判断当前脚本是否以管理员权限运行
    返回 True 表示是管理员权限，False 表示不是
    """
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def run_as_admin():
    """
    以管理员权限重新启动当前脚本
    """
    params = " ".join([f'"{arg}"' for arg in sys.argv])
    # 使用ShellExecuteEx启动管理员权限的进程
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)


if __name__ == "__main__":
    if not is_admin():
        print("当前脚本未以管理员权限运行，正在尝试以管理员权限重新启动...")
        run_as_admin()
        sys.exit(0)
    else:
        print("当前脚本已以管理员权限运行。")
        # 这里写你的主程序逻辑
        # 例如测试SetCursorPos
        import time

        time.sleep(3)
        ctypes.windll.user32.SetCursorPos(500, 300)
        print("鼠标已移动到 (500, 300)")
