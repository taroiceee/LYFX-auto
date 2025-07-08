import pygetwindow as gw


def print_all_window_titles():
    """获取并打印当前所有可见窗口的标题"""
    # 获取所有可见窗口
    windows = gw.getAllWindows()

    print("当前打开的窗口有：")
    for window in windows:
        # 只打印有标题且可见的窗口
        if window.title and window.visible:
            print(window.title)


if __name__ == "__main__":
    print_all_window_titles()
