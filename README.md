一.项目结构
GAMEAUTO
├── code  (脚本)
│   ├── __init__.py  (表明当前是一个包,用于包之间的导入调用,勿删)
│   └── auto_login.py  (自动登录脚本)
├── app
│   ├── __init__.py
│   ├── home.py  (程序主页面)
│   └── pages  (程序子页面)
│       ├── __init__.py
│       └── autoLogin.py  (自动登录页面)



二.终端命令

1.切换虚拟环境
venv\Scripts\Activate.ps1

2.执行单个脚本
python code/auto_login.py   

3.运行单个页面
python -m app.pages.autoLogin


4.查看ttkbootstrap主题
python -m ttkbootstrap


