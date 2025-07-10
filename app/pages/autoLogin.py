import ttkbootstrap as ttkb
from threading import Thread, Event
from code.auto_login import main, pause_event, stop_flag  # 导入main函数和控制变量
import tkinter as tk

# 自带主题样式
# 查看ttkbootstrap主题
# python -m ttkbootstrap
root = ttkb.Window(themename="morph")
root.title("账号执行工具")

# 输入账号密码区域
input_frame = ttkb.Frame(root)
input_frame.grid(row=0, column=0, columnspan=6, padx=5, pady=5, sticky="ew")

input_label = ttkb.Label(input_frame, text="账号+密码输入区", justify="left")
input_label.grid(row=0, column=0, sticky="w")

input_text = tk.Text(input_frame, height=5)
input_text.grid(row=1, column=0, sticky="nsew")

# 让input_frame的第0列扩展，input_text宽度自适应
input_frame.columnconfigure(0, weight=1)
input_frame.rowconfigure(1, weight=1)

placeholder_text = (
    "在此输入所有账号+密码,每组账号以分号分开,示例:\naa+123;bbb+666;ccc+000"
)
input_text.insert(tk.END, placeholder_text)
input_text.configure(fg="grey")


def on_input(event):
    if input_text.get("1.0", tk.END).strip() == placeholder_text:
        input_text.delete("1.0", tk.END)
        input_text.configure(fg="black")


def on_focusout(event):
    if not input_text.get("1.0", tk.END).strip():
        input_text.insert(tk.END, placeholder_text)
        input_text.configure(fg="grey")


input_text.bind("<FocusIn>", on_input)
input_text.bind("<FocusOut>", on_focusout)

# 创建日志和失败区的容器框架，方便布局
log_fail_frame = ttkb.Frame(root)
log_fail_frame.grid(row=2, column=0, columnspan=6, padx=5, pady=5, sticky="ew")

# 第一行标签区域，5个标签放在同一行
log_label = ttkb.Label(log_fail_frame, text="执行日志", font=("微软雅黑", 10, "bold"))
log_label.grid(row=0, column=0, padx=(0, 10), sticky="w")

progress_label = ttkb.Label(
    log_fail_frame, text="执行进度：100%", font=("微软雅黑", 10, "bold")
)
progress_label.grid(row=0, column=1, padx=(0, 10), sticky="w")

fail_label = ttkb.Label(log_fail_frame, text="失败账号", font=("微软雅黑", 10, "bold"))
fail_label.grid(row=0, column=2, padx=(20, 0), sticky="w")

copy_btn = ttkb.Button(
    log_fail_frame, text="复制文本", width=8, style="Outline.TButton"
)
copy_btn.grid(row=0, column=3, padx=(0, 0))

note_label = ttkb.Label(
    log_fail_frame, text="后粘贴至上方重新执行", font=("微软雅黑", 9)
)
note_label.grid(row=0, column=4, padx=(0, 10), sticky="w")

# 第二行文本框区域，日志区和失败区并排
log_text = tk.Text(
    log_fail_frame,
    height=8,
    width=50,
    bg="#f0f0f0",
    fg="#333333",
    relief="sunken",
    bd=2,
)
log_text.grid(row=1, column=0, columnspan=2, padx=(0, 10), pady=5, sticky="nsew")

fail_text = tk.Text(
    log_fail_frame,
    height=8,
    width=50,
    bg="#fff0f0",
    fg="#a00000",
    relief="sunken",
    bd=2,
)
fail_text.grid(row=1, column=2, columnspan=3, padx=(10, 0), pady=5, sticky="nsew")

# 让文本框区域横向扩展
for i in range(5):
    log_fail_frame.columnconfigure(i, weight=1)
log_fail_frame.rowconfigure(1, weight=1)

# 全局变量记录暂停状态
is_paused = False


# 操作按钮
def run_main_thread():
    def task():
        log_text.insert(tk.END, "开始执行main...\n")
        log_text.see(tk.END)
        try:
            # 重置控制变量
            pause_event.clear()
            stop_flag.clear()

            result = main()
            if result:
                log_text.insert(tk.END, "main执行完成，成功！\n")
            else:
                log_text.insert(tk.END, "main执行失败！\n")
        except Exception as e:
            log_text.insert(tk.END, f"执行出错: {e}\n")
        log_text.see(tk.END)

    Thread(target=task, daemon=True).start()


# 暂停按钮回调
def pause_execution():
    if pause_event.is_set():
        pause_event.clear()
        log_text.insert(tk.END, "继续执行...\n")
        pause_btn.configure(text="暂停")
    else:
        pause_event.set()
        log_text.insert(tk.END, "已暂停执行...\n")
        pause_btn.configure(text="继续")
    log_text.see(tk.END)


def toggle_pause():
    global is_paused
    from code.auto_login import pause_event  # 导入auto_login中的pause_event

    if is_paused:
        # 当前是暂停状态，恢复执行
        pause_event.clear()  # 清除暂停信号
        is_paused = False
        pause_btn.configure(text="暂停")  # 更新按钮文本
        log_text.insert(tk.END, "已恢复执行...\n")
    else:
        # 当前是运行状态，暂停执行
        pause_event.set()  # 设置暂停信号
        is_paused = True
        pause_btn.configure(text="继续")  # 更新按钮文本
        log_text.insert(tk.END, "已暂停执行...\n")
    log_text.see(tk.END)


# 终止按钮回调
def stop_execution():
    stop_flag.set()
    # 如果处于暂停状态，先恢复执行以便线程能检测到终止信号
    if pause_event.is_set():
        pause_event.clear()
    log_text.insert(tk.END, "正在终止执行...\n")
    log_text.see(tk.END)


# 创建按钮容器框架，放在root的第1行第0列，跨6列，居中显示
button_frame = ttkb.Frame(root)
button_frame.grid(row=1, column=0, columnspan=6, pady=5)

# 在button_frame里放置三个按钮，使用grid布局
start_btn = ttkb.Button(
    button_frame, text="开始执行", width=10, command=run_main_thread
)
# 修改暂停按钮的command绑定
pause_btn = ttkb.Button(
    button_frame, text="暂停", width=10, style="Outline.TButton", command=toggle_pause
)
stop_btn = ttkb.Button(
    button_frame, text="终止", width=10, style="Outline.TButton", command=stop_execution
)

start_btn.grid(row=0, column=0, padx=10)
pause_btn.grid(row=0, column=1, padx=10)
stop_btn.grid(row=0, column=2, padx=10)

# 让button_frame水平居中
button_frame.columnconfigure((0, 1, 2), weight=1)

# 让root窗口的列0扩展，保证整体布局自适应
root.columnconfigure(0, weight=1)
root.rowconfigure(2, weight=1)

root.mainloop()
