from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox, QPushButton, QLabel,
    QHBoxLayout, QComboBox, QFileDialog, QTextEdit, QFrame,
    QScrollArea
)
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import Qt, QUrl, QThread, pyqtSignal
from PyQt5.QtGui import QDesktopServices
import os
import cv2
import time
import subprocess
import shutil
from utils.steganography import string_to_binary, binary_to_string

class VideoTab(QWidget):
    def __init__(self):
        super().__init__()
        self.video_path = None
        self.max_bits = 0
        self.media_player = QMediaPlayer(self)
        self.initUI()
        self.load_example_video()
        self.setAcceptDrops(True)
        self.video_message_input.textChanged.connect(self.update_bit_display)

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
            QPushButton#playButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #27ae60, stop:1 #229954);
            }
            QPushButton#playButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #37be70, stop:1 #32a964);
            }
            QPushButton#stopButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #e74c3c, stop:1 #c0392b);
            }
            QPushButton#stopButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f55c4c, stop:1 #d0493b);
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
            QLabel#videoPathLabel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1e1e2e, stop:0.5 #2d2d44, stop:1 #1e1e2e);
                border: 2px dashed #00d4ff;
                border-radius: 12px;
                color: #888;
                font-size: 14px;
                font-style: italic;
                padding: 15px;
                min-height: 60px;
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
        video_group = QGroupBox("🎬 Video File Management")
        video_layout = QVBoxLayout()
        video_layout.setSpacing(10)
        file_selection_layout = QHBoxLayout()
        file_selection_layout.setSpacing(15)
        example_frame = QFrame()
        example_frame.setObjectName("card")
        example_layout = QVBoxLayout(example_frame)
        example_layout.setContentsMargins(5,5,5,5)
        self.example_video_dropdown = QComboBox()
        self.example_video_dropdown.setPlaceholderText("Select example video")
        self.example_video_dropdown.currentIndexChanged.connect(self.select_example_video)
        example_layout.addWidget(self.example_video_dropdown)
        select_video_frame = QFrame()
        select_video_frame.setObjectName("card")
        select_video_layout = QVBoxLayout(select_video_frame)
        select_video_layout.setContentsMargins(5,5,5,5)
        self.select_video_button = QPushButton("🔍 Browse Video")
        self.select_video_button.clicked.connect(self.select_video)
        select_video_layout.addWidget(self.select_video_button)
        file_selection_layout.addWidget(example_frame, 1)
        file_selection_layout.addWidget(select_video_frame, 1)
        video_layout.addLayout(file_selection_layout)
        path_and_playback_layout = QHBoxLayout()
        path_and_playback_layout.setSpacing(15)
        path_label_frame = QFrame()
        path_label_frame.setObjectName("card")
        path_label_layout = QVBoxLayout(path_label_frame)
        path_label_layout.setContentsMargins(5,5,5,5)
        current_file_label = QLabel("🎬 Current Video File:")
        current_file_label.setStyleSheet("color: #00d4ff; font-size: 12px;")
        self.video_path_label = QLabel("No file selected")
        self.video_path_label.setObjectName("videoPathLabel")
        self.video_path_label.setAlignment(Qt.AlignCenter)
        path_label_layout.addWidget(current_file_label)
        path_label_layout.addWidget(self.video_path_label)
        playback_buttons_frame = QFrame()
        playback_buttons_frame.setObjectName("card")
        playback_buttons_layout = QVBoxLayout(playback_buttons_frame)
        playback_buttons_layout.setContentsMargins(5,5,5,5)
        playback_row_layout = QHBoxLayout()
        playback_row_layout.setSpacing(10)
        self.play_video_button = QPushButton("Play")
        self.play_video_button.setObjectName("playButton")
        self.play_video_button.clicked.connect(self.play_video)
        self.play_video_button.setMinimumHeight(35)
        self.stop_video_button = QPushButton("Stop")
        self.stop_video_button.setObjectName("stopButton")
        self.stop_video_button.clicked.connect(self.stop_video)
        self.stop_video_button.setMinimumHeight(35)
        playback_row_layout.addWidget(self.play_video_button)
        playback_row_layout.addWidget(self.stop_video_button)
        playback_buttons_layout.addLayout(playback_row_layout)
        path_and_playback_layout.addWidget(path_label_frame, 2)
        path_and_playback_layout.addWidget(playback_buttons_frame, 1)
        video_layout.addLayout(path_and_playback_layout)
        self.video_widget = QVideoWidget()
        self.media_player.setVideoOutput(self.video_widget)
        video_layout.addWidget(self.video_widget)
        video_group.setLayout(video_layout)
        scroll_content_layout.addWidget(video_group)
        message_capacity_group = QGroupBox("💬 Message & Capacity")
        message_capacity_layout = QHBoxLayout()
        message_capacity_layout.setSpacing(15)
        message_input_frame = QFrame()
        message_input_frame.setObjectName("card")
        message_input_layout = QVBoxLayout(message_input_frame)
        message_input_layout.setContentsMargins(5,5,5,5)
        self.video_message_input = QTextEdit()
        self.video_message_input.setPlaceholderText("Enter your secret message here...\nSupports:\n• Multi-line text\n• Unicode characters\n• Special symbols")
        self.video_message_input.setMinimumHeight(150)
        message_input_layout.addWidget(self.video_message_input)
        remaining_bits_frame = QFrame()
        remaining_bits_frame.setObjectName("card")
        remaining_bits_layout = QVBoxLayout(remaining_bits_frame)
        remaining_bits_layout.setContentsMargins(5,5,5,5)
        self.bit_info_label = QLabel("Capacity: N/A | Used: 0")
        self.bit_info_label.setObjectName("bitInfo")
        self.bit_info_label.setAlignment(Qt.AlignCenter)
        self.bit_info_label.setMinimumHeight(100)
        remaining_bits_layout.addWidget(self.bit_info_label)
        message_capacity_layout.addWidget(message_input_frame, 2)
        message_capacity_layout.addWidget(remaining_bits_frame, 1)
        message_capacity_group.setLayout(message_capacity_layout)
        scroll_content_layout.addWidget(message_capacity_group)
        actions_output_group = QGroupBox("🚀 Actions & Output")
        actions_output_layout = QVBoxLayout()
        actions_output_layout.setSpacing(10)
        action_buttons_layout = QHBoxLayout()
        action_buttons_layout.setSpacing(20)
        self.hide_video_button = QPushButton("🔒 Hide")
        self.hide_video_button.setObjectName("hideButton")
        self.hide_video_button.clicked.connect(self.hide_message_in_video)
        self.hide_video_button.setMinimumHeight(40)
        self.extract_video_button = QPushButton("🔓 Extract")
        self.extract_video_button.setObjectName("extractButton")
        self.extract_video_button.clicked.connect(self.extract_message_from_video)
        self.extract_video_button.setMinimumHeight(40)
        self.open_output_folder_button = QPushButton("📁 Output Folder")
        self.open_output_folder_button.setObjectName("folderButton")
        self.open_output_folder_button.clicked.connect(self.open_output_folder)
        self.open_output_folder_button.setMinimumHeight(40)
        action_buttons_layout.addStretch()
        action_buttons_layout.addWidget(self.hide_video_button)
        action_buttons_layout.addWidget(self.extract_video_button)
        action_buttons_layout.addWidget(self.open_output_folder_button)
        action_buttons_layout.addStretch()
        actions_output_layout.addLayout(action_buttons_layout)
        output_label = QLabel("📝 Process Log:")
        output_label.setStyleSheet("color: #00d4ff; font-size: 12px; margin-bottom: 5px; margin-top: 10px;")
        self.result_output = QTextEdit()
        self.result_output.setReadOnly(True)
        self.result_output.setPlaceholderText("Process results and extracted messages will appear here...")
        self.result_output.setMinimumHeight(180)
        actions_output_layout.addWidget(output_label)
        actions_output_layout.addWidget(self.result_output)
        actions_output_group.setLayout(actions_output_layout)
        scroll_content_layout.addWidget(actions_output_group)
        scroll_area.setWidget(scroll_content_widget)
        main_layout.addWidget(scroll_area)
        self.setLayout(main_layout)

    def select_video(self):
        file_dialog = QFileDialog()
        video_path, _ = file_dialog.getOpenFileName(
            self,
            "Select Video File",
            "",
            "Video Files (*.mp4 *.avi *.mkv *.mov)"
        )
        if video_path:
            self.video_path = video_path
            self.video_path_label.setText(os.path.basename(video_path))
            self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(video_path)))
            
            self.calculate_max_bit_capacity()
            self.update_bit_display()
            self.result_output.append(f"<span style='color: #00d4ff;'>🎬 Video selected: {os.path.basename(video_path)}</span>")
        else:
            self.result_output.append("<span style='color: #ff4444;'>❌ No video file selected.</span>")

    def select_example_video(self):
        current_directory = os.path.dirname(os.path.realpath(__file__))
        parent_directory = os.path.dirname(current_directory)
        example_folder_path = os.path.join(parent_directory, "vdio")
        selected_video = self.example_video_dropdown.currentText()
        if selected_video != "Select example video":
            self.video_path = os.path.join(example_folder_path, selected_video)
            self.video_path_label.setText(os.path.basename(self.video_path))
            self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(self.video_path)))
            
            self.calculate_max_bit_capacity()
            self.update_bit_display()
           
        else:
            self.video_path = None
            self.video_path_label.setText("No file selected")
            self.result_output.append("<span style='color: #ff4444;'>❌ No example video selected.</span>")
            self.max_bits = 0
            self.update_bit_display()

    def load_example_video(self):
        current_directory = os.path.dirname(os.path.realpath(__file__))
        parent_directory = os.path.dirname(current_directory)
        example_folder_path = os.path.join(parent_directory, "vdio")
        if os.path.exists(example_folder_path):
            vdio_files = [f for f in os.listdir(example_folder_path) if f.endswith(('.mp4', '.avi', '.mkv', '.mov'))]
            self.example_video_dropdown.clear()
            self.example_video_dropdown.addItem("Select example video")
            self.example_video_dropdown.addItems(vdio_files)
          
            if len(vdio_files) > 0:
                self.example_video_dropdown.setCurrentIndex(1)
        else:
            self.result_output.append("<span style='color: #ff4444;'>❌ Example video folder not found.</span>")

    def play_video(self):
        if self.video_path:
            self.media_player.play()
            self.result_output.append("<span style='color: #00ff88;'>▶️ Playing video...</span>")
        else:
            self.result_output.append("<span style='color: #ff4444;'>❌ Please select a video file to play.</span>")

    def stop_video(self):
        self.media_player.stop()
        self.result_output.append("<span style='color: #ff4444;'>⏹️ Video playback stopped.</span>")

    def open_output_folder(self):
        current_directory = os.path.dirname(os.path.realpath(__file__))
        parent_directory = os.path.dirname(current_directory)
        output_path = os.path.join(parent_directory, "vdio", "output")
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        QDesktopServices.openUrl(QUrl.fromLocalFile(output_path))
        self.result_output.append("<span style='color: #00d4ff;'>📁 Output folder opened.</span>")

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            if os.path.isfile(file_path) and file_path.lower().endswith(('.mp4', '.avi', '.mkv', '.mov')):
                self.video_path = file_path
                self.video_path_label.setText(os.path.basename(file_path))
                self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(file_path)))
                
                self.result_output.append(f"<span style='color: #00d4ff;'>🎬 Video file dropped: {os.path.basename(file_path)}</span>")
                self.calculate_max_bit_capacity()
                self.update_bit_display()
            else:
                self.result_output.append("<span style='color: #ff4444;'>❌ Dropped file is not a supported video format!</span>")

    def calculate_max_bit_capacity(self):
        if not self.video_path:
            self.max_bits = 0
            return 0
        try:
            cap = cv2.VideoCapture(self.video_path)
            if not cap.isOpened():
                raise IOError("Could not open video file.")
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            cap.release()
            self.max_bits = width * height * frame_count * 3
           
            return self.max_bits
        except Exception as e:
            self.result_output.append(f"<span style='color: #ff4444;'>❌ Error calculating bit capacity: {e}</span>")
            self.max_bits = 0
            return 0

    def update_bit_display(self):
        if not self.video_path:
            self.bit_info_label.setText("Capacity: N/A | Used: 0")
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
            return
        message = self.video_message_input.toPlainText()
        total_bits_needed = len(string_to_binary(message)) + 16
        remaining_bits = max(self.max_bits - total_bits_needed, 0)
        self.bit_info_label.setText(
            f"📊 Capacity: {self.max_bits:,} bits | Used: {total_bits_needed:,} bits | Free: {remaining_bits:,} bits"
        )
        if total_bits_needed > self.max_bits:
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
        else:
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

    def hide_message_in_video(self):
        if not self.video_path:
            self.result_output.append("กรุณาเลือกไฟล์วิดีโอก่อน!")
            return

        message = self.video_message_input.toPlainText()
        if not message:
            self.result_output.append("กรุณากรอกข้อความที่จะซ่อนในวิดีโอ!")
            return

        input_video = self.video_path
        current_directory = os.path.dirname(os.path.realpath(__file__))
        parent_directory = os.path.dirname(current_directory)
        directory = os.path.join(parent_directory, "vdio", "output")
        os.makedirs(directory, exist_ok=True)

        filename = os.path.splitext(os.path.basename(input_video))[0]
        timestamp = time.strftime("%Y%m%d%H%M%S")
        output_video = os.path.join(directory, f"{filename}_hidden_{timestamp}.avi")

        self.result_output.append("<font color='blue'>🔄 เริ่มกระบวนการซ่อนข้อความในวิดีโอ...</font>")
        self.worker = VideoSteganographyWorker(
            input_video, output_video, message,
            self.extract_frames, self.encode_message_to_last_frame, self.combine_frames_to_video,
            self.hide_message_in_image, self.extract_message_from_image
        )
        self.worker.finished.connect(self.on_hide_finished)
        self.worker.start()

    def extract_message_from_video(self):
        if not self.video_path:
            self.result_output.append("กรุณาเลือกไฟล์วิดีโอก่อน!")
            return

        output_folder = os.path.join(os.path.dirname(self.video_path), "temp_extracted")
        try:
            self.extract_frames(self.video_path, output_folder)
            frames = sorted([f for f in os.listdir(output_folder) if f.endswith('.png')])
            if not frames:
                self.result_output.append("❌ ไม่พบเฟรมจากวิดีโอ")
                return

            last_frame_path = os.path.join(output_folder, frames[-1])
            img = cv2.imread(last_frame_path)
            if img is None:
                self.result_output.append("❌ ไม่สามารถโหลดเฟรมสุดท้ายได้")
                return

            recovered_message = self.extract_message_from_image(img)
            if recovered_message:
                self.result_output.append(f"<font color='green'>✅ ข้อความที่ถอดได้: {recovered_message}</font>")
            else:
                self.result_output.append("❌ ไม่พบข้อความที่ถูกซ่อนไว้ในวิดีโอ")

        except Exception as e:
            self.result_output.append(f"❌ เกิดข้อผิดพลาดขณะถอดข้อความ: {e}")

        finally:
            if os.path.exists(output_folder):
                shutil.rmtree(output_folder)

    def on_hide_finished(self, message):
        self.result_output.append(message)

    def on_extract_finished(self, message):
        self.result_output.append(message)

    def hide_message_in_image(self, img, message):
        binary_message = string_to_binary(message) + '1111111111111110'  # End Marker
        required_bits = len(binary_message)
        height, width, channels = img.shape
        max_bits = height * width * channels  # จำนวนบิตสูงสุดที่สามารถซ่อนได้

        if required_bits > max_bits:
            raise ValueError(f"ข้อความยาวเกิน: ต้องการ {required_bits} บิต แต่วิดีโอรองรับได้สูงสุด {max_bits} บิต")

        idx = 0
        for i in range(height):
            for j in range(width):
                for k in range(3):  # RGB channels
                    if idx < required_bits:
                        img[i, j, k] = (img[i, j, k] & 0xFE) | int(binary_message[idx])
                        idx += 1
                    else:
                        return img
        return img

    def extract_message_from_image(self, img):
        binary_message = ""
        for i in range(img.shape[0]):
            for j in range(img.shape[1]):
                for k in range(3):  # R, G, B
                    binary_message += str(img[i, j, k] & 1)
                    if len(binary_message) % 8 == 0 and len(binary_message) >= 16:
                        if binary_message[-16:] == '1111111111111110':
                            return binary_to_string(binary_message[:-16])
        return None

    def extract_frames(self, input_video, output_folder):
        if os.path.exists(output_folder):
            shutil.rmtree(output_folder)
        os.makedirs(output_folder)
        subprocess.run(['ffmpeg', '-y', '-i', input_video, f'{output_folder}/frame_%05d.png'], check=True)

    def encode_message_to_last_frame(self, output_folder, message):
        frames = sorted([f for f in os.listdir(output_folder) if f.endswith('.png')])
        if not frames:
            raise FileNotFoundError("ไม่พบเฟรมจากวิดีโอ")

        last_frame_path = os.path.join(output_folder, frames[-1])
        img = cv2.imread(last_frame_path)
        if img is None:
            raise FileNotFoundError(f"Could not load image file: {last_frame_path}")
        img_encoded = self.hide_message_in_image(img, message)
        cv2.imwrite(last_frame_path, img_encoded)

    def combine_frames_to_video(self, output_folder, original_video, output_video):
        # ใช้ FFV1 (Lossless) และรักษาค่า FPS จากวิดีโอต้นฉบับ
        frames = sorted([f for f in os.listdir(output_folder) if f.endswith('.png')])
        if not frames:
            raise FileNotFoundError("ไม่พบไฟล์ภาพในโฟลเดอร์")

        # อ่านค่า FPS จากวิดีโอต้นฉบับ
        cap = cv2.VideoCapture(original_video)
        if not cap.isOpened():
            raise IOError("ไม่สามารถเปิดวิดีโอต้นฉบับเพื่อดึงค่า FPS ได้")
        fps = cap.get(cv2.CAP_PROP_FPS) or 24.0  # ใช้ 24 FPS ถ้าอ่านไม่ได้
        cap.release()

        # ใช้ Codec FFV1 (Lossless) และนามสกุล .avi
        first_frame = cv2.imread(os.path.join(output_folder, frames[0]))
        if first_frame is None:
            raise FileNotFoundError("ไม่สามารถโหลดเฟรมแรกได้")
        height, width, _ = first_frame.shape

        # ปรับให้ความกว้าง-สูงเป็นเลขคู่ (บาง Codec ต้องการ)
        width = width if width % 2 == 0 else width + 1
        height = height if height % 2 == 0 else height + 1

        # ใช้ Codec FFV1 (รองรับนามสกุล .avi)
        fourcc = cv2.VideoWriter_fourcc(*'FFV1')
        out = cv2.VideoWriter(output_video, fourcc, fps, (width, height))
        
        if not out.isOpened():
            raise IOError("ไม่สามารถสร้างวิดีโอขาออกได้")

        # เขียนเฟรมทั้งหมดลงในวิดีโอ
        for frame_file in frames:
            frame = cv2.imread(os.path.join(output_folder, frame_file))
            if frame is None:
                continue
            # ปรับขนาดเฟรมให้ตรงกับความกว้าง-สูงที่กำหนด
            resized_frame = cv2.resize(frame, (width, height))
            out.write(resized_frame)

        out.release()

