from PyQt5.QtWidgets import (
    QFileDialog, QProgressBar, QComboBox, QWidget, QVBoxLayout,
    QGroupBox, QLabel, QPushButton, QHBoxLayout, QTextEdit
)
from PyQt5.QtGui import QPixmap,QDesktopServices
from PyQt5.QtCore import Qt, QUrl, QThread, pyqtSignal
import os
import uuid
from datetime import datetime
from utils.steganography import (
    hide_message_lsb_from_steganography, retrieve_message_lsb_from_steganography,
    hide_message_masking_filtering_from_steganography, retrieve_message_masking_filtering_from_steganography,
    hide_message_palette_based_from_steganography, retrieve_message_palette_based_from_steganography,
    hide_message_edge_detection, retrieve_message_edge_detection,
    hide_message_alpha_channel, retrieve_message_alpha_channel
)
from utils.check_bit import check_bit_lsb, check_bit_masking_filtering, check_bit_palette, check_bit_edge_detection, check_bit_alpha_channel


class ImageTab(QWidget):
    def __init__(self):
        super().__init__()
        self.selected_image = None
        self.num = 0
        self.previous_text_length = 0
        self.initUI()
        self.load_example_image()
        self.setAcceptDrops(True)
        self.message_input.textChanged.connect(self.check_message_length)
        self.mode_selector.currentIndexChanged.connect(self.update_num_from_mode)
        

    def initUI(self):
        layout = QVBoxLayout()

        # --- Image Handling Group ---
        image_group = QGroupBox("จัดการรูปภาพ")
        image_layout = QVBoxLayout()

        # Buttons Layout
        button_layout = QHBoxLayout()
        self.select_image_button = QPushButton("เลือกไฟล์ภาพ")
        self.select_image_button.clicked.connect(self.select_image)

        self.number_selector = QComboBox()
        self.number_selector.addItems([str(i) for i in range(1, 11)])
        self.number_selector.currentIndexChanged.connect(self.load_example_image)

        self.mode_selector = QComboBox()
        self.mode_selector.addItems([
            "LSB",
            "Masking and Filtering",
            "Palette-based Techniques",
            "Edge Detection",
            "Alpha Channel"
        ])

        pic_label = QLabel("เลือกตัวอย่างภาพจากระบบ:")
        mode_label = QLabel("เลือกโหมดการซ่อนข้อความ:")

        button_layout.addWidget(pic_label)
        button_layout.addWidget(self.number_selector)
        button_layout.addWidget(mode_label)
        button_layout.addWidget(self.mode_selector)
        button_layout.addWidget(self.select_image_button)

        # Image Preview
        self.image_label = QLabel()
        self.image_label.setFixedSize(400, 200)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("""
            QLabel {
                background-color: white;
                border: 2px dashed #BBDEFB;
                border-radius: 8px;
            }
        """)

        self.bit_info_label = QLabel("bit เหลือ: 0 (จาก 0 bit) | ใช้ไป: 0 bit")
        self.bit_info_label.setStyleSheet("color: green; font-size: 16px; font-weight: bold;")
        self.bit_info_label.setAlignment(Qt.AlignCenter)

        image_and_error_layout = QHBoxLayout()
        image_and_error_layout.addWidget(self.image_label)
        image_and_error_layout.addWidget(self.bit_info_label)

        # Message Input
        self.message_input = QTextEdit()
        self.message_input.setPlaceholderText("ข้อความที่ต้องการซ่อนในภาพ")
        self.message_input.setMinimumHeight(100)

        # Output Area
        self.result_output = QTextEdit()
        self.result_output.setReadOnly(True)
        self.result_output.setStyleSheet("background-color: #f9f9f9; font-family: Consolas;")

        message_output_layout = QHBoxLayout()
        message_output_layout.addWidget(self.message_input)
        message_output_layout.addWidget(self.result_output)

        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)

        # Action Buttons
        action_layout = QHBoxLayout()
        self.hide_button = QPushButton("ซ่อนข้อความ")
        self.hide_button.clicked.connect(self.hide_message)
        self.hide_button.setStyleSheet("background-color: purple; color: white;")

        self.extract_button = QPushButton("ถอดข้อความ")
        self.extract_button.clicked.connect(self.retrieve_message)
        self.extract_button.setStyleSheet("background-color: orange; color: white;")

        self.output_folder_button = QPushButton("เปิดโฟลเดอร์ Output")
        self.output_folder_button.clicked.connect(self.open_output_folder)
        self.output_folder_button.setStyleSheet("background-color: black; color: white;")

        action_layout.addWidget(self.hide_button)
        action_layout.addWidget(self.extract_button)
        action_layout.addWidget(self.output_folder_button)

        # Combine Layouts
        image_layout.addLayout(button_layout)
        image_layout.addLayout(image_and_error_layout)
        image_layout.addLayout(message_output_layout)
        image_layout.addWidget(self.progress_bar)
        image_layout.addLayout(action_layout)
        image_group.setLayout(image_layout)
        layout.addWidget(image_group)

        self.setLayout(layout)




    def load_image_to_ui(self, image_path):
        if os.path.exists(image_path):
            self.selected_image = image_path
            pixmap = QPixmap(image_path).scaled(400, 200, Qt.KeepAspectRatio)
            self.image_label.setPixmap(pixmap)
            self.result_output.append(f"โหลดภาพ: {image_path}")
            self.update_num_from_mode()
        else:
            self.result_output.append("<font color='red'>ไม่พบไฟล์ภาพ</font>")

    def select_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "เลือกไฟล์ภาพ", "", "Image Files (*.png *.jpg *.jpeg *.bmp)")
        if file_path:
            self.load_image_to_ui(file_path)

    def load_example_image(self):
        num = self.number_selector.currentText()
        example_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'photoexample', f'example{num}.png')
        self.load_image_to_ui(example_path)

    def open_output_folder(self):
        script_dir = os.path.dirname(__file__)
        output_path = os.path.join(script_dir, "..", "photoexample", "output")
        os.makedirs(output_path, exist_ok=True)
        QDesktopServices.openUrl(QUrl.fromLocalFile(output_path))

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                self.load_image_to_ui(file_path)
            else:
                self.result_output.append("<font color='red'>ไฟล์ที่ลากมาไม่ใช่รูปภาพ</font>")

    def check_bit_pic(self):
        mode = self.mode_selector.currentText()
        image_path = self.selected_image

        bit_checker_map = {
            "LSB": check_bit_lsb,
            "Masking and Filtering": check_bit_masking_filtering,
            "Palette-based Techniques": check_bit_palette,
            "Edge Detection": check_bit_edge_detection,
            "Alpha Channel": check_bit_alpha_channel
        }

        if mode in bit_checker_map:
            return bit_checker_map[mode](image_path)
        return 9999  

    def calculate_message_bit(self, message):
        return len(message.encode('utf-8')) * 8  # UTF-8 encoding

    def check_message_length(self):
        max_bit = self.num
        message = self.message_input.toPlainText()
        message_bit = self.calculate_message_bit(message)
        remaining_bit = max_bit - message_bit

        if remaining_bit >= 0:
            self.bit_info_label.setText(f"bit เหลือ: {remaining_bit} (จาก {max_bit} bit) | ใช้ไป: {message_bit} bit")
            self.bit_info_label.setStyleSheet("color: green; font-size: 16px; font-weight: bold;")
        else:
            self.bit_info_label.setText(f"bit เกิน: {-remaining_bit} bit | ใช้ไป: {message_bit} bit (เกิน)")
            self.bit_info_label.setStyleSheet("color: red; font-size: 16px; font-weight: bold;")

    def update_num_from_mode(self):
        self.num = self.check_bit_pic()
        self.previous_text_length = 0
        self.check_message_length()
        self.progress_bar.setValue(0)

    def hide_message(self):
        if not hasattr(self, "selected_image"):
            self.result_output.append("<font color='red'>กรุณาเลือกไฟล์ภาพ</font>")
            return

        mode = self.mode_selector.currentText()
        message = self.message_input.toPlainText()
        image = self.selected_image
        max_bit = self.check_bit_pic()
        message_bit = self.calculate_message_bit(message)

        if message_bit > max_bit:
            self.result_output.append(f"<font color='red'>ข้อความยาวเกินไป (สูงสุด {max_bit // 8} ตัวอักษร)</font>")
            return

        output_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), "photoexample", "output")
        os.makedirs(output_folder, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        unique_id = uuid.uuid4().hex[:8]
        output_path = os.path.join(output_folder, f"{timestamp}_{unique_id}.png")

        self.worker = SteganographyWorker(mode, image, message, output_path)
        self.worker.progress.connect(self.progress_bar.setValue)
        self.worker.finished.connect(lambda msg: self.result_output.append(msg))
        self.worker.start()

    def retrieve_message(self):
        if not hasattr(self, "selected_image"):
            self.result_output.append("<font color='red'>กรุณาเลือกไฟล์ภาพ</font>")
            return

        mode = self.mode_selector.currentText()
        image_path = self.selected_image

        self.retrieve_worker = RetrieveWorker(mode, image_path)
        self.retrieve_worker.progress.connect(self.progress_bar.setValue)
        self.retrieve_worker.finished.connect(lambda msg: self.result_output.append(msg))
        self.retrieve_worker.start()


# --- Thread Worker Classes ---

class SteganographyWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)

    HIDE_MAP = {
        "LSB": hide_message_lsb_from_steganography,
        "Masking and Filtering": hide_message_masking_filtering_from_steganography,
        "Palette-based Techniques": hide_message_palette_based_from_steganography,
        "Edge Detection": hide_message_edge_detection,
        "Alpha Channel": hide_message_alpha_channel
    }

    def __init__(self, mode, image, message, output_path):
        super().__init__()
        self.mode = mode
        self.image = image
        self.message = message
        self.output_path = output_path

    def run(self):
        try:
            for i in range(101):
                self.progress.emit(i)
                QThread.msleep(50)

            if self.mode in self.HIDE_MAP:
                self.HIDE_MAP[self.mode](self.image, self.message, self.output_path)
                self.finished.emit(f"ข้อความถูกซ่อนใน: {self.output_path}")
            else:
                self.finished.emit("<font color='red'>โหมดไม่รองรับ</font>")
        except Exception as e:
            self.finished.emit(f"<font color='red'>เกิดข้อผิดพลาด: {str(e)}</font>")


class RetrieveWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)

    RETRIEVE_MAP = {
        "LSB": retrieve_message_lsb_from_steganography,
        "Masking and Filtering": retrieve_message_masking_filtering_from_steganography,
        "Palette-based Techniques": retrieve_message_palette_based_from_steganography,
        "Edge Detection": retrieve_message_edge_detection,
        "Alpha Channel": retrieve_message_alpha_channel
    }

    def __init__(self, mode, image_path):
        super().__init__()
        self.mode = mode
        self.image_path = image_path

    def run(self):
        try:
            for i in range(101):
                self.progress.emit(i)
                QThread.msleep(50)

            if self.mode in self.RETRIEVE_MAP:
                result = self.RETRIEVE_MAP[self.mode](self.image_path)
                if result:
                    self.finished.emit(f"ข้อความที่ถอดได้: {result}")
                else:
                    self.finished.emit("<font color='red'>ไม่พบข้อความในภาพนี้</font>")
            else:
                self.finished.emit("<font color='red'>โหมดไม่รองรับ</font>")
        except Exception as e:
            self.finished.emit(f"<font color='red'>เกิดข้อผิดพลาด: {str(e)}</font>")