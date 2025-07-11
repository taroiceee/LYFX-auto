# data/__init__.py
import os

# 获取项目根目录
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 定义accounts.csv的路径
ACCOUNTS_CSV_PATH = os.path.join(ROOT_DIR, "data", "accounts.csv")
