import threading
import random
import time
from pynput import mouse
from PyQt5.QtCore import QThread, pyqtSignal
from pynput.mouse import Button
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QGroupBox, QFrame, QComboBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIntValidator
from Constant import mouse_controller

class PhantomClicker(QThread):
    status_signal = pyqtSignal(str, bool)

    def __init__(self):
        super().__init__()
        self.right_trigger = Button.x1
        self.left_trigger = Button.x2

        self.left_clicking = False
        self.right_clicking = False
        self.left_min_interval = 45
        self.left_max_interval = 50
        self.right_min_interval = 45
        self.right_max_interval = 50

    def run(self):
        self.listener = mouse.Listener(on_click=self.on_click)
        self.listener.start()
        self.listener.join()

    def on_click(self, x, y, button, pressed):
        try:
            # 改成动态 trigger 判断
            if button == self.right_trigger:
                if pressed and not self.right_clicking:
                    self.right_clicking = True
                    threading.Thread(target=self.right_click_loop).start()
                    self.status_signal.emit("right", True)
                elif not pressed:
                    self.right_clicking = False
                    self.status_signal.emit("right", False)

            elif button == self.left_trigger:
                if pressed and not self.left_clicking:
                    self.left_clicking = True
                    threading.Thread(target=self.left_click_loop).start()
                    self.status_signal.emit("left", True)
                elif not pressed:
                    self.left_clicking = False
                    self.status_signal.emit("left", False)
        except Exception as e:
            print(f"发生错误: {e}")

    def right_click_loop(self):
        while self.right_clicking:
            mouse_controller.click(Button.right)
            time.sleep(random.randint(self.right_min_interval, self.right_max_interval) / 1000)

    def left_click_loop(self):
        while self.left_clicking:
            mouse_controller.click(Button.left)
            time.sleep(random.randint(self.left_min_interval, self.left_max_interval) / 1000)


