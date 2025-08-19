import os
import sys

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QScrollArea)
from PyQt5.QtGui import QPixmap, QFont, QColor
from PyQt5.QtCore import Qt, QTimer

def resource_path(path):
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, path)

class DonateTab(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        title_label = QLabel("打赏我")
        title_label.setFont(QFont("Microsoft YaHei", 20, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #3498db;")
        main_layout.addWidget(title_label)

        self.thanks_label = QLabel(
            "感谢您使用MC工具盒！如果这个工具对您有帮助，欢迎请作者喝杯咖啡QAQ"
        )

        self.thanks_label.setFont(QFont("Microsoft YaHei", 12))
        self.thanks_label.setAlignment(Qt.AlignCenter)
        self.thanks_label.setWordWrap(True)
        self.thanks_label.setStyleSheet("color: #D8BFD8;")
        main_layout.addWidget(self.thanks_label)

        # 分割线
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("background-color: #3498db;")
        main_layout.addWidget(separator)

        # 二维码区域
        qr_layout = QHBoxLayout()
        qr_layout.setSpacing(50)

        # 支付宝二维码
        alipay_group = self.create_qr_group("支付宝", resource_path("IcoImg/zfb.jpg"))
        qr_layout.addWidget(alipay_group)

        # 微信二维码
        wechat_group = self.create_qr_group("微信", resource_path("IcoImg/wx.jpg"))
        qr_layout.addWidget(wechat_group)

        main_layout.addLayout(qr_layout)
        bottom_label = QLabel("如有任何问题或建议，请联系我")
        bottom_label.setFont(QFont("Microsoft YaHei", 10))
        bottom_label.setAlignment(Qt.AlignCenter)
        bottom_label.setStyleSheet("color: #bdc3c7;")
        main_layout.addWidget(bottom_label)

        self.setLayout(main_layout)

        # ---------- 炫彩文字动画设置 ----------
        self._hue = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update_thanks_color)
        self._timer.start(30)

    def _update_thanks_color(self):
        color = QColor.fromHsv(self._hue % 360, 255, 235)
        self.thanks_label.setStyleSheet(f"color: {color.name()};")
        self._hue += 2

    def create_qr_group(self, title, image_path):
        group = QWidget()
        group_layout = QVBoxLayout(group)
        group_layout.setSpacing(10)

        title_label = QLabel(title)
        title_label.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #3498db;")
        group_layout.addWidget(title_label)

        # 二维码图片
        qr_label = QLabel()
        if os.path.exists(image_path):
            pixmap = QPixmap(image_path)
            scaled_pixmap = pixmap.scaled(300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            qr_label.setPixmap(scaled_pixmap)
        else:
            qr_label.setText(f"二维码图片未找到: {image_path}")
            qr_label.setStyleSheet("color: #e74c3c;")
        qr_label.setAlignment(Qt.AlignCenter)
        qr_label.setMinimumSize(250, 250)
        group_layout.addWidget(qr_label)

        # tip_label = QLabel(f"使用{title}扫码支持")
        # tip_label.setAlignment(Qt.AlignCenter)
        # tip_label.setStyleSheet("color: #ecf0f1;")
        # group_layout.addWidget(tip_label)

        return group


# if __name__ == '__main__':
#     import sys
#     from PyQt5.QtWidgets import QApplication
#     app = QApplication(sys.argv)
#     w = DonateTab()
#     w.show()
#     sys.exit(app.exec_())
