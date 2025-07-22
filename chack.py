from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QPushButton, 
    QTextEdit, QLabel, QFileDialog, QMessageBox, QApplication
)
from PyQt5.QtCore import Qt
import sys

from tabs.integrated_mode_tab import SpecialSteganographyModes

class SteganographyUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('Enhanced Steganography and Encryption App')
        main_layout = QVBoxLayout()
        
        # สร้าง Tab Widget
        tabs = QTabWidget()
        
        # สร้างแท็บต่างๆ
        self.tab1 = self.createHideTab()
        self.tab2 = self.createExtractTab()
        
        # เพิ่มแท็บ
        tabs.addTab(self.tab1, "การซ่อนข้อความ")
        tabs.addTab(self.tab2, "การถอดข้อความ")
        
        main_layout.addWidget(tabs)
        self.setLayout(main_layout)

    def createHideTab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        # ส่วนบนสำหรับข้อความที่จะซ่อน
        input_label = QLabel("ข้อความที่ต้องการซ่อน:")
        self.message_input = QTextEdit()
        self.message_input.setPlaceholderText("พิมพ์ข้อความที่ต้องการซ่อน...")
        self.message_input.setMaximumHeight(150)
        
        # ส่วนกลางสำหรับแสดงไฟล์ที่เลือก
        files_label = QLabel("รายการไฟล์ที่เลือก:")
        self.files_display = QTextEdit()
        self.files_display.setReadOnly(True)
        self.files_display.setMaximumHeight(100)
        self.files_display.setPlaceholderText("ยังไม่ได้เลือกไฟล์...")
        
        # ปุ่มเลือกไฟล์
        select_file_btn = QPushButton("เลือกไฟล์")
        select_file_btn.clicked.connect(self.selectFiles)
        
        # ปุ่มเริ่มการซ่อนข้อมูล
        hide_btn = QPushButton("ซ่อนข้อความ")
        hide_btn.clicked.connect(self.hideData)
        hide_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 8px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)

        # เพิ่ม widgets เข้า layout
        layout.addWidget(input_label)
        layout.addWidget(self.message_input)
        layout.addWidget(files_label)
        layout.addWidget(self.files_display)
        layout.addWidget(select_file_btn)
        layout.addWidget(hide_btn)
        layout.addStretch()
        
        tab.setLayout(layout)
        return tab

    def createExtractTab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        # ส่วนแสดงไฟล์ที่เลือก
        files_label = QLabel("ไฟล์ที่ต้องการถอดข้อความ:")
        self.extract_files_display = QTextEdit()
        self.extract_files_display.setReadOnly(True)
        self.extract_files_display.setMaximumHeight(100)
        self.extract_files_display.setPlaceholderText("ยังไม่ได้เลือกไฟล์...")
        
        # ปุ่มเลือกไฟล์
        select_file_btn = QPushButton("เลือกไฟล์")
        select_file_btn.clicked.connect(self.selectExtractFiles)
        
        # ส่วนแสดงผลลัพธ์
        result_label = QLabel("ข้อความที่ถอดได้:")
        self.result_display = QTextEdit()
        self.result_display.setReadOnly(True)
        self.result_display.setPlaceholderText("ผลลัพธ์จะแสดงที่นี่...")
        
        # ปุ่มถอดข้อความ
        extract_btn = QPushButton("ถอดข้อความ")
        extract_btn.clicked.connect(self.extractData)
        extract_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #388E3C;
            }
        """)

        # เพิ่ม widgets เข้า layout
        layout.addWidget(files_label)
        layout.addWidget(self.extract_files_display)
        layout.addWidget(select_file_btn)
        layout.addWidget(result_label)
        layout.addWidget(self.result_display)
        layout.addWidget(extract_btn)
        layout.addStretch()
        
        tab.setLayout(layout)
        return tab

    def selectFiles(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "เลือกไฟล์",
            "",
            "All Files (*.png *.jpg *.wav *.docx)"
        )
        if files:
            self.files_display.setText("\n".join(files))

    def selectExtractFiles(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "เลือกไฟล์",
            "",
            "All Files (*.png *.jpg *.wav *.docx)"
        )
        if files:
            self.extract_files_display.setText("\n".join(files))

    def hideData(self):
        message = self.message_input.toPlainText()
        files = self.files_display.toPlainText().split('\n')
        
        if not message:
            QMessageBox.warning(self, "คำเตือน", "กรุณาใส่ข้อความที่ต้องการซ่อน")
            return
            
        if not files or files[0] == "":
            QMessageBox.warning(self, "คำเตือน", "กรุณาเลือกไฟล์")
            return
            
        try:
            # เรียกใช้ฟังก์ชันซ่อนข้อมูลที่เหมาะสมตามจำนวนไฟล์
            if len(files) == 3:
                output_files = SpecialSteganographyModes.split_message_to_images(message, files)
                QMessageBox.information(self, "สำเร็จ", f"ซ่อนข้อความเรียบร้อยแล้ว\nไฟล์ผลลัพธ์: {', '.join(output_files)}")
            else:
                QMessageBox.warning(self, "คำเตือน", "กรุณาเลือกไฟล์ให้ถูกต้องตามโหมดที่เลือก")
        except Exception as e:
            QMessageBox.critical(self, "ข้อผิดพลาด", str(e))

    def extractData(self):
        files = self.extract_files_display.toPlainText().split('\n')
        
        if not files or files[0] == "":
            QMessageBox.warning(self, "คำเตือน", "กรุณาเลือกไฟล์")
            return
            
        try:
            # เรียกใช้ฟังก์ชันถอดข้อความที่เหมาะสมตามจำนวนไฟล์
            if len(files) == 3:
                message = SpecialSteganographyModes.extract_message_from_images(files)
                self.result_display.setText(message)
            else:
                QMessageBox.warning(self, "คำเตือน", "กรุณาเลือกไฟล์ให้ถูกต้องตามโหมดที่เลือก")
        except Exception as e:
            QMessageBox.critical(self, "ข้อผิดพลาด", str(e))

# สำหรับการทดสอบ
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = SteganographyUI()
    ex.show()
    sys.exit(app.exec_())