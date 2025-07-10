import sys  # 系统模块，用于处理命令行参数和程序退出
from PyQt5.QtWidgets import (
    QApplication, QWidget, QHBoxLayout, QVBoxLayout, QGroupBox,
    QLabel, QComboBox, QLineEdit, QListWidget, QPushButton,
    QTextEdit, QCheckBox, QSpinBox, QMessageBox, QSizePolicy
)
from PyQt5.QtCore import Qt, QTimer  # Qt 对齐常量与定时器

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()  
        # 窗口标题和固定大小
        self.setWindowTitle("白梦霸王挂-打玉神器")
        self.setFixedSize(1800, 1000)

        # 主布局：水平分两栏
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # 构建左右面板
        left_panel  = self.build_left_panel()   # 功能区
        right_panel = self.build_right_panel()  # 日志区

        # 添加到布局并按 7:3 的伸缩因子分配空间（≈70%/30%）
        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel)
        main_layout.setStretch(0, 7)
        main_layout.setStretch(1, 3)

        # 定时器：用于循环执行业务逻辑
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.show_selection)

    def build_left_panel(self) -> QWidget:
        """构建左侧功能区：挂机设置 + 锁定反击 + 控制按钮"""
        container = QWidget()
        container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout = QVBoxLayout(container)
        layout.setSpacing(10)

        # === 业务代码开始 ===
        # 挂机设置分组
        hangup_group = QGroupBox("自动挂机设置")
        hangup_group.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        hangup_layout = QVBoxLayout(hangup_group)
        hangup_layout.setSpacing(10)
        self.init_equip_section(hangup_layout)   # 装备
        self.init_potion_section(hangup_layout)  # 药品
        layout.addWidget(hangup_group)

        # 锁定反击分组
        lock_group = QGroupBox("锁定反击")
        lock_layout = QVBoxLayout(lock_group)
        lock_layout.setSpacing(10)
        self.init_force_section(lock_layout)       # 势力多选
        self.init_person_section(lock_layout)      # 自定义人名
        self.init_auto_switch_section(lock_layout) # 自动切换
        layout.addWidget(lock_group)
        # === 业务代码结束 ===

        # 循环控制：间隔 + 开始/停止
        ctrl_layout = QHBoxLayout()
        ctrl_layout.addWidget(QLabel("间隔(s):"))
        self.interval_spin = QSpinBox()               # 用户输入秒数
        self.interval_spin.setRange(1, 3600)
        self.interval_spin.setValue(5)
        ctrl_layout.addWidget(self.interval_spin)

        self.start_btn = QPushButton("开始挂机")
        self.start_btn.clicked.connect(self.start_loop)
        ctrl_layout.addWidget(self.start_btn)

        self.stop_btn = QPushButton("停止挂机")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_loop)
        ctrl_layout.addWidget(self.stop_btn)

        layout.addLayout(ctrl_layout)
        layout.addStretch()
        return container

    def build_right_panel(self) -> QWidget:
        """构建右侧日志区"""
        container = QWidget()
        container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout = QVBoxLayout(container)
        layout.setSpacing(10)

        layout.addWidget(QLabel("运行日志"))
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)

        clear_btn = QPushButton("清空日志")
        clear_btn.clicked.connect(self.log_text.clear)
        layout.addWidget(clear_btn)

        return container

    # === 业务代码开始 ===
    def init_equip_section(self, parent_layout):
        """初始化装备选择区"""
        equip_opts = {
            "镐": ["铁镐", "石刀"], "马": ["上都马"], "盾牌": ["破虏盾"],
            "武器": ["邪瘟砲", "铁甲邪瘟砲"], "头盔": ["铜盔"],
            "衣服": ["水苍文士甲"], "鞋子": ["水苍绑腿"], "护腕": ["水苍护腕"]
        }
        box = QGroupBox("装备")
        layout = QHBoxLayout(box)
        layout.setSpacing(10)
        for name, opts in equip_opts.items():
            col = QVBoxLayout()
            col.addWidget(QLabel(name))
            cb = QComboBox()
            cb.addItems(opts)
            col.addWidget(cb)
            setattr(self, f"equip_cb_{name}", cb)
            layout.addLayout(col)
        parent_layout.addWidget(box)

    def init_potion_section(self, parent_layout):
        """初始化药品选择区"""
        potion_opts = {"红": ["人参王", "人参"], "蓝": ["大还单", "小还丹"]}
        box = QGroupBox("药品")
        layout = QHBoxLayout(box)
        layout.setSpacing(10)
        for name, opts in potion_opts.items():
            col = QVBoxLayout()
            col.addWidget(QLabel(f"{name} 药"))
            cb = QComboBox(); cb.addItems(opts); col.addWidget(cb)
            col.addWidget(QLabel("数量"))
            sb = QSpinBox(); sb.setRange(1, 999); sb.setValue(1); col.addWidget(sb)
            setattr(self, f"potion_cb_{name}", cb)
            setattr(self, f"potion_qty_{name}", sb)
            layout.addLayout(col)
        parent_layout.addWidget(box)

    def init_force_section(self, parent_layout):
        """初始化势力多选区"""
        forces = ["赵", "齐", "秦", "韩", "燕", "魏", "楚"]
        box = QGroupBox("选择势力（多选）")
        layout = QHBoxLayout(box); layout.setSpacing(5)
        self.force_checks = {}
        for f in forces:
            cb = QCheckBox(f); cb.stateChanged.connect(self.on_force_changed)
            self.force_checks[f] = cb; layout.addWidget(cb)
        parent_layout.addWidget(box)

    def init_person_section(self, parent_layout):
        """初始化自定义人名列表"""
        box = QGroupBox("锁定人名")
        vbox = QVBoxLayout(box)
        hl = QHBoxLayout()
        self.entry = QLineEdit(); hl.addWidget(self.entry)
        add_btn = QPushButton("添加"); add_btn.clicked.connect(self.add_person); hl.addWidget(add_btn)
        del_btn = QPushButton("删除选中"); del_btn.clicked.connect(self.del_person); hl.addWidget(del_btn)
        vbox.addLayout(hl)
        self.listbox = QListWidget(); vbox.addWidget(self.listbox)
        parent_layout.addWidget(box)

    def init_auto_switch_section(self, parent_layout):
        """初始化“死亡自动切换坐标”复选框"""
        self.cb_auto = QCheckBox("死亡一次自动切换落点坐标反击")
        parent_layout.addWidget(self.cb_auto)
    # === 业务代码结束 ===

    # === 循环控制 ===
    def start_loop(self):
        """开始定时循环执行业务逻辑"""
        interval_ms = self.interval_spin.value() * 1000
        self.timer.start(interval_ms)
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)

    def stop_loop(self):
        """停止循环"""
        self.timer.stop()
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

    # === 交互与日志 ===
    def on_force_changed(self):
        """切换势力复选时，控制自定义输入区状态"""
        any_checked = any(cb.isChecked() for cb in self.force_checks.values())
        self.entry.setDisabled(any_checked)
        self.listbox.setDisabled(any_checked)
        for btn in self.findChildren(QPushButton):
            if btn.text() in ("添加", "删除选中"):
                btn.setDisabled(any_checked)

    def add_person(self):
        """添加自定义人名"""
        text = self.entry.text().strip()
        if not text:
            QMessageBox.warning(self, "提示", "请输入内容后再添加")
            return
        if any(cb.isChecked() for cb in self.force_checks.values()):
            QMessageBox.warning(self, "提示", "势力已选择，不能添加自定义内容")
            return
        self.listbox.addItem(text)
        self.entry.clear()

    def del_person(self):
        """删除选中人名"""
        row = self.listbox.currentRow()
        if row < 0:
            QMessageBox.information(self, "提示", "请先选择要删除的项")
            return
        self.listbox.takeItem(row)

    def show_selection(self):
        """执行业务逻辑并打印当前配置到日志区"""
        self.log_text.clear()
        def log(m): self.log_text.append(m)

        log("开始运行，挂机设置选择：")
        for name in ["镐","马","盾牌","武器","头盔","衣服","鞋子","护腕"]:
            cb = getattr(self, f"equip_cb_{name}")
            log(f"  装备 {name}: {cb.currentText()}")
        for name in ["红","蓝"]:
            cb  = getattr(self, f"potion_cb_{name}")
            qty = getattr(self, f"potion_qty_{name}").value()
            log(f"  药品 {name}: {cb.currentText()}，数量: {qty}")

        selected = [f for f, cb in self.force_checks.items() if cb.isChecked()]
        log("锁定反击势力选择："); log(f"  {selected if selected else '无'}")

        items = [self.listbox.item(i).text() for i in range(self.listbox.count())]
        log("锁定反击锁定人名列表内容："); log(f"  {items if items else '无'}")

        log("锁定反击切换坐标位反击选择：")
        log(f"  {'已选' if self.cb_auto.isChecked() else '未选'}")
        
        log("准备开始检测！")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
