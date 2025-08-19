import datetime
import os
from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout,QLabel, QPushButton, QLineEdit, QMessageBox, QDialog)
from PyQt5.QtCore import Qt
from Crypto.Cipher import AES
import uuid
import json
import base64
from Crypto.Hash import SHA256
from Constant import SECRET_KEY

# ======================== 授权系统核心类 ========================
class LicenseManager:
    def __init__(self):
        self.license_file = "license.key"
        self.license_data = None
        self.machine_id = self.get_machine_id()

    def get_machine_id(self):
        """获取机器唯一标识符"""
        try:
            # Windows
            if os.name == 'nt':
                import winreg
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Cryptography")
                value, _ = winreg.QueryValueEx(key, "MachineGuid")
                return value
            # Linux
            elif os.name == 'posix':
                with open('/etc/machine-id', 'r') as f:
                    return f.read().strip()
            # macOS
            else:
                return str(uuid.uuid4())
        except Exception:
            return str(uuid.uuid4())

    def _derive_key(self, secret):
         # SHA256将任意长度的secret转成32字节AES key
        h = SHA256.new()
        h.update(secret.encode('utf-8'))
        return h.digest()  # 32字节

    def generate_license(self, days):
        expiration = datetime.datetime.now() + datetime.timedelta(days=days)
        license_data = {
            "machine_id": self.machine_id,
            "expiration": expiration.isoformat(),
            "days": days
        }

        json_data = json.dumps(license_data).encode('utf-8')
        key = self._derive_key(SECRET_KEY)

        cipher = AES.new(key, AES.MODE_EAX)
        ciphertext, tag = cipher.encrypt_and_digest(json_data)
        nonce = cipher.nonce

        # 保存：先写入 nonce ，再写 nonce、tag、ciphertext
        with open(self.license_file, 'wb') as f:
            f.write(len(nonce).to_bytes(1, 'big'))
            f.write(nonce)
            f.write(tag)
            f.write(ciphertext)

        return base64.b64encode(ciphertext).decode('utf-8')

    def validate_license(self, key=SECRET_KEY):
        if not os.path.exists(self.license_file):
            return False, "许可证文件不存在"

        try:
            with open(self.license_file, 'rb') as f:
                nonce_len_b = f.read(1)
                if not nonce_len_b:
                    return False, "许可证文件损坏（缺少 nonce 长度）"
                nonce_len = int.from_bytes(nonce_len_b, 'big')
                nonce = f.read(nonce_len)
                tag = f.read(16)
                ciphertext = f.read()

            key_bytes = self._derive_key(SECRET_KEY)
            cipher = AES.new(key_bytes, AES.MODE_EAX, nonce=nonce)
            data = cipher.decrypt_and_verify(ciphertext, tag)

            self.license_data = json.loads(data.decode('utf-8'))

            # 检查机器ID
            if self.license_data.get('machine_id') != self.machine_id:
                return False, "许可证与当前设备不匹配"

            # 检查有效期
            expiration = datetime.datetime.fromisoformat(self.license_data['expiration'])
            if datetime.datetime.now() > expiration:
                return False, f"许可证已于 {expiration.strftime('%Y-%m-%d')} 过期"

            return True, f"许可证有效，有效期至 {expiration.strftime('%Y-%m-%d')}"
        except Exception as e:
            return False, f"许可证验证失败: {str(e)}"

    def get_remaining_days(self):
        # 获取剩余天数
        if not self.license_data:
            return 0

        expiration = datetime.datetime.fromisoformat(self.license_data['expiration'])
        delta = expiration - datetime.datetime.now()
        return delta.days + 1 if delta.days >= 0 else 0


# ======================== 授权输入对话框 ========================
class LicenseDialog(QDialog):
    def __init__(self, license_manager):
        super().__init__()
        self.license_manager = license_manager
        self.setWindowTitle("程序授权验证")
        self.setFixedSize(500, 300)
        self.setStyleSheet("""
            QDialog {
                background-color: #2c3e50;
                color: #ecf0f1;
            }
            QLabel {
                font-size: 14px;
                color: #bdc3c7;
            }
            QLineEdit {
                background-color: #34495e;
                border: 1px solid #3498db;
                border-radius: 5px;
                padding: 8px;
                color: #ecf0f1;
                font-size: 14px;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-size: 14px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1c6ea4;
            }
        """)

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        title = QLabel("MC工具盒授权验证")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #3498db;")
        layout.addWidget(title)

        description = QLabel("本程序需要有效的授权密钥才能使用。请输入您的授权密钥以解锁全部功能。")
        description.setWordWrap(True)
        layout.addWidget(description)

        device_id_label = QLabel(f"设备ID: {self.license_manager.machine_id}")
        device_id_label.setWordWrap(True)
        layout.addWidget(device_id_label)
        license_layout = QHBoxLayout()
        license_layout.addWidget(QLabel("授权密钥:"))
        self.license_input = QLineEdit()
        license_layout.addWidget(self.license_input, 1)
        layout.addLayout(license_layout)
        btn_layout = QHBoxLayout()

        self.activate_btn = QPushButton("激活授权")
        self.activate_btn.clicked.connect(self.activate_license)
        btn_layout.addWidget(self.activate_btn)

        self.exit_btn = QPushButton("退出程序")
        self.exit_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.exit_btn)

        layout.addLayout(btn_layout)

        self.status_label = QLabel()
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet("color: #e74c3c;")
        layout.addWidget(self.status_label)

        trial_info = QLabel("答案是: 下北泽虹夏")
        trial_info.setStyleSheet("font-size: 12px; color: #7f8c8d;")
        trial_info.setAlignment(Qt.AlignCenter)
        layout.addWidget(trial_info)

        self.setLayout(layout)

    def activate_license(self):
        license_key = self.license_input.text().strip()
        if not license_key:
            self.status_label.setText("请输入有效的授权密钥")
            return
        if license_key == SECRET_KEY:
            try:
                self.license_manager.generate_license(999999)
                valid, msg = self.license_manager.validate_license()
                if valid:
                    self.accept()
                else:
                    QMessageBox.critical(self, "授权失败", f"授权生成后验证失败：{msg}")
            except Exception as e:
                QMessageBox.critical(self, "激活异常", f"激活过程中出现错误：{str(e)}")
        else:
            self.status_label.setText("授权密钥无效，请检查后重试")