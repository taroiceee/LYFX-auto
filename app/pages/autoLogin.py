import tkinter as tk
from threading import Thread
from code.auto_login import main  # 导入main函数

root = tk.Tk()
root.title("账号执行工具")

# 输入区域
input_frame = tk.Frame(root)
input_frame.grid(row=0, column=0, columnspan=3, padx=5, pady=5, sticky=tk.W)

input_label = tk.Label(input_frame, text="账号+密码输入区", justify=tk.LEFT)
input_label.pack(anchor=tk.W)

input_text = tk.Text(input_frame, height=5, width=50)
input_text.pack()

# 提示语处理
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

# 执行日志区
log_label = tk.Label(root, text="执行日志")
log_label.grid(row=2, column=0, padx=5, sticky=tk.W)

log_text = tk.Text(root, height=8, width=30)
log_text.grid(row=3, column=0, padx=5, pady=5, rowspan=2)

# 进度与失败区
progress_label = tk.Label(root, text="执行进度：100%")
progress_label.grid(row=2, column=1, padx=5, sticky=tk.W)

fail_label = tk.Label(root, text="失败账号")
fail_label.grid(row=2, column=2, padx=5, sticky=tk.W)

copy_btn = tk.Button(root, text="复制文本", width=8)
copy_btn.grid(row=3, column=2, padx=5, sticky=tk.W)

fail_text = tk.Text(root, height=8, width=30)
fail_text.grid(row=4, column=2, padx=5, pady=5)

note_label = tk.Label(root, text="后粘贴至上方重新执行")
note_label.grid(row=5, column=2, padx=5, sticky=tk.W)


# 操作按钮
def run_main_thread():
    def task():
        log_text.insert(tk.END, "开始执行main...\n")
        log_text.see(tk.END)
        try:
            result = main()
            if result:
                log_text.insert(tk.END, "main执行完成，成功！\n")
            else:
                log_text.insert(tk.END, "main执行失败！\n")
        except Exception as e:
            log_text.insert(tk.END, f"执行出错: {e}\n")
        log_text.see(tk.END)

    Thread(target=task, daemon=True).start()


start_btn = tk.Button(root, text="开始执行", width=10, command=run_main_thread)
start_btn.grid(row=1, column=0, padx=5, pady=5)

pause_btn = tk.Button(root, text="暂停", width=10)
pause_btn.grid(row=1, column=1, padx=5, pady=5)

stop_btn = tk.Button(root, text="终止", width=10)
stop_btn.grid(row=1, column=2, padx=5, pady=5)

root.mainloop()
