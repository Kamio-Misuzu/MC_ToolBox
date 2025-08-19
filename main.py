import os
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QPushButton
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt, QSettings
from Auto_Click import AutoClickerTab
from DC_Click import PhantomClickTab
from Auto_Message_Auto import AutoMessageATab
from Auto_Fish import AutoFishTab
from License import LicenseManager, LicenseDialog
from Donate import DonateTab
import qdarktheme

def resource_path(path):
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, path)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        icon_path = "F:/python/MC/爬虫/640x640.ico"
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        else:
            print(f"图标不存在: {icon_path}")
        self.setWindowTitle("MC工具盒-下北泽虹夏")
        self.setGeometry(300, 100, 900, 700)

        self.settings = QSettings("下北泽虹夏", "MCToolbox")
        self.night_mode = self.settings.value("night_mode", False, type=bool)

        self.night_mode_button = QPushButton()
        self.night_mode_button.setFixedSize(100, 30)
        self.night_mode_button.clicked.connect(self.toggle_night_mode)

        # 标签页
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # 功能标签页
        self.auto_clicker_tab = AutoClickerTab()
        self.auto_click_tab = PhantomClickTab()
        self.auto_fish_tab = AutoFishTab()
        self.auto_msg_a_tab = AutoMessageATab()
        self.donate_tab = DonateTab()

        self.tabs.addTab(self.auto_clicker_tab, "连点器")
        self.tabs.addTab(self.auto_click_tab, "浮动连续点击")
        self.tabs.addTab(self.auto_fish_tab, "自动钓鱼-声音提示")
        self.tabs.addTab(self.auto_msg_a_tab, "自动消息")
        self.tabs.addTab(self.donate_tab, "打赏我")

        # 标签页图标
        self.tabs.setTabIcon(0, QIcon(resource_path("IcoImg/click.jpg")))
        self.tabs.setTabIcon(1, QIcon(resource_path("IcoImg/fish.jpg")))
        self.tabs.setTabIcon(2, QIcon(resource_path("IcoImg/msg_auto.jpg")))
        self.tabs.setTabIcon(3, QIcon(resource_path("IcoImg/auto_click.jpg")))
        self.tabs.setTabIcon(4, QIcon(resource_path("IcoImg/donate.jpg")))

        # 将夜间模式按钮添加到主窗口, 同时不随窗口放大缩小改动位置
        self.night_mode_button.setParent(self)
        self.night_mode_button.move(self.width() - 110, 10)

        self.update_night_mode_button()
        self.apply_theme()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.night_mode_button.move(self.width() - 110, 10)

    def toggle_night_mode(self):
        self.night_mode = not self.night_mode
        self.settings.setValue("night_mode", self.night_mode)
        self.update_night_mode_button()
        self.apply_theme()

    def update_night_mode_button(self):
        if self.night_mode:
            self.night_mode_button.setText("日间模式")
            self.night_mode_button.setStyleSheet(
                "QPushButton { background-color: #3498db; color: white; border-radius: 5px; }"
                "QPushButton:hover { background-color: #2980b9; }"
            )
        else:
            self.night_mode_button.setText("夜间模式")
            self.night_mode_button.setStyleSheet(
                "QPushButton { background-color: #2c3e50; color: white; border-radius: 5px; }"
                "QPushButton:hover { background-color: #34495e; }"
            )

    def apply_theme(self):
        if self.night_mode:
            # pip install pyqtdarktheme==2.1.0 --ignore-requires-python
            # 3.12+的python版本需要强制安装兼容版本
            qdarktheme.setup_theme("dark", custom_colors={
                "primary": "#3498db",
                "background": "#1e1e1e",
                "foreground": "#ffffff"
            })
        else:
            qdarktheme.setup_theme("light", custom_colors={
                "primary": "#3498db",
                "background": "#f5f5f5",
                "foreground": "#000000"
            })

        self.update_night_mode_button()

        for i in range(self.tabs.count()):
            tab = self.tabs.widget(i)
            if hasattr(tab, 'update_theme'):
                tab.update_theme(self.night_mode)

    def closeEvent(self, event):
        # 确保所有线程在关闭窗口时停止自动点击
        self.auto_clicker_tab.stop_clicker()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    font = QFont("Arial", 10)
    app.setFont(font)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     license_manager = LicenseManager()
#     valid, message = license_manager.validate_license()
#
#     if not valid:
#         dialog = LicenseDialog(license_manager)
#         if dialog.exec_() == QDialog.Accepted:
#             valid, message = license_manager.validate_license()
#         else:
#             sys.exit()
#     if not valid:
#         temp_app = QApplication(sys.argv)
#         QMessageBox.critical(None, "授权验证失败", f"{message}\n\n程序将退出。")
#         sys.exit()
#     window = MainWindow()
#     window.show()
#
#     remaining_days = license_manager.get_remaining_days()
#     if remaining_days > 0:
#         if hasattr(window, 'log_text'):
#             window.log_text.append(f'<span style="color:#2ecc71">授权验证成功！剩余天数: {remaining_days}天</span>')
#             window.log_text.setStyleSheet("background-color: #1b1b1b; color: #ecf0f1;")
#         else:
#             msg = QMessageBox(window)
#             msg.setWindowTitle("授权信息")
#             msg.setIcon(QMessageBox.Information)
#             msg.setText(f"<div style='color:#ecf0f1; font-size:12pt;'>授权验证成功！剩余天数: {remaining_days}天</div>")
#             msg.setStandardButtons(QMessageBox.Ok)
#             msg.setStyleSheet("""
#                 QMessageBox {
#                     background-color: #2c3e50;
#                 }
#                 QLabel {
#                     color: #ecf0f1;
#                 }
#                 QPushButton {
#                     background-color: #3498db;
#                     color: white;
#                     padding: 6px 12px;
#                     border-radius: 6px;
#                 }
#                 QPushButton:hover {
#                     background-color: #2980b9;
#                 }
#             """)
#             msg.exec_()
#
#     sys.exit(app.exec_())