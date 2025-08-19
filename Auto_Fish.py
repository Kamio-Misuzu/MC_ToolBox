import time
import cv2
import pyautogui
import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import ( QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QLineEdit, QGroupBox, QTextEdit, QGridLayout, QFileDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class AutoFish(QThread):
    status_signal = pyqtSignal(str)
    region_selected = pyqtSignal(tuple)

    def __init__(self):
        super().__init__()
        self.running = False
        self.vari_list = [0.51, 0, 0, 0, 0]  # [阈值, x, y, w, h]
        self.template_path = ''
        self.selected_region = None
        self.region_selector = None
        self.last_match_time = time.time()
        self.no_match_start_time = time.time()
        self.match_count = 0
        self.match_times = []
        self.successful_scale = None

    def run(self):
        self.start_time = time.time()

        while self.running:
            try:
                if self.selected_region and all(self.selected_region):
                    # 调用多尺度模板匹配函数
                    if self.multi_scale_template_matching():
                        self.match_count += 1
                        current_time = time.time()
                        match_interval = current_time - self.last_match_time
                        self.match_times.append(match_interval)
                        self.last_match_time = current_time
                        self.no_match_start_time = current_time  # 重置未匹配成功的起始时间

                        pyautogui.click(button='right')
                        time.sleep(1)
                        pyautogui.click(button='right')
                        time.sleep(3)
                    else:
                        # 检查连续未匹配成功的时间
                        current_time = time.time()

                        if current_time - self.no_match_start_time >= 40:
                            self.status_signal.emit("40秒未匹配成功，尝试回到游戏并点击右键")
                            pyautogui.press('tab')
                            time.sleep(0.5)
                            pyautogui.press('enter')
                            time.sleep(0.5)
                            pyautogui.click(button='right')
                            self.no_match_start_time = current_time

                time.sleep(0.4)
            except Exception as e:
                self.status_signal.emit(f"错误: {str(e)}")
                time.sleep(1)

    def format_time(self, seconds):
        minutes, seconds = divmod(seconds, 60)
        return f"{int(minutes)}m {seconds:.3f}s"

    def multi_scale_template_matching(self):
        template = cv2.imread(self.template_path, 0)
        if template is None:
            self.status_signal.emit(f"无法读取模板图像: {self.template_path}")
            return False

        # 截取用户选择的屏幕区域
        x, y, w, h = self.selected_region
        screenshot = pyautogui.screenshot(region=(x, y, w, h))
        screenshot_gray = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)

        # 用于记录最佳匹配的结果
        best_match = None
        max_val = 0

        # 在多个尺度上运行模板匹配
        if self.successful_scale is not None:
            # 如果之前有成功的尺度，那么只在这个尺度的附近进行匹配
            min_scale = max(0.7, self.successful_scale * 0.9)
            max_scale = min(2, self.successful_scale * 1.1)
            scales = np.linspace(min_scale, max_scale, 20)[::-1]
        else:
            scales = np.linspace(0.7, 2, 50)[::-1]

        for scale in scales:
            # 缩放模板图像
            resized_template = cv2.resize(template, (0, 0), fx=scale, fy=scale)
            resized_height, resized_width = resized_template.shape[:2]

            # 确保缩放后的模板不大于截图区域
            if resized_height > h or resized_width > w:
                continue

            # 模板匹配
            res = cv2.matchTemplate(screenshot_gray, resized_template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val_temp, min_loc, max_loc = cv2.minMaxLoc(res)

            # 如果当前匹配结果更好，则更新最佳匹配结果
            if max_val_temp > max_val:
                max_val = max_val_temp
                best_match = max_loc, scale

        # 检查是否找到足够好的匹配结果
        if best_match and max_val > self.vari_list[0]:
            max_loc, scale = best_match
            self.successful_scale = scale  # 保存成功的尺度
            current_time = time.time()
            elapsed_time = current_time - self.start_time
            formatted_time = self.format_time(elapsed_time)

            # 计算匹配统计信息
            min_time = min(self.match_times) if self.match_times else 0
            max_time = max(self.match_times) if self.match_times else 0
            avg_time = sum(self.match_times) / len(self.match_times) if self.match_times else 0

            match_info = (
                f"已运行 {formatted_time}。匹配成功: {self.match_count}次\n"
                f"尺度: {scale:.6f}, 相似度: {max_val:.6f}\n"
                f"最小间隔: {min_time:.4f}s, 最大间隔: {max_time:.4f}s, 平均间隔: {avg_time:.4f}s"
            )
            self.status_signal.emit(match_info)
            return True
        else:
            current_time = time.time()
            elapsed_time = current_time - self.start_time
            formatted_time = self.format_time(elapsed_time)
            self.status_signal.emit(f"已运行 {formatted_time}。未找到匹配图像。最高相似度: {max_val:.6f}")
            return False


    def select_region(self):# 区域选择窗口
        self.region_selector = RegionSelector()
        self.region_selector.region_selected.connect(self.handle_region_selected)
        self.region_selector.show()

    def handle_region_selected(self, region):# 处理选择的区域
        self.selected_region = region
        self.status_signal.emit(f"已选择区域: x={region[0]}, y={region[1]}, w={region[2]}, h={region[3]}")
        self.region_selected.emit(region)


# ======================== 区域选择窗口 ========================
class RegionSelector(QWidget):
    region_selected = pyqtSignal(tuple)

    def __init__(self):
        super().__init__()
        self._drag_pos = None
        self.setWindowTitle("选择识别区域")
        self.setGeometry(100, 100, 400, 300)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background-color: rgba(52, 152, 219, 150); border: 2px solid #2980b9; border-radius: 10px;")

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        self.label = QLabel("调整窗口位置和大小覆盖字幕区域\n完成后点击确认")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("color: white; font-weight: bold; font-size: 14px;")
        layout.addWidget(self.label)

        self.confirm_btn = QPushButton("确认")
        self.confirm_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        self.confirm_btn.clicked.connect(self.confirm_selection)
        layout.addWidget(self.confirm_btn)

        self.setLayout(layout)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        if self._drag_pos is not None:
            delta = event.globalPos() - self._drag_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self._drag_pos = event.globalPos()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = None

    def confirm_selection(self):
        region = (self.geometry().x(), self.geometry().y(),
                  self.geometry().width(), self.geometry().height())
        self.region_selected.emit(region)
        self.close()

# ======================== 自动钓鱼标签页 ========================
class AutoFishTab(QWidget):
    def __init__(self):
        super().__init__()

        self.fisher = AutoFish()
        self.fisher.status_signal.connect(self.update_status)
        self.fisher.region_selected.connect(self.update_region_inputs)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        title = QLabel("自动钓鱼工具")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # 状态显示
        self.status_label = QLabel("状态: 未运行")
        self.status_label.setFont(QFont("Arial", 14))
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            background-color: #34495e;
            color: #3498db;
            border-radius: 10px;
            padding: 20px;
        """)
        layout.addWidget(self.status_label)

        # 控制按钮
        btn_layout = QHBoxLayout()

        self.start_btn = QPushButton("开始钓鱼")
        self.start_btn.setFont(QFont("Arial", 12))
        self.start_btn.clicked.connect(self.start_fishing)

        self.stop_btn = QPushButton("停止钓鱼")
        self.stop_btn.setFont(QFont("Arial", 12))
        self.stop_btn.clicked.connect(self.stop_fishing)
        self.stop_btn.setEnabled(False)

        self.select_region_btn = QPushButton("选择区域")
        self.select_region_btn.setFont(QFont("Arial", 12))
        self.select_region_btn.clicked.connect(self.fisher.select_region)

        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.stop_btn)
        btn_layout.addWidget(self.select_region_btn)
        layout.addLayout(btn_layout)

        # 设置面板
        settings_group = QGroupBox("钓鱼设置")
        settings_layout = QVBoxLayout()

        # 阈值设置
        threshold_layout = QHBoxLayout()
        threshold_layout.addWidget(QLabel("匹配阈值:"))
        self.threshold_input = QLineEdit("0.5")
        self.threshold_input.setFont(QFont("Arial", 12))
        threshold_layout.addWidget(self.threshold_input)
        settings_layout.addLayout(threshold_layout)

        # —— 模板选择 ——
        tmpl_layout = QHBoxLayout()
        tmpl_layout.addWidget(QLabel("模板路径:"))
        self.tmpl_path_label = QLabel(self.fisher.template_path)
        tmpl_layout.addWidget(self.tmpl_path_label, 1)
        self.select_tmpl_btn = QPushButton("选择模板")
        self.select_tmpl_btn.clicked.connect(self.select_template)
        tmpl_layout.addWidget(self.select_tmpl_btn)
        settings_layout.addLayout(tmpl_layout)

        # 区域设置
        region_layout = QGridLayout()
        region_layout.addWidget(QLabel("区域设置:"), 0, 0)

        region_layout.addWidget(QLabel("X:"), 0, 1)
        self.x_input = QLineEdit("0")
        self.x_input.setFont(QFont("Arial", 12))
        region_layout.addWidget(self.x_input, 0, 2)

        region_layout.addWidget(QLabel("Y:"), 0, 3)
        self.y_input = QLineEdit("0")
        self.y_input.setFont(QFont("Arial", 12))
        region_layout.addWidget(self.y_input, 0, 4)

        region_layout.addWidget(QLabel("宽度:"), 1, 1)
        self.w_input = QLineEdit("0")
        self.w_input.setFont(QFont("Arial", 12))
        region_layout.addWidget(self.w_input, 1, 2)

        region_layout.addWidget(QLabel("高度:"), 1, 3)
        self.h_input = QLineEdit("0")
        self.h_input.setFont(QFont("Arial", 12))
        region_layout.addWidget(self.h_input, 1, 4)

        settings_layout.addLayout(region_layout)
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

    def select_template(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择模板图像", "", "Image Files (*.png *.jpg *.bmp)")
        if file_path:
            self.fisher.template_path = file_path
            self.tmpl_path_label.setText(file_path)
            self.log_text.append(f"已选择模板: {file_path}")


    def start_fishing(self):
        try:
            # 更新区域设置
            region = (
                int(self.x_input.text()),
                int(self.y_input.text()),
                int(self.w_input.text()),
                int(self.h_input.text())
            )

            # 检查区域是否有效
            if any(dim <= 0 for dim in region):
                self.log_text.append("错误: 区域设置无效，请选择有效区域")
                return

            # 更新阈值
            threshold = float(self.threshold_input.text())
            self.fisher.vari_list = [threshold] + list(region)

            self.fisher.running = True
            self.fisher.start()

            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.select_region_btn.setEnabled(False)
            self.status_label.setText("状态: 运行中")
            self.status_label.setStyleSheet("""
                background-color: #34495e;
                color: #2ecc71;
                border-radius: 10px;
                padding: 20px;
            """)
            self.log_text.append("自动钓鱼已启动...")
        except Exception as e:
            self.log_text.append(f"启动失败: {str(e)}")

    def stop_fishing(self):
        self.fisher.running = False
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.select_region_btn.setEnabled(True)
        self.status_label.setText("状态: 已停止")
        self.status_label.setStyleSheet("""
            background-color: #34495e;
            color: #e74c3c;
            border-radius: 10px;
            padding: 20px;
        """)
        self.log_text.append("自动钓鱼已停止")

    def update_status(self, msg):
        self.log_text.append(msg)

    def update_region_inputs(self, region):
        """更新区域输入框的值"""
        self.x_input.setText(str(region[0]))
        self.y_input.setText(str(region[1]))
        self.w_input.setText(str(region[2]))
        self.h_input.setText(str(region[3]))
