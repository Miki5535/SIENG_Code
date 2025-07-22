import os
import datetime
from PyQt5.QtWidgets import (
  QWidget, QVBoxLayout, QGroupBox, QHBoxLayout, QLineEdit,
  QTextEdit, QPushButton, QLabel, QMessageBox, QDialog, QFormLayout,
  QComboBox, QTextBrowser, QDialogButtonBox, QFileDialog, QInputDialog,
  QScrollArea, QFrame
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QUrl
import gnupg

class PGPTab(QWidget):
    def __init__(self):
        super().__init__()
        self.gpg_instance = gnupg.GPG()
        self.initUI()

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
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
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
            QPushButton#listKeysButton, QPushButton#importKeyButton, QPushButton#exportKeyButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #424242, stop:1 #616161);
            }
            QPushButton#listKeysButton:hover, QPushButton#importKeyButton:hover, QPushButton#exportKeyButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #757575, stop:1 #9e9e9e);
            }
            QPushButton#deleteKeyButton {
                background: #dc3545;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 11px;
                font-weight: bold;
                min-height: 20px;
            }
            QPushButton#deleteKeyButton:hover {
                background: #c82333;
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
            QTextEdit, QTextBrowser {
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
            QTextEdit:focus, QTextBrowser:focus {
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
            QScrollBar:vertical {
                background: #2a2a3e;
                width: 10px;
                border-radius: 5px;
                margin: 0;
            }
            QScrollBar::handle:vertical {
                background: #00d4ff;
                border-radius: 5px;
                min-height: 15px;
                margin: 1px;
            }
            QScrollBar::handle:vertical:hover {
                background: #33ddff;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
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
        
        pgp_group = QGroupBox("🔑 PGP Security & Key Management")
        pgp_layout = QVBoxLayout()
        pgp_layout.setSpacing(10)
        
        # เพิ่ม UI สำหรับเลือกไฟล์และข้อความ
        message_input_frame = QFrame()
        message_input_frame.setObjectName("card")
        message_input_layout = QVBoxLayout(message_input_frame)
        message_input_layout.setContentsMargins(5,5,5,5)
        message_input_layout.addWidget(QLabel("Message or File Content:"))
        
        # เพิ่มช่องสำหรับเลือกไฟล์
        self.file_path_input = QLineEdit()
        self.file_path_input.setPlaceholderText("No file selected")
        self.file_path_input.setReadOnly(True)
        message_input_layout.addWidget(self.file_path_input)
        
        self.select_file_button = QPushButton("📂 Select File")
        self.select_file_button.setObjectName("encryptButton")
        self.select_file_button.clicked.connect(self.select_file)
        self.select_file_button.setMinimumHeight(30)
        message_input_layout.addWidget(self.select_file_button)
        
        # ช่องเดิมสำหรับข้อความ
        self.rsa_message_input = QLineEdit()
        self.rsa_message_input.setPlaceholderText("Enter text or drag & drop a file")
        message_input_layout.addWidget(self.rsa_message_input)
        
        pgp_layout.addWidget(message_input_frame)
        
        # UI สำหรับ Public Key, Private Key และ Signature
        keys_signature_frame = QFrame()
        keys_signature_frame.setObjectName("card")
        keys_signature_layout = QHBoxLayout(keys_signature_frame)
        keys_signature_layout.setContentsMargins(5, 5, 5, 5)
        keys_signature_layout.setSpacing(10)
        
        # Public Key
        public_key_layout = QVBoxLayout()
        public_key_layout.addWidget(QLabel("Public Key (ASCII Armored):"))
        self.rsa_public_key_input = QTextEdit()
        self.rsa_public_key_input.setPlaceholderText("Paste Public Key here (e.g., from .asc file)")
        self.rsa_public_key_input.setMinimumHeight(300)
        public_key_layout.addWidget(self.rsa_public_key_input)
        
        # Private Key
        private_key_layout = QVBoxLayout()
        private_key_layout.addWidget(QLabel("Private Key (ASCII Armored):"))
        self.rsa_private_key_input = QTextEdit()
        self.rsa_private_key_input.setPlaceholderText("Paste Private Key here (e.g., from .asc file)")
        self.rsa_private_key_input.setMinimumHeight(300)
        private_key_layout.addWidget(self.rsa_private_key_input)
        
        # Digital Signature
        signature_layout = QVBoxLayout()
        signature_layout.addWidget(QLabel("Digital Signature:"))
        self.signature_input = QTextEdit()
        self.signature_input.setPlaceholderText("Paste Digital Signature here")
        self.signature_input.setMinimumHeight(300)
        signature_layout.addWidget(self.signature_input)
        
        keys_signature_layout.addLayout(public_key_layout)
        keys_signature_layout.addLayout(private_key_layout)
        keys_signature_layout.addLayout(signature_layout)
        pgp_layout.addWidget(keys_signature_frame)
        
        # ปุ่มดำเนินการ
        action_buttons_frame = QFrame()
        action_buttons_frame.setObjectName("card")
        action_buttons_layout = QVBoxLayout(action_buttons_frame)
        action_buttons_layout.setContentsMargins(5,5,5,5)
        action_buttons_layout.setSpacing(10)
        
        # ปุ่มแถวที่ 1 (Generate, Encrypt, Decrypt)
        row1_buttons_layout = QHBoxLayout()
        row1_buttons_layout.setSpacing(10)
        
        self.rsa_generate_keys_button = QPushButton("✨ Generate Key Pair")
        self.rsa_generate_keys_button.setObjectName("generateKeyButton")
        self.rsa_generate_keys_button.clicked.connect(self.generate_rsa_keys)
        self.rsa_generate_keys_button.setMinimumHeight(40)
        
        self.rsa_encrypt_button = QPushButton("🔒 Encrypt PGP")
        self.rsa_encrypt_button.setObjectName("encryptButton")
        self.rsa_encrypt_button.clicked.connect(self.rsa_encrypt)
        self.rsa_encrypt_button.setMinimumHeight(40)
        
        self.rsa_decrypt_button = QPushButton("🔓 Decrypt PGP")
        self.rsa_decrypt_button.setObjectName("decryptButton")
        self.rsa_decrypt_button.clicked.connect(self.rsa_decrypt)
        self.rsa_decrypt_button.setMinimumHeight(40)
        
        row1_buttons_layout.addStretch()
        row1_buttons_layout.addWidget(self.rsa_generate_keys_button)
        row1_buttons_layout.addWidget(self.rsa_encrypt_button)
        row1_buttons_layout.addWidget(self.rsa_decrypt_button)
        row1_buttons_layout.addStretch()
        
        action_buttons_layout.addLayout(row1_buttons_layout)
        
        # ปุ่มแถวที่ 2 (Sign, Verify)
        row2_buttons_layout = QHBoxLayout()
        row2_buttons_layout.setSpacing(10)
        
        self.rsa_sign_button = QPushButton("✍️ Sign Message/File")
        self.rsa_sign_button.setObjectName("signButton")
        self.rsa_sign_button.clicked.connect(self.sign_message_or_file)
        self.rsa_sign_button.setMinimumHeight(40)
        
        self.rsa_verify_button = QPushButton("✅ Verify Signature")
        self.rsa_verify_button.setObjectName("verifyButton")
        self.rsa_verify_button.clicked.connect(self.verify_signature)
        self.rsa_verify_button.setMinimumHeight(40)
        
        self.rsa_sign_file_button = QPushButton("✍️ Sign File")
        self.rsa_sign_file_button.setObjectName("signButton")
        self.rsa_sign_file_button.clicked.connect(self.sign_file)
        self.rsa_sign_file_button.setMinimumHeight(40)
        
        self.rsa_verify_file_button = QPushButton("✅ Verify File Signature")
        self.rsa_verify_file_button.setObjectName("verifyButton")
        self.rsa_verify_file_button.clicked.connect(self.verify_file_signature)
        self.rsa_verify_file_button.setMinimumHeight(40)
        
        row2_buttons_layout.addWidget(self.rsa_sign_button)
        row2_buttons_layout.addWidget(self.rsa_verify_button)
        row2_buttons_layout.addWidget(self.rsa_sign_file_button)
        row2_buttons_layout.addWidget(self.rsa_verify_file_button)
        
        action_buttons_layout.addLayout(row2_buttons_layout)
        
        # ปุ่มแถวที่ 3 (List, Import, Export Keys)
        row3_buttons_layout = QHBoxLayout()
        row3_buttons_layout.setSpacing(10)
        
        self.show_keys_button = QPushButton("📋 List All Keys")
        self.show_keys_button.setObjectName("listKeysButton")
        self.show_keys_button.clicked.connect(self.list_all_keys)
        self.show_keys_button.setMinimumHeight(40)
        
        self.key_import_button = QPushButton("📥 Import Key")
        self.key_import_button.setObjectName("importKeyButton")
        self.key_import_button.clicked.connect(self.import_key)
        self.key_import_button.setMinimumHeight(40)
        
        self.key_export_button = QPushButton("📤 Export Key")
        self.key_export_button.setObjectName("exportKeyButton")
        self.key_export_button.clicked.connect(self.export_key)
        self.key_export_button.setMinimumHeight(40)
        
        row3_buttons_layout.addWidget(self.show_keys_button)
        row3_buttons_layout.addWidget(self.key_import_button)
        row3_buttons_layout.addWidget(self.key_export_button)
        
        action_buttons_layout.addLayout(row3_buttons_layout)
        pgp_layout.addWidget(action_buttons_frame)
        
        pgp_group.setLayout(pgp_layout)
        scroll_content_layout.addWidget(pgp_group)
        
        # พื้นที่แสดงผลลัพธ์
        output_group = QGroupBox("📊 Process Log")
        output_layout = QVBoxLayout()
        output_layout.setSpacing(10)
        
        self.rsa_result_output = QTextEdit()
        self.rsa_result_output.setReadOnly(True)
        self.rsa_result_output.setPlaceholderText("PGP operation results and logs will appear here...")
        self.rsa_result_output.setMinimumHeight(180)
        
        output_layout.addWidget(self.rsa_result_output)
        output_group.setLayout(output_layout)
        scroll_content_layout.addWidget(output_group)
        
        scroll_area.setWidget(scroll_content_widget)
        main_layout.addWidget(scroll_area)
        self.setLayout(main_layout)

    def generate_rsa_keys(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("✨ Generate RSA Key Pair")
        dialog.setStyleSheet(self.styleSheet())
        form_layout = QFormLayout(dialog)
        name_email_input = QLineEdit(dialog)
        name_email_input.setPlaceholderText("e.g., your_email@example.com")
        name_real_input = QLineEdit(dialog)
        name_real_input.setPlaceholderText("e.g., Your Name")
        passphrase_input = QLineEdit(dialog)
        passphrase_input.setEchoMode(QLineEdit.Password)
        passphrase_input.setPlaceholderText("Enter a strong passphrase")
        expire_date_input = QComboBox(dialog)
        expire_date_input.addItems([ "1w", "1m", "3m", "1y", "2y"])
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, dialog)
        form_layout.addRow("Email:", name_email_input)
        form_layout.addRow("Real Name:", name_real_input)
        form_layout.addRow("Passphrase:", passphrase_input)
        form_layout.addRow("Expiry:", expire_date_input)
        form_layout.addWidget(button_box)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        
        if dialog.exec_() == QDialog.Accepted:
            name_email = name_email_input.text().strip()
            name_real = name_real_input.text().strip()
            passphrase = passphrase_input.text().strip()
            expire_date = expire_date_input.currentText()
            
            if not name_email or not name_real or not passphrase:
                QMessageBox.warning(self, "Input Error", "Email, Name, and Passphrase cannot be empty.")
                return
            try:
                input_data = self.gpg_instance.gen_key_input(
                    name_email=name_email,
                    name_real=name_real,
                    passphrase=passphrase,
                    key_type="RSA",
                    key_length=2048,
                    expire_date=expire_date
                )
                key = self.gpg_instance.gen_key(input_data)
                if not key.fingerprint:
                    raise Exception("Key generation failed. Check GPG setup or input.")
                
                fingerprint = key.fingerprint
                
                key_dir = "key"
                if not os.path.exists(key_dir):
                    os.makedirs(key_dir)
                public_key = self.gpg_instance.export_keys(fingerprint)
                private_key = self.gpg_instance.export_keys(fingerprint, secret=True, passphrase=passphrase)
                with open(os.path.join(key_dir, "public_key.asc"), "w") as pub_file:
                    pub_file.write(public_key)
                with open(os.path.join(key_dir, "private_key.asc"), "w") as priv_file:
                    priv_file.write(private_key)
                self.rsa_public_key_input.setPlainText(public_key)
                self.rsa_private_key_input.setPlainText(private_key)
                
                self.rsa_result_output.append(f"<span style='color: #00ff88;'>✅ Key pair generated successfully!</span>")
            except Exception as e:
                self.rsa_result_output.append(f"<span style='color: #ff4444;'>❌ Error generating keys: {str(e)}</span>")
                QMessageBox.critical(self, "Error", f"Failed to generate keys: {str(e)}")

    def rsa_encrypt(self):
        message = self.rsa_message_input.text().strip()
        public_key_text = self.rsa_public_key_input.toPlainText().strip()
        if not message:
            QMessageBox.warning(self, "Input Error", "Please enter a message to encrypt.")
            return
        if not public_key_text:
            QMessageBox.warning(self, "Input Error", "Please paste the Public Key for encryption.")
            return
        try:
            imported = self.gpg_instance.import_keys(public_key_text)
            if not imported.fingerprints:
                raise Exception("Could not import Public Key. Please ensure it's a valid PGP public key.")
            recipient_fingerprint = imported.fingerprints[0]
            encrypted_data = self.gpg_instance.encrypt(message, recipients=[recipient_fingerprint], always_trust=True)
            if encrypted_data.ok:
                self.rsa_result_output.append(f"<span style='color: #00ff88;'>✅ PGP Encrypted Message:</span>")
                self.rsa_result_output.append(f"<pre style='color:#00d4ff;'>{str(encrypted_data)}</pre>")
            else:
                raise Exception(encrypted_data.status)
        except Exception as e:
            self.rsa_result_output.append(f"<span style='color: #ff4444;'>❌ Error encrypting: {str(e)}</span>")
            QMessageBox.critical(self, "Error", f"Failed to encrypt: {str(e)}")

    def rsa_decrypt(self):
        encrypted_text = self.rsa_message_input.text().strip()
        private_key_text = self.rsa_private_key_input.toPlainText().strip()
        if not encrypted_text:
            QMessageBox.warning(self, "Input Error", "Please enter the encrypted message.")
            return
        try:
            if private_key_text:
                imported = self.gpg_instance.import_keys(private_key_text)
                if not imported.fingerprints:
                    QMessageBox.warning(self, "Key Import Error", "Could not import Private Key. Decryption might fail.")
            passphrase, ok = QInputDialog.getText(self, 'Passphrase', 'Please enter passphrase for private key:', QLineEdit.Password)
            if not ok:
                return
            decrypted_data = self.gpg_instance.decrypt(encrypted_text, passphrase=passphrase)
            if decrypted_data.ok:
                self.rsa_result_output.append(f"<span style='color: #00ff88;'>✅ PGP Decrypted Message:</span>")
                self.rsa_result_output.append(f"<pre style='color:#ffffff;'>{decrypted_data.data.decode('utf-8', errors='replace')}</pre>")
            else:
                raise Exception(decrypted_data.status)
        except Exception as e:
            self.rsa_result_output.append(f"<span style='color: #ff4444;'>❌ Error decrypting: {str(e)}</span>")
            QMessageBox.critical(self, "Error", f"Failed to decrypt: {str(e)}")



       
            
            
    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select File to Sign", "", "All Files (*.*)"
        )
        if file_path:
            self.file_path_input.setText(file_path)
            try:
                with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read(200)
                    self.rsa_message_input.setText(f"File: {os.path.basename(file_path)}\n{content[:150]}...")
            except Exception as e:
                self.rsa_message_input.setText(f"File: {os.path.basename(file_path)} (Binary file)")
    
    
    
    def sign_message_or_file(self):
        message = self.rsa_message_input.text().strip()
        file_path = self.file_path_input.text().strip()
        private_key_text = self.rsa_private_key_input.toPlainText().strip()
        
        if not message and not file_path:
            QMessageBox.warning(self, "Input Error", "Please enter a message or select a file to sign.")
            return
        if not private_key_text:
            QMessageBox.warning(self, "Input Error", "Please paste the Private Key for signing.")
            return

        try:
            imported = self.gpg_instance.import_keys(private_key_text)
            if not imported.fingerprints:
                raise Exception("Could not import Private Key. Please ensure it's a valid PGP private key.")
            
            signing_fingerprint = imported.fingerprints[0]
            passphrase, ok = QInputDialog.getText(
                self, 'Passphrase', 
                'Please enter passphrase for signing key:', 
                QLineEdit.Password
            )
            if not ok:
                return

            if file_path:  # ลงลายเซ็นไฟล์
                with open(file_path, 'rb') as f:
                    signed_data = self.gpg_instance.sign_file(
                        f, 
                        passphrase=passphrase, 
                        keyid=signing_fingerprint,  
                        detach=True
                    )
                # ตรวจสอบผลลัพธ์ด้วย .status
                if hasattr(signed_data, 'status') and signed_data.status == "signature created":
                    signature_path = file_path + ".sig"
                    with open(signature_path, 'wb') as sig_file:
                        sig_file.write(signed_data.data)
                    self.signature_input.setPlainText(str(signed_data))
                    self.rsa_result_output.append(
                        f"<span style='color: #00ff88;'>✅ File signed successfully! Signature saved to: {signature_path}</span>"
                    )
                else:
                    error_msg = signed_data.status if hasattr(signed_data, 'status') else "Unknown error"
                    raise Exception(f"Signing failed: {error_msg}")
            else:  # ลงลายเซ็นข้อความ
                signed_data = self.gpg_instance.sign(
                    message, 
                    passphrase=passphrase, 
                    keyid=signing_fingerprint, 
                    detach=True
                )
                if hasattr(signed_data, 'status') and signed_data.status == "signature created":
                    self.signature_input.setPlainText(str(signed_data))
                    self.rsa_result_output.append(
                        "<span style='color: #00ff88;'>✅ Message signed successfully!</span>"
                    )
                else:
                    error_msg = signed_data.status if hasattr(signed_data, 'status') else "Unknown error"
                    raise Exception(f"Signing failed: {error_msg}")
                    
        except Exception as e:
            self.rsa_result_output.append(
                f"<span style='color: #ff4444;'>❌ Error signing: {str(e)}</span>"
            )
            QMessageBox.critical(self, "Error", f"Failed to sign: {str(e)}") 
    
    
    def sign_file(self):
        file_path = self.file_path_input.text().strip()
        private_key_text = self.rsa_private_key_input.toPlainText().strip()
        
        if not file_path:
            QMessageBox.warning(self, "Input Error", "Please select a file to sign.")
            return
        if not private_key_text:
            QMessageBox.warning(self, "Input Error", "Please paste the Private Key for signing.")
            return

        try:
            imported = self.gpg_instance.import_keys(private_key_text)
            if not imported.fingerprints:
                raise Exception("Could not import Private Key. Please ensure it's a valid PGP private key.")
            
            signing_fingerprint = imported.fingerprints[0]
            passphrase, ok = QInputDialog.getText(
                self, 'Passphrase', 
                'Please enter passphrase for signing key:', 
                QLineEdit.Password
            )
            if not ok:
                return

            with open(file_path, 'rb') as f:
                signed_data = self.gpg_instance.sign_file(
                    f, 
                    passphrase=passphrase, 
                    keyid=signing_fingerprint, 
                    detach=True
                )

            # ตรวจสอบผลลัพธ์ด้วย .status
            if hasattr(signed_data, 'status') and signed_data.status == "signature created":
                signature_path = file_path + ".sig"
                with open(signature_path, 'wb') as sig_file:
                    sig_file.write(signed_data.data)
                self.signature_input.setPlainText(str(signed_data))
                self.rsa_result_output.append(
                    f"<span style='color: #00ff88;'>✅ File signed successfully! Signature saved to: {signature_path}</span>"
                )
            else:
                error_msg = signed_data.status if hasattr(signed_data, 'status') else "Unknown error"
                raise Exception(f"Signing failed: {error_msg}")
                
        except Exception as e:
            self.rsa_result_output.append(
                f"<span style='color: #ff4444;'>❌ Error signing file: {str(e)}</span>"
            )
            QMessageBox.critical(self, "Error", f"Failed to sign file: {str(e)}")    

    
    def verify_signature(self):
        message = self.rsa_message_input.text().strip()
        signature = self.signature_input.toPlainText().strip()
        public_key_text = self.rsa_public_key_input.toPlainText().strip()
        file_path = self.file_path_input.text().strip()
        
        if not message and not file_path:
            QMessageBox.warning(self, "Input Error", "Please enter the message or select a file.")
            return
        if not signature:
            QMessageBox.warning(self, "Input Error", "Please paste the digital signature.")
            return

        try:
            if public_key_text:
                imported = self.gpg_instance.import_keys(public_key_text)
                if not imported.fingerprints:
                    QMessageBox.warning(self, "Key Import Error", "Could not import Public Key. Verification might fail.")

            if file_path:  # ตรวจสอบลายเซ็นไฟล์
                with open(file_path, 'rb') as f:
                    file_data = f.read()
                verified = self.gpg_instance.verify_file(
                    signature.encode('utf-8'), 
                    file_data
                )
            else:  # ตรวจสอบลายเซ็นข้อความ
                verified = self.gpg_instance.verify_data(
                    signature, 
                    message.encode('utf-8')
                )

            if verified and verified.valid:
                self.rsa_result_output.append(
                    "<span style='color: #00ff88;'>✅ Signature is VALID!</span>"
                )
                self.rsa_result_output.append(
                    f"  Signed by: <span style='color:#00d4ff;'>{verified.username}</span>"
                )
                self.rsa_result_output.append(
                    f"  Key ID: <span style='color:#00d4ff;'>{verified.key_id}</span>"
                )
            else:
                self.rsa_result_output.append(
                    "<span style='color: #ff4444;'>❌ Signature is INVALID or could not be verified.</span>"
                )
                if verified and verified.status:
                    self.rsa_result_output.append(f"  Status: {verified.status}")
                    
        except Exception as e:
            self.rsa_result_output.append(
                f"<span style='color: #ff4444;'>❌ Error verifying signature: {str(e)}</span>"
            )
            QMessageBox.critical(self, "Error", f"Failed to verify signature: {str(e)}")
    
    def verify_file_signature(self):
        file_path = self.file_path_input.text().strip()
        signature_path = self.signature_input.toPlainText().strip()
        public_key_text = self.rsa_public_key_input.toPlainText().strip()
        
        if not file_path or not signature_path:
            QMessageBox.warning(self, "Input Error", "Please select a file and provide a signature file.")
            return

        try:
            if public_key_text:
                imported = self.gpg_instance.import_keys(public_key_text)
                if not imported.fingerprints:
                    QMessageBox.warning(self, "Key Import Error", "Could not import Public Key. Verification might fail.")

            with open(file_path, 'rb') as f:
                file_data = f.read()
            with open(signature_path, 'rb') as s:
                signature_data = s.read()

            verified = self.gpg_instance.verify_file(signature_data, file_data)

            if verified and verified.valid:
                self.rsa_result_output.append(
                    "<span style='color: #00ff88;'>✅ Signature is VALID!</span>"
                )
                self.rsa_result_output.append(
                    f"  Signed by: <span style='color:#00d4ff;'>{verified.username}</span>"
                )
                self.rsa_result_output.append(
                    f"  Key ID: <span style='color:#00d4ff;'>{verified.key_id}</span>"
                )
            else:
                self.rsa_result_output.append(
                    "<span style='color: #ff4444;'>❌ Signature is INVALID or could not be verified.</span>"
                )
                
        except Exception as e:
            self.rsa_result_output.append(
                f"<span style='color: #ff4444;'>❌ Error verifying file signature: {str(e)}</span>"
            )
            QMessageBox.critical(self, "Error", f"Failed to verify file signature: {str(e)}")            
            
            
            

    def list_all_keys(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("🔑 PGP Keyring")
        dialog.setMinimumSize(700, 500)
        dialog.setStyleSheet(self.styleSheet())
        main_layout = QVBoxLayout(dialog)
        text_browser = QTextBrowser(dialog)
        text_browser.setOpenExternalLinks(False)
        text_browser.setHtml("<p style='text-align:center;color:#888;'>Loading keys...</p>")
        main_layout.addWidget(text_browser)
        dialog_buttons_layout = QHBoxLayout()
        btn_delete_all = QPushButton("⚠️ Delete All Keys")
        btn_delete_all.setObjectName("deleteKeyButton")
        btn_delete_all.clicked.connect(lambda: delete_all_keys())
        btn_close = QPushButton("Close")
        btn_close.clicked.connect(dialog.accept)
        dialog_buttons_layout.addStretch()
        dialog_buttons_layout.addWidget(btn_delete_all)
        dialog_buttons_layout.addWidget(btn_close)
        dialog_buttons_layout.addStretch()
        main_layout.addLayout(dialog_buttons_layout)
        
        gpg = self.gpg_instance
        
        def update_text_browser():
            text_browser.clear()
            public_keys = gpg.list_keys()
            private_keys = gpg.list_keys(secret=True)
            key_map = {}
            for key in public_keys:
                fp = key['fingerprint']
                key_map[fp] = {
                    "uids": key['uids'],
                    "date": key['date'],
                    "expires": key.get('expires'),
                    "public": True,
                    "private": False
                }
            for key in private_keys:
                fp = key['fingerprint']
                if fp in key_map:
                    key_map[fp]['private'] = True
                else:
                    key_map[fp] = {
                        "uids": key['uids'],
                        "date": key['date'],
                        "expires": key.get('expires'),
                        "public": False,
                        "private": True
                    }
            if not key_map:
                text_browser.append("<p style='text-align:center;color:#ff4444;'>❌ No keys found in keyring.</p>")
                return
            
            for fp, info in key_map.items():
                uids = ', '.join(info["uids"]) if info["uids"] else "N/A"
                created = datetime.datetime.utcfromtimestamp(int(info["date"])).strftime('%Y-%m-%d %H:%M:%S UTC')
                exp_str = "No Expiry"
                if info["expires"]:
                    exp_dt = datetime.datetime.utcfromtimestamp(int(info["expires"]))
                    now = datetime.datetime.now()
                    delta = exp_dt - now
                    days_left = delta.days
                    if days_left < 0:
                        exp_str = f"<span style='color:#ff4444;font-weight:bold;'>Expired on {exp_dt.strftime('%Y-%m-%d')}</span>"
                    else:
                        exp_str = f"{exp_dt.strftime('%Y-%m-%d')} (Expires in {days_left} days)"
                key_type_str = []
                if info['public']: key_type_str.append("Public")
                if info['private']: key_type_str.append("Private")
                key_type_display = " & ".join(key_type_str) if key_type_str else "Unknown"
                key_html = f"""
    <div style="margin-bottom: 10px; padding: 12px; border: 1px solid #00d4ff; border-radius: 8px; background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #3a3a54, stop:1 #2a2a3e);">
        <b style='color:#00d4ff;'>Fingerprint:</b> <span style='color:#ffffff;'>{fp}</span><br>
        <b style='color:#00d4ff;'>User:</b> <span style='color:#ffffff;'>{uids}</span><br>
        <b style='color:#00d4ff;'>Created:</b> <span style='color:#ffffff;'>{created}</span><br>
        <b style='color:#00d4ff;'>Expires:</b> {exp_str}<br>
        <b style='color:#00d4ff;'>Type:</b> <span style='color:#ffffff;'>{key_type_display}</span><br><br>
        <a href="delete:{fp}" style="background: #dc3545; color: white; padding: 6px 10px; border-radius: 6px; font-size: 11px; font-weight: bold; text-decoration: none;">🗑 Delete Key</a>
    </div>
    """
                text_browser.append(key_html)
        
        def delete_key(fingerprint):
            confirm = QMessageBox.question(
                dialog,
                "⚠️ Confirm Deletion",
                f"Are you sure you want to delete this key?\nFingerprint: {fingerprint}\nThis action cannot be undone!",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if confirm == QMessageBox.Yes:
                try:
                    if gpg.delete_keys(fingerprint, secret=True, expect_passphrase=False) and gpg.delete_keys(fingerprint):
                        QMessageBox.information(dialog, "Success", f"Key deleted successfully: {fingerprint}")
                        update_text_browser()
                    else:
                        raise Exception(f"Failed to delete key.\nPrivate: {gpg.delete_keys(fingerprint, secret=True, expect_passphrase=False).status}\nPublic: {gpg.delete_keys(fingerprint).status}")
                except Exception as e:
                    QMessageBox.critical(dialog, "Error", f"Could not delete key:\n{str(e)}")
        
        def handle_anchor_click(url):
            url_str = url.toString()
            if url_str.startswith("delete:"):
                fp = url_str[len("delete:"):]
                delete_key(fp)
        
        def delete_all_keys():
            confirm = QMessageBox.question(
                dialog,
                "⚠️ Confirm Delete All",
                "Are you absolutely sure you want to delete ALL keys?\nThis action cannot be undone!",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if confirm == QMessageBox.Yes:
                try:
                    public_fps = [key['fingerprint'] for key in gpg.list_keys()]
                    private_fps = [key['fingerprint'] for key in gpg.list_keys(secret=True)]
                    for fp in set(public_fps + private_fps):
                        gpg.delete_keys(fp, secret=True, expect_passphrase=False)
                        gpg.delete_keys(fp)
                    QMessageBox.information(dialog, "Success", "All keys deleted successfully.")
                    update_text_browser()
                except Exception as e:
                    QMessageBox.critical(dialog, "Error", f"Could not delete all keys:\n{str(e)}")
        
        text_browser.anchorClicked.connect(handle_anchor_click)
        update_text_browser()
        dialog.exec_()
    
    def import_key(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Key File to Import", "", "Key Files (*.asc *.gpg);;All Files (*.*)")
        if file_path:
            try:
                with open(file_path, "r") as f:
                    key_data = f.read()
                result = self.gpg_instance.import_keys(key_data)
                if result.ok:
                    self.rsa_result_output.append(f"<span style='color: #00ff88;'>✅ Imported {result.count} key(s).</span>")
                    for fp in result.fingerprints:
                        self.rsa_result_output.append(f"  - Fingerprint: <span style='color:#00d4ff;'>{fp}</span>")
                else:
                    raise Exception(result.status)
            except Exception as e:
                self.rsa_result_output.append(f"<span style='color: #ff4444;'>❌ Error importing key: {str(e)}</span>")
                QMessageBox.critical(self, "Error", f"Failed to import key: {str(e)}")
    
    def export_key(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("📤 Export PGP Key")
        dialog.setStyleSheet(self.styleSheet())
        layout = QVBoxLayout(dialog)
        key_list_combo = QComboBox()
        keys = self.gpg_instance.list_keys()
        if not keys:
            QMessageBox.warning(self, "No Keys", "No keys found in your keyring to export.")
            dialog.close()
            return
        for key in keys:
            uid = key['uids'][0] if key['uids'] else "No User ID"
            key_list_combo.addItem(f"{uid} - {key['fingerprint']}")
        layout.addWidget(QLabel("Select key to export:"))
        layout.addWidget(key_list_combo)
        save_public_btn = QPushButton("💾 Save Public Key")
        save_public_btn.setObjectName("exportKeyButton")
        save_public_btn.clicked.connect(lambda: self.save_exported_key(dialog, key_list_combo.currentText(), secret=False))
        layout.addWidget(save_public_btn)
        save_private_btn = QPushButton("💾 Save Private Key")
        save_private_btn.setObjectName("exportKeyButton")
        save_private_btn.clicked.connect(lambda: self.save_exported_key(dialog, key_list_combo.currentText(), secret=True))
        layout.addWidget(save_private_btn)
        dialog.exec_()
    
    def save_exported_key(self, dialog, item_text, secret=False):
        fingerprint = item_text.split("-")[-1].strip()
        try:
            if secret:
                passphrase, ok = QInputDialog.getText(dialog, 'Passphrase', 'Please enter passphrase for private key:', QLineEdit.Password)
                if not ok: return
                exported_key_data = self.gpg_instance.export_keys(fingerprint, secret=True, passphrase=passphrase)
                default_filename = f"private_key_{fingerprint[:8]}.asc"
            else:
                exported_key_data = self.gpg_instance.export_keys(fingerprint)
                default_filename = f"public_key_{fingerprint[:8]}.asc"
            if not exported_key_data:
                raise Exception("Failed to export key. Key might not exist or passphrase was incorrect.")
            file_path, _ = QFileDialog.getSaveFileName(dialog, "Save Key", default_filename, "Key Files (*.asc);;All Files (*.*)")
            if file_path:
                with open(file_path, "w") as f:
                    f.write(str(exported_key_data))
                QMessageBox.information(dialog, "Success", f"Key saved successfully to: {os.path.basename(file_path)}")
                self.rsa_result_output.append(f"<span style='color: #00ff88;'>✅ Key exported: <font color='#00d4ff'>{os.path.basename(file_path)}</font></span>")
            else:
                self.rsa_result_output.append("<span style='color: #ff4444;'>❌ Key export cancelled.</span>")
        except Exception as e:
            self.rsa_result_output.append(f"<span style='color: #ff4444;'>❌ Error exporting key: {str(e)}</span>")
            QMessageBox.critical(dialog, "Error", f"Failed to export key: {str(e)}")            
            
            
            
    def sign_message(self):
        """ลงลายเซ็นข้อความ"""
        message = self.rsa_message_input.text().strip()
        private_key_text = self.rsa_private_key_input.toPlainText().strip()
        
        if not message:
            QMessageBox.warning(self, "Input Error", "Please enter a message to sign.")
            return
        if not private_key_text:
            QMessageBox.warning(self, "Input Error", "Please paste the Private Key for signing.")
            return

        try:
            # นำเข้า Private Key
            imported = self.gpg_instance.import_keys(private_key_text)
            if not imported.fingerprints:
                raise Exception("Could not import Private Key. Please ensure it's a valid PGP private key.")
            
            signing_fingerprint = imported.fingerprints[0]
            # รับ Passphrase
            passphrase, ok = QInputDialog.getText(
                self, 'Passphrase', 
                'Please enter passphrase for signing key:', 
                QLineEdit.Password
            )
            if not ok:
                return

            # ลงลายเซ็นข้อความ
            signed_data = self.gpg_instance.sign(
                message,  # ไม่ต้อง encode
                passphrase=passphrase, 
                keyid=signing_fingerprint, 
                detach=True
            )
            
            # ตรวจสอบผลลัพธ์
            if hasattr(signed_data, 'status') and signed_data.status == "signature created":
                self.signature_input.setPlainText(str(signed_data))
                self.rsa_result_output.append(
                    "<span style='color: #00ff88;'>✅ Message signed successfully!</span>"
                )
            else:
                error_msg = signed_data.status if hasattr(signed_data, 'status') else "Unknown error"
                raise Exception(f"Signing failed: {error_msg}")
                
        except Exception as e:
            self.rsa_result_output.append(
                f"<span style='color: #ff4444;'>❌ Error signing message: {str(e)}</span>"
            )
            QMessageBox.critical(self, "Error", f"Failed to sign message: {str(e)}")
            
            

    
    
    def sign_file(self):
        """ลงลายเซ็นไฟล์"""
        file_path = self.file_path_input.text().strip()
        private_key_text = self.rsa_private_key_input.toPlainText().strip()
        
        if not file_path:
            QMessageBox.warning(self, "Input Error", "Please select a file to sign.")
            return
        if not private_key_text:
            QMessageBox.warning(self, "Input Error", "Please paste the Private Key for signing.")
            return

        try:
            # นำเข้า Private Key
            imported = self.gpg_instance.import_keys(private_key_text)
            if not imported.fingerprints:
                raise Exception("Could not import Private Key. Please ensure it's a valid PGP private key.")
            
            signing_fingerprint = imported.fingerprints[0]
            # รับ Passphrase
            passphrase, ok = QInputDialog.getText(
                self, 'Passphrase', 
                'Please enter passphrase for signing key:', 
                QLineEdit.Password
            )
            if not ok:
                return

            # ลงลายเซ็นไฟล์
            with open(file_path, 'rb') as f:
                signed_data = self.gpg_instance.sign_file(
                    f, 
                    passphrase=passphrase, 
                    keyid=signing_fingerprint, 
                    detach=True
                )
            
            # ตรวจสอบผลลัพธ์
            if hasattr(signed_data, 'status') and signed_data.status == "signature created":
                signature_path = file_path + ".sig"
                with open(signature_path, 'wb') as sig_file:
                    sig_file.write(signed_data.data)
                self.signature_input.setPlainText(str(signed_data))
                self.rsa_result_output.append(
                    f"<span style='color: #00ff88;'>✅ File signed successfully! Signature saved to: {signature_path}</span>"
                )
            else:
                error_msg = signed_data.status if hasattr(signed_data, 'status') else "Unknown error"
                raise Exception(f"Signing failed: {error_msg}")
                
        except Exception as e:
            self.rsa_result_output.append(
                f"<span style='color: #ff4444;'>❌ Error signing file: {str(e)}</span>"
            )
            QMessageBox.critical(self, "Error", f"Failed to sign file: {str(e)}")
    


    def verify_message_signature(self):
        """ตรวจสอบลายเซ็นข้อความ"""
        message = self.rsa_message_input.text().strip()
        signature = self.signature_input.toPlainText().strip()
        public_key_text = self.rsa_public_key_input.toPlainText().strip()

        if not message or not signature:
            QMessageBox.warning(self, "Input Error", "Please enter the message and signature.")
            return

        try:
            # นำเข้า Public Key หากมี
            if public_key_text:
                self.gpg_instance.import_keys(public_key_text)

            # ตรวจสอบว่า message เป็นข้อความอ่านได้
            try:
                message_bytes = message.encode('utf-8')
            except UnicodeEncodeError:
                message_bytes = message.encode('latin-1')  # ถ้าไม่ใช่ UTF-8

            # ลายเซ็นเป็น ASCII-armored ไม่ควรใช้ encode
            signature_bytes = signature.encode('utf-8')  # ใช้ได้ในกรณีนี้ แต่ควรระวัง

            # ตรวจสอบลายเซ็น
            verified = self.gpg_instance.verify_data(signature_bytes, message_bytes)

            # ตรวจสอบ .valid แทนแค่ .status
            if verified and getattr(verified, 'valid', False):
                self.rsa_result_output.append(
                    "<span style='color: #00ff88;'>✅ Signature is VALID!</span>"
                )
                if hasattr(verified, 'username'):
                    self.rsa_result_output.append(
                        f"Signed by: <span style='color:#00d4ff;'>{verified.username}</span>"
                    )
                if hasattr(verified, 'key_id'):
                    self.rsa_result_output.append(
                        f"Key ID: <span style='color:#00d4ff;'>{verified.key_id}</span>"
                    )
            else:
                self.rsa_result_output.append(
                    "<span style='color: #ff4444;'>❌ Signature is INVALID or could not be verified.</span>"
                )
                if hasattr(verified, 'status'):
                    self.rsa_result_output.append(f"Status: {verified.status}")

        except Exception as e:
            self.rsa_result_output.append(
                f"<span style='color: #ff4444;'>❌ Error verifying signature: {str(e)}</span>"
            )
            QMessageBox.critical(self, "Error", f"Failed to verify signature: {str(e)}")
    
    
    def verify_file_signature(self):
        """ตรวจสอบลายเซ็นไฟล์"""
        file_path = self.file_path_input.text().strip()
        signature_path, _ = QFileDialog.getOpenFileName(
            self, "Select Signature File", "", "Signature Files (*.sig);;All Files (*.*)"
        )

        if not file_path or not signature_path:
            QMessageBox.warning(self, "Input Error", "Please select a file and signature file.")
            return

        try:
            # อ่านไฟล์และลายเซ็นแบบ binary
            with open(file_path, 'rb') as f:
                file_data = f.read()
            with open(signature_path, 'rb') as s:
                signature_data = s.read()

            # ตรวจสอบลายเซ็น
            verified = self.gpg_instance.verify_file(signature_data, file_data)

            # ตรวจสอบ .valid แทนแค่ .status
            if verified and getattr(verified, 'valid', False):
                self.rsa_result_output.append(
                    "<span style='color: #00ff88;'>✅ Signature is VALID!</span>"
                )
                if hasattr(verified, 'username'):
                    self.rsa_result_output.append(
                        f"Signed by: <span style='color:#00d4ff;'>{verified.username}</span>"
                    )
                if hasattr(verified, 'key_id'):
                    self.rsa_result_output.append(
                        f"Key ID: <span style='color:#00d4ff;'>{verified.key_id}</span>"
                    )
            else:
                self.rsa_result_output.append(
                    "<span style='color: #ff4444;'>❌ Signature is INVALID or could not be verified.</span>"
                )
                if hasattr(verified, 'status'):
                    self.rsa_result_output.append(f"Status: {verified.status}")

        except Exception as e:
            self.rsa_result_output.append(
                f"<span style='color: #ff4444;'>❌ Error verifying file signature: {str(e)}</span>"
            )
            QMessageBox.critical(self, "Error", f"Failed to verify file signature: {str(e)}")
    
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
            