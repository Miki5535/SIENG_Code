from PyQt5.QtWidgets import (
  QWidget, QVBoxLayout, QGroupBox, QLineEdit, QComboBox, QPushButton, QLabel,
  QTextEdit, QHBoxLayout, QScrollArea, QFrame, QMessageBox
)
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtGui import QDesktopServices
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
import base64
import os
import random
import string
import time

class EncryptionTab(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.rsa_keys = None

    def initUI(self):
        self.setStyleSheet("""
            QWidget {
                background: transparent;
                color: #ffffff;
                font-family: 'Segoe UI', 'Roboto', Arial, sans-serif;
            }
            QGroupBox {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2d2d44, stop:1 #1e1e2e);
                border: 2px solid #00d4ff;
                border-radius: 12px;
                margin-top: 10px;
                padding: 15px;
                font-size: 14px;
                font-weight: bold;
                color: #00d4ff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px 0 8px;
                color: #00d4ff;
                font-size: 16px;
                font-weight: bold;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1e1e2e, stop:1 #2d2d44);
                border-radius: 6px;
            }
            QFrame#card {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3a3a54, stop:1 #2a2a3e);
                border: 1px solid #555;
                border-radius: 10px;
                padding: 12px;
                margin: 3px;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4a90e2, stop:1 #357abd);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 16px;
                font-size: 13px;
                font-weight: bold;
                min-height: 18px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5ba0f2, stop:1 #4585c7);
            }
            QPushButton:pressed {
                background: #2d5aa0;
            }
            QPushButton#generateKeyButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2196F3, stop:1 #1976D2);
            }
            QPushButton#generateKeyButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #42A5F5, stop:1 #2196F3);
            }
            QPushButton#encryptButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4CAF50, stop:1 #388E3C);
            }
            QPushButton#encryptButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #66BB6A, stop:1 #4CAF50);
            }
            QPushButton#decryptButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FF9800, stop:1 #F57C00);
            }
            QPushButton#decryptButton:hover {
                background: qline4gradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FFB74D, stop:1 #FF9800);
            }
            QPushButton#signButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #673AB7, stop:1 #512DA8);
            }
            QPushButton#signButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #9575CD, stop:1 #673AB7);
            }
            QPushButton#verifyButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #009688, stop:1 #00796B);
            }
            QPushButton#verifyButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4DB6AC, stop:1 #009688);
            }
            QPushButton#folderButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #424242, stop:1 #616161);
            }
            QPushButton#folderButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #757575, stop:1 #9e9e9e);
            }
            QComboBox {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3a3a54, stop:1 #2a2a3e);
                color: #ffffff;
                border: 2px solid #555;
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 12px;
                font-weight: bold;
                min-width: 100px;
            }
            QComboBox:hover {
                border-color: #00d4ff;
            }
            QComboBox:focus {
                border-color: #00d4ff;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4a4a64, stop:1 #3a3a4e);
            }
            QComboBox::drop-down {
                border: none;
                width: 25px;
                background: transparent;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid #00d4ff;
                margin-right: 6px;
            }
            QComboBox QAbstractItemView {
                background: #2a2a3e;
                border: 2px solid #00d4ff;
                border-radius: 6px;
                selection-background-color: #00d4ff;
                selection-color: white;
                color: white;
                padding: 4px;
            }
            QLineEdit {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1e1e2e, stop:1 #2d2d44);
                color: #ffffff;
                border: 2px solid #555;
                border-radius: 8px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
                padding: 8px;
            }
            QLineEdit:focus {
                border-color: #00d4ff;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2e2e3e, stop:1 #3d3d54);
            }
            QTextEdit {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1e1e2e, stop:1 #2d2d44);
                color: #ffffff;
                border: 2px solid #555;
                border-radius: 8px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
                padding: 10px;
                line-height: 1.3;
            }
            QTextEdit:focus {
                border-color: #00d4ff;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2e2e3e, stop:1 #3d3d54);
            }
            QLabel {
                color: #cccccc;
                font-size: 12px;
                font-weight: bold;
                background: transparent;
            }
        """)
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
            } """)

            
        
        scroll_content_widget = QWidget()
        scroll_content_layout = QVBoxLayout(scroll_content_widget)
        scroll_content_layout.setSpacing(15)
        scroll_content_layout.setContentsMargins(0,0,0,0)
        horizontal_group_layout = QHBoxLayout()
        horizontal_group_layout.setSpacing(15)
        
        aes_group = QGroupBox("🔐 AES Encryption")
        aes_layout = QVBoxLayout()
        aes_layout.setSpacing(10)
        aes_mode_frame = QFrame()
        aes_mode_frame.setObjectName("card")
        aes_mode_layout = QVBoxLayout(aes_mode_frame)
        aes_mode_layout.setContentsMargins(5,5,5,5)
        
        
        self.aes_combo = QComboBox()
        self.aes_combo.addItems(["AES-ECB", "AES-CBC", "AES-CFB", "AES-OFB", "AES-GCM"])
        aes_mode_layout.addWidget(self.aes_combo)
        aes_layout.addWidget(aes_mode_frame)
        aes_inputs_frame = QFrame()
        aes_inputs_frame.setObjectName("card")
        aes_inputs_layout = QVBoxLayout(aes_inputs_frame)
        aes_inputs_layout.setContentsMargins(5,5,5,5)
        aes_inputs_layout.addWidget(QLabel("Message"))
        
        self.aes_message_input = QTextEdit()
        self.aes_message_input.setPlaceholderText("Enter message for AES encryption/decryption")
        self.aes_message_input.setMinimumHeight(100)
        aes_inputs_layout.addWidget(self.aes_message_input)
        
        
        aes_inputs_layout.addWidget(QLabel("Key (16, 24, or 32 bytes)"))
        
        
        self.aes_key_input = QLineEdit()
        self.aes_key_input.setPlaceholderText("Enter AES key")
        
        aes_inputs_layout.addWidget(self.aes_key_input)
        aes_layout.addWidget(aes_inputs_frame)
        aes_buttons_frame = QFrame()
        aes_buttons_frame.setObjectName("card")
        aes_buttons_layout = QHBoxLayout(aes_buttons_frame)
        aes_buttons_layout.setContentsMargins(5,5,5,5)
        aes_buttons_layout.setSpacing(10)
        self.aes_random_key_button = QPushButton("🔑 Generate Key")
        self.aes_random_key_button.setObjectName("generateKeyButton")
        self.aes_random_key_button.clicked.connect(self.generate_random_key)
        self.aes_random_key_button.setMinimumHeight(40)
        self.aes_encrypt_button = QPushButton("🔒 Encrypt AES")
        self.aes_encrypt_button.setObjectName("encryptButton")
        self.aes_encrypt_button.clicked.connect(self.encrypt_aes)
        self.aes_encrypt_button.setMinimumHeight(40)
        self.aes_decrypt_button = QPushButton("🔓 Decrypt AES")
        self.aes_decrypt_button.setObjectName("decryptButton")
        self.aes_decrypt_button.clicked.connect(self.decrypt_aes)
        self.aes_decrypt_button.setMinimumHeight(40)
        aes_buttons_layout.addStretch()
        aes_buttons_layout.addWidget(self.aes_random_key_button)
        aes_buttons_layout.addWidget(self.aes_encrypt_button)
        aes_buttons_layout.addWidget(self.aes_decrypt_button)
        aes_buttons_layout.addStretch()
        aes_layout.addWidget(aes_buttons_frame)
        aes_group.setLayout(aes_layout)
        horizontal_group_layout.addWidget(aes_group)
        
        
        
        rsa_group = QGroupBox("🔑 RSA Encryption")
        rsa_layout = QVBoxLayout()
        rsa_layout.setSpacing(10)
        rsa_inputs_frame = QFrame()
        rsa_inputs_frame.setObjectName("card")
        rsa_inputs_layout = QVBoxLayout(rsa_inputs_frame)
        rsa_inputs_layout.setContentsMargins(5,5,5,5)
        
        rsa_inputs_layout.addWidget(QLabel("Message"))
        
        self.rsa_message_input = QTextEdit()
        self.rsa_message_input.setPlaceholderText("Enter message for RSA operations")
        self.rsa_message_input.setMinimumHeight(100)
        rsa_inputs_layout.addWidget(self.rsa_message_input)
        
        

        keys_h_layout = QHBoxLayout()
        public_key_v_layout = QVBoxLayout()
        public_key_label = QLabel("Public Key")
        public_key_v_layout.addWidget(public_key_label)
        self.rsa_public_key_input = QTextEdit()
        self.rsa_public_key_input.setPlaceholderText("Paste Public Key here")
        self.rsa_public_key_input.setMinimumHeight(200)
        public_key_v_layout.addWidget(self.rsa_public_key_input)
        keys_h_layout.addLayout(public_key_v_layout)

        
        private_key_v_layout = QVBoxLayout()
        private_key_label = QLabel("Private Key")
        private_key_v_layout.addWidget(private_key_label)
        self.rsa_private_key_input = QTextEdit()
        self.rsa_private_key_input.setPlaceholderText("Paste Private Key here")
        self.rsa_private_key_input.setMinimumHeight(200)
        private_key_v_layout.addWidget(self.rsa_private_key_input)
        keys_h_layout.addLayout(private_key_v_layout)

        
        rsa_inputs_layout.addLayout(keys_h_layout)
        

        
        rsa_layout.addWidget(rsa_inputs_frame)
        rsa_buttons_frame = QFrame()
        rsa_buttons_frame.setObjectName("card")
        rsa_buttons_layout = QVBoxLayout(rsa_buttons_frame)
        rsa_buttons_layout.setContentsMargins(5,5,5,5)
        rsa_buttons_layout.setSpacing(10)
        rsa_key_gen_layout = QHBoxLayout()
        rsa_key_gen_layout.addStretch()
        
        self.rsa_generate_keys_button = QPushButton("✨ Generate Key Pair")
        self.rsa_generate_keys_button.setObjectName("generateKeyButton")
        self.rsa_generate_keys_button.clicked.connect(self.generate_rsa_keys)
        self.rsa_generate_keys_button.setMinimumHeight(40)
        rsa_key_gen_layout.addWidget(self.rsa_generate_keys_button)
        rsa_key_gen_layout.addStretch()
        rsa_buttons_layout.addLayout(rsa_key_gen_layout)
        rsa_encrypt_decrypt_layout = QHBoxLayout()
        rsa_encrypt_decrypt_layout.setSpacing(10)
        
        self.rsa_encrypt_button = QPushButton("🔒 Encrypt RSA")
        self.rsa_encrypt_button.setObjectName("encryptButton")
        self.rsa_encrypt_button.clicked.connect(self.encrypt_rsa)
        self.rsa_encrypt_button.setMinimumHeight(40)
        self.rsa_decrypt_button = QPushButton("🔓 Decrypt RSA")
        self.rsa_decrypt_button.setObjectName("decryptButton")
        self.rsa_decrypt_button.clicked.connect(self.decrypt_rsa)
        self.rsa_decrypt_button.setMinimumHeight(40)
        rsa_encrypt_decrypt_layout.addStretch()
        rsa_encrypt_decrypt_layout.addWidget(self.rsa_encrypt_button)
        rsa_encrypt_decrypt_layout.addWidget(self.rsa_decrypt_button)
        rsa_encrypt_decrypt_layout.addStretch()
        rsa_buttons_layout.addLayout(rsa_encrypt_decrypt_layout)
        rsa_sign_verify_layout = QHBoxLayout()
        rsa_sign_verify_layout.setSpacing(10)
        

        
        
        self.output_folder_button = QPushButton("📁 Open Key Folder")
        self.output_folder_button.setObjectName("folderButton")
        self.output_folder_button.clicked.connect(self.open_output_folder)
        self.output_folder_button.setMinimumHeight(40)
        
        

        
        
        
        rsa_layout.addWidget(rsa_buttons_frame)
        rsa_group.setLayout(rsa_layout)
        horizontal_group_layout.addWidget(rsa_group)
        scroll_content_layout.addLayout(horizontal_group_layout)
        output_group = QGroupBox("📊 Process Log")
        output_layout = QVBoxLayout()
        output_layout.setSpacing(10)
        self.aes_result_output = QTextEdit()
        self.aes_result_output.setReadOnly(True)
        self.aes_result_output.setPlaceholderText("Encryption/Decryption results and logs will appear here...")
        self.aes_result_output.setMinimumHeight(180)
        output_layout.addWidget(self.aes_result_output)
        output_group.setLayout(output_layout)
        scroll_content_layout.addWidget(output_group)
        scroll_area.setWidget(scroll_content_widget)
        main_layout.addWidget(scroll_area)
        self.setLayout(main_layout)

    def generate_random_key(self):
        key_lengths = [16, 24, 32]
        generated_keys = {}
        for length in key_lengths:
            key = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
            generated_keys[length] = key
        self.aes_result_output.append("<span style='color: #00d4ff;'>--- Generated AES Keys ---</span>")
        for length, key in generated_keys.items():
            self.aes_result_output.append(f"<b>Key {length} Bytes:</b> <span style='color:#00ff88;'>{key}</span>")
        self.aes_result_output.append("<span style='color: #00d4ff;'>--------------------------</span>")



    def encrypt_aes(self):
        message = self.aes_message_input.toPlainText()  
        key = self.aes_key_input.text()
        encryption_type = self.aes_combo.currentText()

        if not message:
            self.aes_result_output.append("<span style='color: #ff4444;'>❌ Please enter a message to encrypt.</span>")
            return
        if not key:
            self.aes_result_output.append("<span style='color: #ff4444;'>❌ Please enter an AES key.</span>")
            return
        
        try:
            key_bytes = key.encode('utf-8')
            if len(key_bytes) not in [16, 24, 32]:
                self.aes_result_output.append("<span style='color: #ff4444;'>❌ Key must be 16, 24, or 32 bytes long.</span>")
                return
            encrypted = ""
            if encryption_type == "AES-ECB":
                cipher = AES.new(key_bytes, AES.MODE_ECB)
                encrypted = base64.b64encode(cipher.encrypt(pad(message.encode('utf-8'), AES.block_size))).decode('utf-8')
            else:
                iv = get_random_bytes(16)
                if encryption_type == "AES-CBC":
                    cipher = AES.new(key_bytes, AES.MODE_CBC, iv)
                    encrypted = base64.b64encode(iv + cipher.encrypt(pad(message.encode('utf-8'), AES.block_size))).decode('utf-8')
                elif encryption_type == "AES-CFB":
                    cipher = AES.new(key_bytes, AES.MODE_CFB, iv)
                    encrypted = base64.b64encode(iv + cipher.encrypt(message.encode('utf-8'))).decode('utf-8')
                elif encryption_type == "AES-OFB":
                    cipher = AES.new(key_bytes, AES.MODE_OFB, iv)
                    encrypted = base64.b64encode(iv + cipher.encrypt(message.encode('utf-8'))).decode('utf-8')
                elif encryption_type == "AES-GCM":
                    cipher = AES.new(key_bytes, AES.MODE_GCM)
                    ciphertext, tag = cipher.encrypt_and_digest(message.encode('utf-8'))
                    encrypted = base64.b64encode(cipher.nonce + ciphertext + tag).decode('utf-8')
            self.aes_result_output.append(f"<span style='color: #00ff88;'>✅ Encrypted ({encryption_type}):</span> <span style='color:#00d4ff;'>{encrypted}</span>")
        except Exception as e:
            self.aes_result_output.append(f"<span style='color: #ff4444;'>❌ Error encrypting: {str(e)}</span>")

    def decrypt_aes(self):
        encrypted_message = self.aes_message_input.toPlainText()
        key = self.aes_key_input.text()

        if not encrypted_message or not key:
            self.aes_result_output.append("<span style='color: #ff4444;'>❌ Please enter both encrypted message and key.</span>")
            return
        try:
            encrypted_data = base64.b64decode(encrypted_message)
            key_bytes = key.encode('utf-8')
            if len(key_bytes) not in [16, 24, 32]:
                self.aes_result_output.append("<span style='color: #ff4444;'>❌ Key must be 16, 24, or 32 bytes long.</span>")
                return
            decrypted_text = None
            modes_to_try = ["AES-ECB", "AES-CBC", "AES-CFB", "AES-OFB", "AES-GCM"]
            for mode_name in modes_to_try:
                try:
                    if mode_name == "AES-ECB":
                        cipher = AES.new(key_bytes, AES.MODE_ECB)
                        decrypted_text = unpad(cipher.decrypt(encrypted_data), AES.block_size).decode('utf-8')
                    elif mode_name in ["AES-CBC", "AES-CFB", "AES-OFB"]:
                        iv, data = encrypted_data[:16], encrypted_data[16:]
                        if len(iv) != 16: continue
                        cipher = AES.new(key_bytes, getattr(AES, f"MODE_{mode_name.split('-')[1]}"), iv)
                        decrypted_data = cipher.decrypt(data)
                        decrypted_text = unpad(decrypted_data, AES.block_size).decode('utf-8') if mode_name == "AES-CBC" else decrypted_data.decode('utf-8')
                    elif mode_name == "AES-GCM":
                        nonce, ciphertext, tag = encrypted_data[:16], encrypted_data[16:-16], encrypted_data[-16:]
                        if len(nonce) != 16 or len(tag) != 16: continue
                        cipher = AES.new(key_bytes, AES.MODE_GCM, nonce=nonce)
                        decrypted_text = cipher.decrypt_and_verify(ciphertext, tag).decode('utf-8')
                    if decrypted_text:
                        self.aes_result_output.append(f"<span style='color: #00ff88;'>✅ Decrypted ({mode_name}):</span> <span style='color:#ffffff;'>{decrypted_text}</span>")
                        return
                except Exception as inner_e:
                    continue
            self.aes_result_output.append("<span style='color: #ff4444;'>❌ Could not decrypt message with any mode. Check key and message.</span>")
        except Exception as e:
            self.aes_result_output.append(f"<span style='color: #ff4444;'>❌ Error decrypting: {str(e)}</span>")



    def open_output_folder(self):
        current_directory = os.path.dirname(os.path.realpath(__file__))
        parent_directory = os.path.dirname(current_directory)
        output_path = os.path.join(parent_directory, "key_output")
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        QDesktopServices.openUrl(QUrl.fromLocalFile(output_path))
        self.aes_result_output.append("<span style='color: #00d4ff;'>📁 Key output folder opened.</span>")

    def generate_rsa_keys(self):
        try:
            key = RSA.generate(2048)
            self.rsa_keys = key
            private_key_pem = key.export_key().decode('utf-8')
            public_key_pem = key.publickey().export_key().decode('utf-8')
            output_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "key_output")
            os.makedirs(output_dir, exist_ok=True)
            timestamp = int(time.time())
            private_key_path = os.path.join(output_dir, f"private_key.pem")
            public_key_path = os.path.join(output_dir, f"public_key.pem")
            with open(private_key_path, "w") as f:
                f.write(private_key_pem)
            with open(public_key_path, "w") as f:
                f.write(public_key_pem)
            self.rsa_private_key_input.setPlainText(private_key_pem)
            self.rsa_public_key_input.setPlainText(public_key_pem)
            self.aes_result_output.append(f"<span style='color: #00ff88;'>✅ RSA key pair generated and saved to <font color='#00d4ff'>{os.path.basename(output_dir)}</font></span>")
            self.aes_result_output.append(f"  - Private Key: {private_key_path}")
            self.aes_result_output.append(f"  - Public Key: {public_key_path}")
        except Exception as e:
            self.aes_result_output.append(f"<span style='color: #ff4444;'>❌ Error generating RSA keys: {str(e)}</span>")

    def encrypt_rsa(self):
        public_key_str = self.rsa_public_key_input.toPlainText()
        message = self.rsa_message_input.toPlainText()  
        if not public_key_str:
            self.aes_result_output.append("<span style='color: #ff4444;'>❌ Please provide a Public Key.</span>")
            return
        if not message:
            self.aes_result_output.append("<span style='color: #ff4444;'>❌ Please enter a message to encrypt.</span>")
            return
        try:
            public_key = RSA.import_key(public_key_str)
            cipher = PKCS1_OAEP.new(public_key)
            ciphertext = cipher.encrypt(message.encode('utf-8'))
            encoded_ciphertext = base64.b64encode(ciphertext).decode('utf-8')
            self.aes_result_output.append(f"<span style='color: #00ff88;'>✅ RSA Encrypted:</span> <span style='color:#00d4ff;'>{encoded_ciphertext}</span>")
        except Exception as e:
            self.aes_result_output.append(f"<span style='color: #ff4444;'>❌ Error encrypting with RSA: {str(e)}</span>")

    def decrypt_rsa(self):
        private_key_str = self.rsa_private_key_input.toPlainText()
        ciphertext_b64 =  self.rsa_message_input.toPlainText()  
        if not private_key_str:
            self.aes_result_output.append("<span style='color: #ff4444;'>❌ Please provide a Private Key.</span>")
            return
        if not ciphertext_b64:
            self.aes_result_output.append("<span style='color: #ff4444;'>❌ Please enter the encrypted message.</span>")
            return
        try:
            private_key = RSA.import_key(private_key_str)
            ciphertext_bytes = base64.b64decode(ciphertext_b64)
            cipher = PKCS1_OAEP.new(private_key)
            plaintext = cipher.decrypt(ciphertext_bytes).decode('utf-8')
            self.aes_result_output.append(f"<span style='color: #00ff88;'>✅ RSA Decrypted:</span> <span style='color:#ffffff;'>{plaintext}</span>")
        except Exception as e:
            self.aes_result_output.append(f"<span style='color: #ff4444;'>❌ Error decrypting with RSA: {str(e)}</span>")


    def verify_signature_rsa(self):
      public_key_str = self.rsa_public_key_input.toPlainText()
      message = self.rsa_message_input.toPlainText()

      signature_base64 = self.signature_input.toPlainText()
      if not public_key_str:
          self.aes_result_output.append("<span style='color: #ff4444;'>❌ Please provide a Public Key.</span>")
          return
      if not message:
          self.aes_result_output.append("<span style='color: #ff4444;'>❌ Please enter the original message.</span>")
          return
      if not signature_base64:
          self.aes_result_output.append("<span style='color: #ff4444;'>❌ Please enter the digital signature.</span>")
          return
      try:
          public_key = RSA.import_key(public_key_str)
          signature = base64.b64decode(signature_base64)
          message_hash = SHA256.new(message.encode('utf-8'))
          pkcs1_15.new(public_key).verify(message_hash, signature)
          self.aes_result_output.append("<span style='color: #00ff88;'>✅ Signature is VALID.</span>")
      except ValueError:
          self.aes_result_output.append("<span style='color: #ff4444;'>❌ Signature is INVALID.</span>")
      except Exception as e:
          self.aes_result_output.append(f"<span style='color: #ff4444;'>❌ Error verifying signature: {str(e)}</span>")