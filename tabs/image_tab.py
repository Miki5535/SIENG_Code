from PyQt5.QtWidgets import (
QFileDialog, QProgressBar, QComboBox, QWidget, QVBoxLayout,
QGroupBox, QLabel, QPushButton, QHBoxLayout, QTextEdit, QFrame,
QGridLayout, QSplitter, QScrollArea
)
from PyQt5.QtGui import QPixmap, QDesktopServices, QFont, QIcon
from PyQt5.QtCore import Qt, QUrl, QThread, pyqtSignal, QPropertyAnimation, QEasingCurve
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
from utils.check_bit import (
check_bit_lsb, check_bit_masking_filtering, check_bit_palette, 
check_bit_edge_detection, check_bit_alpha_channel
)

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
        # Apply modern dark styling (keep existing styles)
        self.setStyleSheet("""
        /* Main Widget Styling */
        QWidget {
            background: transparent;
            color: #ffffff;
            font-family: 'Segoe UI', 'Roboto', Arial, sans-serif;
        }
        
        /* Group Box Styling */
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
        
        /* Card Frame Styling */
        QFrame#card {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #3a3a54, stop:1 #2a2a3e);
            border: 1px solid #555;
            border-radius: 10px;
            padding: 12px;
            margin: 3px;
        }
        
        /* Button Styling */
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
        
        /* Special Button Colors */
        QPushButton#hideButton {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #8e24aa, stop:1 #5e35b1);
        }
        
        QPushButton#hideButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #ba68c8, stop:1 #9575cd);
        }
        
        QPushButton#extractButton {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #ff9800, stop:1 #fb8c00);
        }
        
        QPushButton#extractButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #ffb74d, stop:1 #ffa726);
        }
        
        QPushButton#folderButton {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #424242, stop:1 #616161);
        }
        
        QPushButton#folderButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #757575, stop:1 #9e9e9e);
        }
        
        /* ComboBox Styling */
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
        
        /* Text Edit Styling */
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
        
        /* Label Styling */
        QLabel {
            color: #cccccc;
            font-size: 12px;
            font-weight: bold;
            background: transparent;
        }
        
        QLabel#imagePreview {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #1e1e2e, stop:0.5 #2d2d44, stop:1 #1e1e2e);
            border: 2px dashed #00d4ff;
            border-radius: 12px;
            color: #888;
            font-size: 14px;
            font-style: italic;
        }
        
        QLabel#bitInfo {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 rgba(0, 212, 255, 0.1), stop:1 rgba(0, 212, 255, 0.05));
            border: 2px solid #00d4ff;
            border-radius: 8px;
            padding: 12px;
            font-size: 12px;
            font-weight: bold;
        }
        
        /* Progress Bar Styling */
        QProgressBar {
            background: #3c3c3c;
            border: 2px solid #555;
            border-radius: 8px;
            text-align: center;
            color: #ffffff;
            font-weight: bold;
            font-size: 11px;
            height: 20px;
        }
        
        QProgressBar::chunk {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #00d4ff, stop:1 #0099cc);
            border-radius: 6px;
            margin: 2px;
        }
        
        /* Scroll Bar Styling */
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

        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # === TOP SECTION: Image Controls ===
        control_group = QGroupBox("🖼️ Image Selection & Configuration")
        control_layout = QGridLayout()
        control_layout.setSpacing(10)

        # Row 1: Image Selection
        pic_label = QLabel("📁 Sample:")
        pic_label.setStyleSheet("color: #00d4ff; font-size: 12px;")

        self.number_selector = QComboBox()
        self.number_selector.addItems([f"Ex {i}" for i in range(1, 11)])
        self.number_selector.currentIndexChanged.connect(self.load_example_image)

        self.select_image_button = QPushButton("🔍 Browse")
        self.select_image_button.clicked.connect(self.select_image)

        # Row 2: Mode Selection
        mode_label = QLabel("⚙️ Mode:")
        mode_label.setStyleSheet("color: #00d4ff; font-size: 12px;")

        self.mode_selector = QComboBox()
        self.mode_selector.addItems([
            "🔹 LSB",
            "🎭 Masking",
            "🎨 Palette",
            "📐 Edge",
            "🔍 Alpha"
        ])

        control_layout.addWidget(pic_label, 0, 0)
        control_layout.addWidget(self.number_selector, 0, 1)
        control_layout.addWidget(self.select_image_button, 0, 2)
        control_layout.addWidget(mode_label, 1, 0)
        control_layout.addWidget(self.mode_selector, 1, 1, 1, 2)

        control_group.setLayout(control_layout)

        # === MIDDLE SECTION: Image Preview & Message I/O ===
        content_layout = QHBoxLayout()
        content_layout.setSpacing(10)

        # Left: Image Preview
        preview_frame = QFrame()
        preview_frame.setObjectName("card")
        preview_layout = QVBoxLayout()

        preview_title = QLabel("🖼️ Preview")
        preview_title.setStyleSheet("color: #00d4ff; font-size: 13px; margin-bottom: 5px;")

        self.image_label = QLabel("Drag & Drop Image\nor Use Browse Button")
        self.image_label.setObjectName("imagePreview")
        # Increased image label size
        self.image_label.setFixedSize(450, 250) 
        self.image_label.setAlignment(Qt.AlignCenter)

        # Capacity info (compact)
        self.bit_info_label = QLabel("📊 Capacity: 0 bits | Used: 0 bits")
        self.bit_info_label.setObjectName("bitInfo")
        self.bit_info_label.setAlignment(Qt.AlignCenter)
        self.bit_info_label.setMaximumHeight(60)

        preview_layout.addWidget(preview_title)
        preview_layout.addWidget(self.image_label)
        preview_layout.addWidget(self.bit_info_label)
        preview_frame.setLayout(preview_layout)

        # Right: Message Input/Output
        message_frame = QFrame()
        message_frame.setObjectName("card")
        message_layout = QVBoxLayout()

        # Input section
        input_title = QLabel("✏️ Secret Message")
        input_title.setStyleSheet("color: #00d4ff; font-size: 13px; margin-bottom: 5px;")

        self.message_input = QTextEdit()
        self.message_input.setPlaceholderText("Enter your secret message here...\n\nSupports:\n• Multi-line text\n• Unicode characters\n• Special symbols")
        # Increased minimum height for text edits
        self.message_input.setMinimumHeight(150) 

        # Output section
        output_title = QLabel("📤 Output")
        output_title.setStyleSheet("color: #00d4ff; font-size: 13px; margin-bottom: 5px; margin-top: 10px;")

        self.result_output = QTextEdit()
        self.result_output.setReadOnly(True)
        self.result_output.setPlaceholderText("Process results and extracted messages will appear here...")
        # Increased minimum height for text edits
        self.result_output.setMinimumHeight(150) 

        message_layout.addWidget(input_title)
        message_layout.addWidget(self.message_input)
        message_layout.addWidget(output_title)
        message_layout.addWidget(self.result_output)
        message_frame.setLayout(message_layout)

        # Adjusted stretch factors for message input/output
        content_layout.addWidget(preview_frame, 1) # Image preview takes 1 part
        content_layout.addWidget(message_frame, 1) # Message I/O takes 1.5 parts, making it wider

        # === BOTTOM SECTION: Progress & Actions ===
        bottom_layout = QVBoxLayout()
        bottom_layout.setSpacing(8)

        # Progress section
        progress_title = QLabel("⏳ Progress")
        progress_title.setStyleSheet("color: #00d4ff; font-size: 12px; margin-bottom: 3px;")

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)

        # Action buttons
        action_layout = QHBoxLayout()
        action_layout.setSpacing(15)

        self.hide_button = QPushButton("🔒 Hide")
        self.hide_button.setObjectName("hideButton")
        self.hide_button.clicked.connect(self.hide_message)
        self.hide_button.setMinimumHeight(40)

        self.extract_button = QPushButton("🔓 Extract")
        self.extract_button.setObjectName("extractButton")
        self.extract_button.clicked.connect(self.retrieve_message)
        self.extract_button.setMinimumHeight(40)

        self.output_folder_button = QPushButton("📁 Output")
        self.output_folder_button.setObjectName("folderButton")
        self.output_folder_button.clicked.connect(self.open_output_folder)
        self.output_folder_button.setMinimumHeight(40)

        action_layout.addStretch()
        action_layout.addWidget(self.hide_button)
        action_layout.addWidget(self.extract_button)
        action_layout.addWidget(self.output_folder_button)
        action_layout.addStretch()

        bottom_layout.addWidget(progress_title)
        bottom_layout.addWidget(self.progress_bar)
        bottom_layout.addLayout(action_layout)

        # Assemble main layout
        main_layout.addWidget(control_group)
        main_layout.addLayout(content_layout, 1) # Give content layout stretch
        main_layout.addLayout(bottom_layout)

        self.setLayout(main_layout)

    def load_image_to_ui(self, image_path):
        if os.path.exists(image_path):
            self.selected_image = image_path
            # Scaled to match the new fixed size
            pixmap = QPixmap(image_path).scaled(450, 250, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.image_label.setPixmap(pixmap)
            # self.result_output.append(f"<span style='color: #00ff88;'>✅ Image loaded: {os.path.basename(image_path)}</span>")
            self.update_num_from_mode()
        else:
            self.result_output.append("<span style='color: #ff4444;'>❌ Image file not found</span>")


    def select_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Select Image File", 
            "", 
            "Image Files (*.png *.jpg *.jpeg *.bmp *.gif *.tiff)"
        )
        if file_path:
            self.load_image_to_ui(file_path)

    def load_example_image(self):
        # Path ของโฟลเดอร์ภาพ
        example_folder = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'photoexample'
        )

        # หาเฉพาะไฟล์ภาพ .png, .jpg, .jpeg
        image_files = [f for f in os.listdir(example_folder) 
                    if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

        # จัดเรียงไฟล์ภาพ (optional)
        image_files.sort()

        # ตรวจสอบ index
        index = self.number_selector.currentIndex()
        if 0 <= index < len(image_files):
            image_path = os.path.join(example_folder, image_files[index])
            self.load_image_to_ui(image_path)
        else:
            self.result_output.append("<span style='color: #ff4444;'>❌ No image at selected index</span>")


    def open_output_folder(self):
        script_dir = os.path.dirname(__file__)
        output_path = os.path.join(script_dir, "..", "photoexample", "output")
        os.makedirs(output_path, exist_ok=True)
        QDesktopServices.openUrl(QUrl.fromLocalFile(output_path))
        self.result_output.append("<span style='color: #00d4ff;'>📁 Output folder opened</span>")

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff')):
                self.load_image_to_ui(file_path)
            else:
                self.result_output.append("<span style='color: #ff4444;'>❌ Dropped file is not a supported image format</span>")

    def check_bit_pic(self):
        mode = self.mode_selector.currentText()
        image_path = self.selected_image
        
        # Map shortened names to full names
        mode_mapping = {
            "🔹 LSB": "LSB",
            "🎭 Masking": "Masking and Filtering", 
            "🎨 Palette": "Palette-based Techniques",
            "📐 Edge": "Edge Detection",
            "🔍 Alpha": "Alpha Channel"
        }
        
        mode_clean = mode_mapping.get(mode, mode)
        
        bit_checker_map = {
            "LSB": check_bit_lsb,
            "Masking and Filtering": check_bit_masking_filtering,
            "Palette-based Techniques": check_bit_palette,
            "Edge Detection": check_bit_edge_detection,
            "Alpha Channel": check_bit_alpha_channel
        }
        
        if mode_clean in bit_checker_map:
            return bit_checker_map[mode_clean](image_path)
        return 9999

    def calculate_message_bit(self, message):
        return len(message.encode('utf-8')) * 8

    def check_message_length(self):
        max_bit = self.num
        message = self.message_input.toPlainText()
        message_bit = self.calculate_message_bit(message)
        remaining_bit = max_bit - message_bit

        if remaining_bit >= 0:
            self.bit_info_label.setText(
                f"📊 Capacity: {max_bit:,} bits | Used: {message_bit:,} | Free: {remaining_bit:,}"
            )
            self.bit_info_label.setStyleSheet("""
                QLabel#bitInfo {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 rgba(0, 255, 136, 0.1), stop:1 rgba(0, 255, 136, 0.05));
                    border: 2px solid #00ff88;
                    border-radius: 8px;
                    padding: 12px;
                    font-size: 12px;
                    font-weight: bold;
                    color: #00ff88;
                }
            """)
        else:
            self.bit_info_label.setText(
                f"📊 Capacity: {max_bit:,} bits | Used: {message_bit:,} | ⚠️ Over: {-remaining_bit:,}"
            )
            self.bit_info_label.setStyleSheet("""
                QLabel#bitInfo {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 rgba(255, 68, 68, 0.1), stop:1 rgba(255, 68, 68, 0.05));
                    border: 2px solid #ff4444;
                    border-radius: 8px;
                    padding: 12px;
                    font-size: 12px;
                    font-weight: bold;
                    color: #ff4444;
                }
            """)

    def update_num_from_mode(self):
        self.num = self.check_bit_pic()
        self.previous_text_length = 0
        self.check_message_length()
        self.progress_bar.setValue(0)

    def hide_message(self):
        if not hasattr(self, "selected_image") or not self.selected_image:
            self.result_output.append("<span style='color: #ff4444;'>❌ Please select an image file first</span>")
            return
            
        mode = self.mode_selector.currentText()
        message = self.message_input.toPlainText()
        
        if not message.strip():
            self.result_output.append("<span style='color: #ff4444;'>❌ Please enter a message to hide</span>")
            return
            
        image = self.selected_image
        max_bit = self.check_bit_pic()
        message_bit = self.calculate_message_bit(message)
        
        if message_bit > max_bit:
            max_chars = max_bit // 8
            self.result_output.append(
                f"<span style='color: #ff4444;'>❌ Message too long! Maximum: {max_chars:,} characters</span>"
            )
            return

        output_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), "photoexample", "output")
        os.makedirs(output_folder, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = uuid.uuid4().hex[:8]
        output_path = os.path.join(output_folder, f"hidden_{timestamp}_{unique_id}.png")

        self.result_output.append("<span style='color: #00d4ff;'>🔄 Starting steganography process...</span>")
        
        self.worker = SteganographyWorker(mode, image, message, output_path)
        self.worker.progress.connect(self.progress_bar.setValue)
        self.worker.finished.connect(self.on_hide_finished)
        self.worker.start()

    def retrieve_message(self):
        if not hasattr(self, "selected_image") or not self.selected_image:
            self.result_output.append("<span style='color: #ff4444;'>❌ Please select an image file first</span>")
            return

        mode = self.mode_selector.currentText()
        image_path = self.selected_image
        
        self.result_output.append("<span style='color: #00d4ff;'>🔄 Extracting hidden message...</span>")
        
        self.retrieve_worker = RetrieveWorker(mode, image_path)
        self.retrieve_worker.progress.connect(self.progress_bar.setValue)
        self.retrieve_worker.finished.connect(self.on_extract_finished)
        self.retrieve_worker.start()

    def on_hide_finished(self, message):
        self.result_output.append(message)
        self.progress_bar.setValue(100)

    def on_extract_finished(self, message):
        self.result_output.append(message)
        self.progress_bar.setValue(100)


# --- Thread Worker Classes ---
class SteganographyWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)

    HIDE_MAP = {
        "🔹 LSB": hide_message_lsb_from_steganography,
        "🎭 Masking": hide_message_masking_filtering_from_steganography,
        "🎨 Palette": hide_message_palette_based_from_steganography,
        "📐 Edge": hide_message_edge_detection,
        "🔍 Alpha": hide_message_alpha_channel
    }

    def __init__(self, mode, image, message, output_path):
        super().__init__()
        self.mode = mode
        self.image = image
        self.message = message
        self.output_path = output_path

    def run(self):
        try:
            # Simulate progress
            for i in range(0, 101, 10):
                self.progress.emit(i)
                QThread.msleep(50)
            
            if self.mode in self.HIDE_MAP:
                self.HIDE_MAP[self.mode](self.image, self.message, self.output_path)
                filename = os.path.basename(self.output_path)
                self.finished.emit(
                    f"<span style='color: #00ff88;'>✅ Hidden in: {filename}</span>"
                )
            else:
                self.finished.emit("<span style='color: #ff4444;'>❌ Unsupported mode</span>")
                
        except Exception as e:
            self.finished.emit(f"<span style='color: #ff4444;'>❌ Error: {str(e)}</span>")


class RetrieveWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)

    RETRIEVE_MAP = {
        "🔹 LSB": retrieve_message_lsb_from_steganography,
        "🎭 Masking": retrieve_message_masking_filtering_from_steganography,
        "🎨 Palette": retrieve_message_palette_based_from_steganography,
        "📐 Edge": retrieve_message_edge_detection,
        "🔍 Alpha": retrieve_message_alpha_channel
    }

    def __init__(self, mode, image_path):
        super().__init__()
        self.mode = mode
        self.image_path = image_path

    def run(self):
        try:
            # Simulate progress
            for i in range(0, 101, 10):
                self.progress.emit(i)
                QThread.msleep(50)
            
            if self.mode in self.RETRIEVE_MAP:
                result = self.RETRIEVE_MAP[self.mode](self.image_path)
                if result:
                    self.finished.emit(
                        f"<span style='color: #00ff88;'>✅ Extracted:</span><br>"
                        f"<div style='background: rgba(0, 255, 136, 0.1); padding: 8px; "
                        f"border-radius: 6px; margin: 3px 0; border-left: 3px solid #00ff88;'>"
                        f"<span style='color: #ffffff;'>{result}</span></div>"
                    )
                else:
                    self.finished.emit("<span style='color: #ff4444;'>❌ No message found</span>")
            else:
                self.finished.emit("<span style='color: #ff4444;'>❌ Unsupported mode</span>")
                
        except Exception as e:
            self.finished.emit(f"<span style='color: #ff4444;'>❌ Error: {str(e)}</span>")