class VideoSteganographyWorker(QThread):
    finished = pyqtSignal(str)

    def __init__(self, input_video, output_video, message, extract_frames_func, encode_func, combine_func, hide_func, extract_func):
        super().__init__()
        self.input_video = input_video
        self.output_video = output_video
        self.message = message
        self.extract_frames_func = extract_frames_func
        self.encode_func = encode_func
        self.combine_func = combine_func
        self.hide_func = hide_func
        self.extract_func = extract_func

    def run(self):
        output_folder = os.path.join(os.path.dirname(self.output_video), "temp_frames")
        try:
            self.extract_frames_func(self.input_video, output_folder)
            self.encode_func(output_folder, self.message)
            self.combine_func(output_folder, self.input_video, self.output_video)
            filename = os.path.basename(self.output_video)
            self.finished.emit(f"<font color='green'>✅ ซ่อนข้อความใน: {filename}</font>")
        except Exception as e:
            self.finished.emit(f"<font color='red'>❌ เกิดข้อผิดพลาด: {str(e)}</font>")
        finally:
            if os.path.exists(output_folder):
                shutil.rmtree(output_folder)

class VideoRetrieveWorker(QThread):
    finished = pyqtSignal(str)
    def __init__(self, encoded_video, extract_frames_func, extract_message_from_image_func):
        super().__init__()
        self.encoded_video = encoded_video
        self.extract_frames_func = extract_frames_func
        self.extract_message_from_image_func = extract_message_from_image_func

    def run(self):
        output_folder = os.path.join(os.path.dirname(self.encoded_video), "temp_extracted")
        try:
            self.extract_frames_func(self.encoded_video, output_folder)
            frames = sorted([f for f in os.listdir(output_folder) if f.endswith('.png')])
            if not frames:
                self.finished.emit("<span style='color: #ff4444;'>❌ No frames found from video.</span>")
                return
            last_frame_path = os.path.join(output_folder, frames[-1])
            img = cv2.imread(last_frame_path)
            if img is None:
                self.finished.emit("<span style='color: #ff4444;'>❌ Could not load the last frame.</span>")
                return
            recovered_message = self.extract_message_from_image_func(img)
            if recovered_message:
                self.finished.emit(
                    f"<span style='color: #00ff88;'>✅ Extracted message:</span><br>"
                    f"<div style='background: rgba(0, 255, 136, 0.1); padding: 8px; "
                    f"border-radius: 6px; margin: 3px 0; border-left: 3px solid #00ff88;'>"
                    f"<span style='color: #ffffff;'>{recovered_message}</span></div>"
                )
            else:
                self.finished.emit("<span style='color: #ff4444;'>❌ No hidden message found in this video.</span>")
        except subprocess.CalledProcessError as e:
            stderr = e.stderr.decode('utf-8', errors='ignore')
            self.finished.emit(f"<span style='color: #ff4444;'>❌ FFmpeg Error: {stderr}</span>")
        except Exception as e:
            self.finished.emit(f"<span style='color: #ff4444;'>❌ Error extracting message: {str(e)}</span>")
        finally:
            if os.path.exists(output_folder):
                shutil.rmtree(output_folder)