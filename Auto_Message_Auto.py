import random
import time
import pyautogui
from PyQt5.QtCore import QThread, pyqtSignal
import pyperclip
import sys
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QLineEdit, QGroupBox, QTextEdit, QCheckBox, QApplication)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QPalette


class AutoMessageA(QThread):
    status_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.running = False
        self.messages = ["欢迎使用下北泽虹夏制作的MC工具盒"]
        self.min_interval = 3
        self.max_interval = 5
        self.use_clipboard = True
        self.use_enter_to_send = True
        self.append_random_digits = False

    def run(self):
        while self.running:
            try:
                if self.use_enter_to_send:
                    pyautogui.press('enter')
                    time.sleep(0.3)

                message = random.choice(self.messages)

                # 处理带数字的消息
                if '{num}' in message:
                    num_digits = random.randint(1, 3)
                    digits = ''.join(random.choices('0123456789', k=num_digits))
                    full_message = message.replace('{num}', digits)
                else:
                    full_message = message
                    if self.append_random_digits:
                        num_digits = random.randint(1, 3)
                        digits = ''.join(random.choices('0123456789', k=num_digits))
                        full_message = full_message + digits

                if self.use_clipboard:
                    try:
                        pyperclip.copy(full_message)
                        time.sleep(0.3)
                        pyautogui.hotkey('ctrl', 'v')
                        self.status_signal.emit(f"已发送(剪贴板): {full_message}")
                    except Exception as e:
                        self.status_signal.emit(f"剪贴板错误: {str(e)}")
                        # 尝试直接输入
                        try:
                            pyautogui.write(full_message, interval=0.1)
                            self.status_signal.emit(f"已发送(直接输入): {full_message}")
                        except:
                            self.status_signal.emit("无法发送消息")
                else:
                    pyautogui.write(full_message, interval=0.1)
                    self.status_signal.emit(f"已发送(直接输入): {full_message}")

                if self.use_enter_to_send:
                    time.sleep(0.2)
                    pyautogui.press('enter')

                interval = random.uniform(self.min_interval, self.max_interval)
                time.sleep(interval)

            except Exception as e:
                self.status_signal.emit(f"运行时错误: {str(e)}")
                time.sleep(1)

    def stop(self):
        self.running = False
        self.wait()