# ======================== 自动点击标签页 ========================
class PhantomClickTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.clicker = PhantomClicker()
        self.clicker.status_signal.connect(self.update_status)
        self.clicker.start()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        title = QLabel("鼠标自动连点器")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # 状态指示灯
        self.status_frame = QFrame()
        self.status_frame.setFixedHeight(150)
        status_layout = QHBoxLayout(self.status_frame)

        self.left_status = QLabel("左键状态: 停止")
        self.left_status.setFont(QFont("Arial", 14))
        self.left_status.setAlignment(Qt.AlignCenter)
        self.left_status.setStyleSheet("""
            background-color: #e74c3c;
            color: white;
            border-radius: 10px;
            padding: 20px;
        """)

        self.right_status = QLabel("右键状态: 停止")
        self.right_status.setFont(QFont("Arial", 14))
        self.right_status.setAlignment(Qt.AlignCenter)
        self.right_status.setStyleSheet("""
            background-color: #e74c3c;
            color: white;
            border-radius: 10px;
            padding: 20px;
        """)

        status_layout.addWidget(self.left_status)
        status_layout.addWidget(self.right_status)
        layout.addWidget(self.status_frame)

        trigger_group = QGroupBox("触发按键设置")
        tg_layout = QHBoxLayout()
        tg_layout.addWidget(QLabel("左键连点触发键:"))
        self.left_trigger_combo = QComboBox()
        self.left_trigger_combo.addItems(["侧边前键","侧边后键" , "鼠标左键", "鼠标右键", "鼠标中键"])
        self.left_trigger_combo.currentTextChanged.connect(self.on_left_trigger_changed)
        tg_layout.addWidget(self.left_trigger_combo)

        tg_layout.addWidget(QLabel("右键连点触发键:"))
        self.right_trigger_combo = QComboBox()
        self.right_trigger_combo.addItems(["侧边后键", "侧边前键", "鼠标左键", "鼠标右键", "鼠标中键"])
        self.right_trigger_combo.currentTextChanged.connect(self.on_right_trigger_changed)
        tg_layout.addWidget(self.right_trigger_combo)

        trigger_group.setLayout(tg_layout)
        layout.addWidget(trigger_group)

        control_group = QGroupBox("点击间隔设置 (毫秒)")
        control_layout = QHBoxLayout()

        # 左键设置
        left_group = QGroupBox("左键设置")
        left_layout = QVBoxLayout()

        min_layout = QHBoxLayout()
        min_layout.addWidget(QLabel("最小间隔:"))
        self.left_min_input = QLineEdit("45")
        self.left_min_input.setFont(QFont("Arial", 12))
        self.left_min_input.setValidator(QIntValidator(10, 500, self))
        self.left_min_input.textChanged.connect(self.update_left_min)
        min_layout.addWidget(self.left_min_input)

        max_layout = QHBoxLayout()
        max_layout.addWidget(QLabel("最大间隔:"))
        self.left_max_input = QLineEdit("50")
        self.left_max_input.setFont(QFont("Arial", 12))
        self.left_max_input.setValidator(QIntValidator(10, 500, self))
        self.left_max_input.textChanged.connect(self.update_left_max)
        max_layout.addWidget(self.left_max_input)

        left_layout.addLayout(min_layout)
        left_layout.addLayout(max_layout)
        left_group.setLayout(left_layout)

        # 右键设置
        right_group = QGroupBox("右键设置")
        right_layout = QVBoxLayout()

        min_layout = QHBoxLayout()
        min_layout.addWidget(QLabel("最小间隔:"))
        self.right_min_input = QLineEdit("45")
        self.right_min_input.setFont(QFont("Arial", 12))
        self.right_min_input.setValidator(QIntValidator(10, 500, self))
        self.right_min_input.textChanged.connect(self.update_right_min)
        min_layout.addWidget(self.right_min_input)

        max_layout = QHBoxLayout()
        max_layout.addWidget(QLabel("最大间隔:"))
        self.right_max_input = QLineEdit("50")
        self.right_max_input.setFont(QFont("Arial", 12))
        self.right_max_input.setValidator(QIntValidator(10, 500, self))
        self.right_max_input.textChanged.connect(self.update_right_max)
        max_layout.addWidget(self.right_max_input)

        right_layout.addLayout(min_layout)
        right_layout.addLayout(max_layout)
        right_group.setLayout(right_layout)

        control_layout.addWidget(left_group)
        control_layout.addWidget(right_group)
        control_group.setLayout(control_layout)
        layout.addWidget(control_group)

        # 说明部分的代码
        help_group = QGroupBox("说明")
        help_layout = QVBoxLayout()
        help_label = QLabel("1. 该功能可以让CPS浮动而非稳定在某个值\n2. 间隔时间越高说明时间越长说明CPS越低\n3. 45-50延迟左右按满大概就是20CPS\n4.之所以叫这个名字是因为我觉得和自动点击不同, 而是按下鼠标侧键可以让鼠标左键或者右键多次点击, 类似于模拟DC点击")
        help_label.setFont(QFont("Arial", 10))
        help_layout.addWidget(help_label)
        help_group.setLayout(help_layout)
        layout.addWidget(help_group)

        self.setLayout(layout)

    def on_left_trigger_changed(self, txt):
        mapping = {
            "侧边前键": Button.x2,"侧边后键": Button.x1,
            "鼠标左键": Button.left, "鼠标右键": Button.right,
            "鼠标中键": Button.middle
        }
        self.clicker.left_trigger = mapping[txt]

    def on_right_trigger_changed(self, txt):
        mapping = {
            "侧边后键": Button.x1, "侧边前键": Button.x2,
            "鼠标左键": Button.left, "鼠标右键": Button.right,
            "鼠标中键": Button.middle
        }
        self.clicker.right_trigger = mapping[txt]

    def update_status(self, btn_type, active):
        if btn_type == "left":
            text = "左键状态: 运行中" if active else "左键状态: 停止"
            color = "#2ecc71" if active else "#e74c3c"
            self.left_status.setText(text)
            self.left_status.setStyleSheet(f"""
                background-color: {color};
                color: white;
                border-radius: 10px;
                padding: 20px;
            """)
        else:
            text = "右键状态: 运行中" if active else "右键状态: 停止"
            color = "#2ecc71" if active else "#e74c3c"
            self.right_status.setText(text)
            self.right_status.setStyleSheet(f"""
                background-color: {color};
                color: white;
                border-radius: 10px;
                padding: 20px;
            """)

    def update_left_min(self, value):
        if value:
            try:
                self.clicker.left_min_interval = int(value)
            except ValueError:
                pass

    def update_left_max(self, value):
        if value:
            try:
                self.clicker.left_max_interval = int(value)
            except ValueError:
                pass

    def update_right_min(self, value):
        if value:
            try:
                self.clicker.right_min_interval = int(value)
            except ValueError:
                pass

    def update_right_max(self, value):
        if value:
            try:
                self.clicker.right_max_interval = int(value)
            except ValueError:
                pass

