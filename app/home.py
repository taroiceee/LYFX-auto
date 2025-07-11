import tkinter as tk
from tkinter import messagebox

root = tk.Tk()
root.title("游戏自动程序")
root.geometry("500x400")

label_title = tk.Label(
    root, text="欢迎使用游戏自动程序", font=("微软雅黑", 18), fg="blue"
)
label_title.pack(pady=20)

label_account = tk.Label(root, text="请输入账号：")
label_account.pack()

entry_account = tk.Entry(root, width=30)
entry_account.pack(pady=5)

label_password = tk.Label(root, text="请输入密码：")
label_password.pack()

entry_password = tk.Entry(root, width=30, show="*")
entry_password.pack(pady=5)

remember_var = tk.IntVar()
check_remember = tk.Checkbutton(root, text="记住密码", variable=remember_var)
check_remember.pack(pady=5)


def on_start():
    account = entry_account.get()
    password = entry_password.get()
    remember = remember_var.get()
    messagebox.showinfo(
        "提示", f"账号：{account}\n密码：{'*' * len(password)}\n记住密码：{remember}"
    )


btn_start = tk.Button(
    root, text="登录", command=on_start, bg="green", fg="white", width=20
)
btn_start.pack(pady=20)

root.mainloop()