class AutoMessageATab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.sender = AutoMessageA()
        self.sender.status_signal.connect(self.update_log)

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)

        title = QLabel("自动消息发送器")
        title.setFont(QFont("Microsoft YaHei", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #3498db;")
        main_layout.addWidget(title)

        # 状态显示
        status_box = QGroupBox("运行状态")
        status_layout = QVBoxLayout()

        self.status_label = QLabel("状态: 未运行")
        self.status_label.setFont(QFont("Microsoft YaHei", 12))
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            background-color: #2c3e50;
            color: #ecf0f1;
            border-radius: 10px;
            padding: 15px;
        """)
        status_layout.addWidget(self.status_label)
        status_box.setLayout(status_layout)
        main_layout.addWidget(status_box)

        # 控制按钮
        control_box = QGroupBox("控制面板")
        control_layout = QHBoxLayout()

        self.start_btn = QPushButton("▶ 开始发送")
        self.start_btn.setFont(QFont("Microsoft YaHei", 12))
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border-radius: 8px;
                padding: 12px 24px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
            QPushButton:disabled {
                background-color: #7f8c8d;
            }
        """)
        self.start_btn.clicked.connect(self.start_sending)

        self.stop_btn = QPushButton("■ 停止发送")
        self.stop_btn.setFont(QFont("Microsoft YaHei", 12))
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border-radius: 8px;
                padding: 12px 24px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:disabled {
                background-color: #7f8c8d;
            }
        """)
        self.stop_btn.clicked.connect(self.stop_sending)
        self.stop_btn.setEnabled(False)

        control_layout.addWidget(self.start_btn)
        control_layout.addWidget(self.stop_btn)
        control_box.setLayout(control_layout)
        main_layout.addWidget(control_box)

        settings_box = QGroupBox("消息设置")
        settings_layout = QVBoxLayout()

        msg_layout = QVBoxLayout()
        self.msg_edit = QTextEdit()
        self.msg_edit.setFont(QFont("Microsoft YaHei", 11))
        self.msg_edit.setPlainText(
            "欢迎使用下北泽虹夏制作的MC工具盒"
        )
        self.msg_edit.setMinimumHeight(120)
        msg_layout.addWidget(self.msg_edit)
        settings_layout.addLayout(msg_layout)
        advanced_layout = QHBoxLayout()

        # 间隔设置
        interval_box = QGroupBox("发送间隔 (秒)")
        interval_layout = QVBoxLayout()

        min_layout = QHBoxLayout()
        min_layout.addWidget(QLabel("最小间隔:"))
        self.min_input = QLineEdit("3")
        self.min_input.setFont(QFont("Microsoft YaHei", 11))
        self.min_input.setMaximumWidth(100)
        min_layout.addWidget(self.min_input)

        max_layout = QHBoxLayout()
        max_layout.addWidget(QLabel("最大间隔:"))
        self.max_input = QLineEdit("5")
        self.max_input.setFont(QFont("Microsoft YaHei", 11))
        self.max_input.setMaximumWidth(100)
        max_layout.addWidget(self.max_input)

        interval_layout.addLayout(min_layout)
        interval_layout.addLayout(max_layout)
        interval_box.setLayout(interval_layout)
        advanced_layout.addWidget(interval_box)

        options_box = QGroupBox("发送选项")
        options_layout = QVBoxLayout()

        self.clipboard_cb = QCheckBox("使用剪贴板发送 (支持中文)")
        self.clipboard_cb.setFont(QFont("Microsoft YaHei", 10))
        self.clipboard_cb.setChecked(True)

        self.enter_cb = QCheckBox("自动按Enter键发送")
        self.enter_cb.setFont(QFont("Microsoft YaHei", 10))
        self.enter_cb.setChecked(True)

        self.append_digits_cb = QCheckBox("每条消息后附加随机数字 (1-3位)")
        self.append_digits_cb.setFont(QFont("Microsoft YaHei", 10))
        self.append_digits_cb.setChecked(False)
        self.append_digits_cb.setToolTip("无论消息是中文、英文还是混合语言，都会在末尾添加随机数字")

        options_layout.addWidget(self.clipboard_cb)
        options_layout.addWidget(self.enter_cb)
        options_layout.addWidget(self.append_digits_cb)
        options_box.setLayout(options_layout)
        advanced_layout.addWidget(options_box)

        settings_layout.addLayout(advanced_layout)
        settings_box.setLayout(settings_layout)
        main_layout.addWidget(settings_box)

        # 日志区域
        log_box = QGroupBox("发送日志")
        log_layout = QVBoxLayout()

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Microsoft YaHei", 10))
        self.log_text.setMinimumHeight(150)

        palette = self.log_text.palette()
        palette.setColor(QPalette.Base, QColor("#2c3e50"))
        palette.setColor(QPalette.Text, QColor("#ecf0f1"))
        self.log_text.setPalette(palette)

        log_layout.addWidget(self.log_text)
        log_box.setLayout(log_layout)
        main_layout.addWidget(log_box)

        self.setLayout(main_layout)
        self.setWindowTitle("自动消息发送器")
        self.setMinimumSize(700, 800)

    def start_sending(self):
        try:
            self.sender.messages = self.msg_edit.toPlainText().split('\n')
            self.sender.min_interval = float(self.min_input.text())
            self.sender.max_interval = float(self.max_input.text())
            self.sender.use_clipboard = self.clipboard_cb.isChecked()
            self.sender.use_enter_to_send = self.enter_cb.isChecked()
            self.sender.append_random_digits = self.append_digits_cb.isChecked()  # 设置新选项

            self.sender.running = True
            self.sender.start()

            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.status_label.setText("状态: 运行中")
            self.status_label.setStyleSheet("""
                background-color: #2c3e50;
                color: #2ecc71;
                border-radius: 10px;
                padding: 15px;
            """)
            self.log_text.append("自动消息发送已启动...")
        except Exception as e:
            self.log_text.append(f"启动失败: {str(e)}")

    def stop_sending(self):
        self.sender.running = False
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.status_label.setText("状态: 已停止")
        self.status_label.setStyleSheet("""
            background-color: #2c3e50;
            color: #e74c3c;
            border-radius: 10px;
            padding: 15px;
        """)
        self.log_text.append("自动消息发送已停止")

    def update_log(self, msg):
        if "错误" in msg:
            self.log_text.append(f'<span style="color:#e74c3c;">{msg}</span>')
        elif "发送" in msg:
            self.log_text.append(f'<span style="color:#2ecc71;">{msg}</span>')
        else:
            self.log_text.append(msg)

