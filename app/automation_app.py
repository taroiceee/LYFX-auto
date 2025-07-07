import subprocess
import sys
import tkinter as tk
from tkinter import messagebox, ttk
from pathlib import Path
import threading


class ScriptRunnerApp:
    def __init__(self, root):
        self.root = root
        self.process = None
        self.is_running = False

        # 设置中文字体支持
        self.root.option_add("*Font", "SimHei 10")
        self.root.title("自动化脚本运行器")
        self.root.geometry("600x400")
        self.root.resizable(True, True)

        self.script_path = "your_script.py"  # 替换为你的脚本路径

        self.create_widgets()

    def create_widgets(self):
        # 创建顶部控制区域
        control_frame = ttk.Frame(self.root, padding=10)
        control_frame.pack(fill=tk.X)

        self.run_button = ttk.Button(
            control_frame, text="开始运行", command=self.toggle_script, width=15
        )
        self.run_button.pack(side=tk.LEFT, padx=(0, 10))

        self.status_var = tk.StringVar(value="就绪")
        status_label = ttk.Label(control_frame, textvariable=self.status_var)
        status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # 创建输出区域
        output_frame = ttk.Frame(self.root, padding=10)
        output_frame.pack(fill=tk.BOTH, expand=True)

        self.output_text = tk.Text(output_frame, wrap=tk.WORD, state=tk.DISABLED)
        self.output_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(output_frame, command=self.output_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.output_text.config(yscrollcommand=scrollbar.set)

    def toggle_script(self):
        if not self.is_running:
            self.start_script()
        else:
            self.stop_script()

    def start_script(self):
        if not Path(self.script_path).exists():
            messagebox.showerror("错误", f"脚本文件不存在: {self.script_path}")
            return

        self.is_running = True
        self.run_button.config(text="停止运行")
        self.status_var.set("运行中...")
        self.clear_output()

        # 在新线程中运行脚本
        threading.Thread(target=self.run_script, daemon=True).start()

    def run_script(self):
        try:
            self.process = subprocess.Popen(
                [sys.executable, self.script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1,
            )

            # 实时读取输出
            for line in iter(self.process.stdout.readline, ""):
                self.append_output(line)

            self.process.wait()
            return_code = self.process.returncode

            if self.is_running:  # 确保不是被手动停止的
                self.append_output(f"\n脚本已完成，返回代码: {return_code}")
                self.status_var.set(f"已完成，返回代码: {return_code}")
        except Exception as e:
            self.append_output(f"\n错误: {str(e)}")
            self.status_var.set("运行错误")
        finally:
            self.is_running = False
            self.run_button.config(text="开始运行")
            self.process = None

    def stop_script(self):
        if self.process:
            self.append_output("\n正在停止脚本...")
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
                self.append_output(f"\n脚本已停止，返回代码: {self.process.returncode}")
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.append_output("\n脚本已强制终止")

        self.is_running = False
        self.run_button.config(text="开始运行")
        self.status_var.set("已停止")

    def append_output(self, text):
        self.root.after(0, lambda: self._append_output(text))

    def _append_output(self, text):
        self.output_text.config(state=tk.NORMAL)
        self.output_text.insert(tk.END, text)
        self.output_text.see(tk.END)
        self.output_text.config(state=tk.DISABLED)

    def clear_output(self):
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state=tk.DISABLED)


def main():
    root = tk.Tk()
    app = ScriptRunnerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
