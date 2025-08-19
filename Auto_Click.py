import keyboard
from PyQt5.QtCore import pyqtSignal, QThread
from pynput.mouse import Button
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QLineEdit, QGroupBox, QTextEdit, QFrame, QGridLayout,
                             QComboBox, QButtonGroup, QRadioButton)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIntValidator
from Constant import mouse_controller

class AutoClicker(QThread):
    status_signal = pyqtSignal(str)
    log_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.running = False
        self.clicking = False
        self.trigger_key = "f6"
        self.button = "left"
        self.cps = 10
        self.click_interval = 0.1

    def run(self):
        self.running = True
        self.log_signal.emit("连点器已启动")
        self.log_signal.emit(f"按 {self.trigger_key.upper()} 键开始/停止自动点击")

        # 注册热键
        keyboard.add_hotkey(self.trigger_key, self.toggle_clicking)

        while self.running:
            if self.clicking:
                if self.button == "left":
                    mouse_controller.click(Button.left)
                else:
                    mouse_controller.click(Button.right)

                QThread.msleep(int(self.click_interval * 1000))

        keyboard.remove_hotkey(self.trigger_key)
        self.log_signal.emit("连点器已停止")

    def toggle_clicking(self):
        self.clicking = not self.clicking
        status = "运行中" if self.clicking else "已停止"
        self.status_signal.emit(status)
        self.log_signal.emit(f"自动点击已{status}")

    def stop(self):
        self.running = False
        self.clicking = False


# ==================连点器======================

class AutoClickerTab(QWidget):
    def __init__(self):
        super().__init__()
        self.auto_clicker = AutoClicker()
        self.auto_clicker.status_signal.connect(self.update_status)
        self.auto_clicker.log_signal.connect(self.update_log)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        title = QLabel("鼠标连点器")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # 状态显示
        self.status_frame = QFrame()
        self.status_frame.setFixedHeight(100)
        status_layout = QHBoxLayout(self.status_frame)

        self.status_label = QLabel("状态: 未启动")
        self.status_label.setFont(QFont("Arial", 14))
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            background-color: #e74c3c;
            color: white;
            border-radius: 10px;
            padding: 20px;
        """)

        status_layout.addWidget(self.status_label)
        layout.addWidget(self.status_frame)

        # 控制按钮
        btn_layout = QHBoxLayout()

        self.start_btn = QPushButton("启动连点器")
        self.start_btn.setFont(QFont("Arial", 12))
        self.start_btn.clicked.connect(self.start_clicker)

        self.stop_btn = QPushButton("停止连点器")
        self.stop_btn.setFont(QFont("Arial", 12))
        self.stop_btn.clicked.connect(self.stop_clicker)
        self.stop_btn.setEnabled(False)

        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.stop_btn)
        layout.addLayout(btn_layout)

        # 设置面板
        settings_group = QGroupBox("连点器设置")
        settings_layout = QGridLayout()

        # 触发键设置
        settings_layout.addWidget(QLabel("触发按键:"), 0, 0)
        self.trigger_combo = QComboBox()
        self.trigger_combo.addItems(["f6", "f7", "f8", "f9", "f10", "f11", "f12", "insert", "delete", "home", "end"])
        self.trigger_combo.currentTextChanged.connect(self.update_trigger_key)
        settings_layout.addWidget(self.trigger_combo, 0, 1)

        # 点击按钮选择
        settings_layout.addWidget(QLabel("点击按钮:"), 1, 0)
        self.button_group = QButtonGroup(self)

        self.left_radio = QRadioButton("左键")
        self.left_radio.setChecked(True)
        self.button_group.addButton(self.left_radio)
        settings_layout.addWidget(self.left_radio, 1, 1)

        self.right_radio = QRadioButton("右键")
        self.button_group.addButton(self.right_radio)
        settings_layout.addWidget(self.right_radio, 1, 2)

        self.button_group.buttonClicked.connect(self.update_click_button)

        # CPS设置
        settings_layout.addWidget(QLabel("点击速度 (CPS):"), 2, 0)
        self.cps_slider = QLineEdit("10")
        self.cps_slider.setValidator(QIntValidator(1, 50, self))
        self.cps_slider.textChanged.connect(self.update_cps)
        settings_layout.addWidget(self.cps_slider, 2, 1)
        settings_layout.addWidget(QLabel("次/秒"), 2, 2)

        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)

        # 日志区域
        log_group = QGroupBox("运行日志")
        log_layout = QVBoxLayout()

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Arial", 10))
        log_layout.addWidget(self.log_text)

        log_group.setLayout(log_layout)
        layout.addWidget(log_group)

        self.setLayout(layout)

    def start_clicker(self):
        self.auto_clicker.start()
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.status_label.setText("状态: 运行中")
        self.status_label.setStyleSheet("""
            background-color: #34495e;
            color: #3498db;
            border-radius: 10px;
            padding: 20px;
        """)
        self.log_text.append("连点器已启动，等待触发...")

    def stop_clicker(self):
        self.auto_clicker.stop()
        self.auto_clicker.wait(1)
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.status_label.setText("状态: 未启动")
        self.status_label.setStyleSheet("""
            background-color: #e74c3c;
            color: white;
            border-radius: 10px;
            padding: 20px;
        """)
        self.log_text.append("连点器已停止")

    def update_status(self, status):
        self.status_label.setText(f"状态: {status}")
        if status == "运行中":
            self.status_label.setStyleSheet("""
                background-color: #2ecc71;
                color: white;
                border-radius: 10px;
                padding: 20px;
            """)
        else:
            self.status_label.setStyleSheet("""
                background-color: #34495e;
                color: #3498db;
                border-radius: 10px;
                padding: 20px;
            """)

    def update_log(self, msg):
        self.log_text.append(msg)

    def update_trigger_key(self, key):
        self.auto_clicker.trigger_key = key.lower()
        self.log_text.append(f"触发键已设置为: {key.upper()}")

    def update_click_button(self):
        if self.left_radio.isChecked():
            self.auto_clicker.button = "left"
            self.log_text.append("已设置为左键点击")
        else:
            self.auto_clicker.button = "right"
            self.log_text.append("已设置为右键点击")

    def update_cps(self, cps):
        if cps:
            try:
                cps_value = int(cps)
                if 1 <= cps_value <= 99:
                    self.auto_clicker.cps = cps_value
                    self.auto_clicker.click_interval = 1.0 / cps_value
                    self.log_text.append(f"点击速度已设置为: {cps_value} CPS")
                else:
                    self.log_text.append("CPS值必须在1-99之间")
            except ValueError:
                pass