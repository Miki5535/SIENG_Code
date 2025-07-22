import os
import mimetypes
import subprocess
import json
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit,
    QGroupBox, QHBoxLayout, QTextEdit, QComboBox, QMessageBox, QFileDialog,
    QListWidget, QSplitter, QScrollArea, QSizePolicy, QFrame
)
from PyQt5.QtCore import Qt
import ffmpeg
from utils.steganography import string_to_binary, binary_to_string2, binary_to_string


class FileInfoTab(QWidget):
    def __init__(self):
        super().__init__()
        self.selected_file = None
        self.initUI()
        self.setAcceptDrops(True)
        self.hidden_data = {}
        self.supported_formats = {
            '.mp3': ['-id3v2_version', '3', '-write_id3v1', '1'],
            '.m4a': ['-movflags', '+faststart'],
            '.mp4': ['-movflags', '+faststart'],
            '.ogg': [],
            '.wav': []
        }

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
                min-height: 35px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5ba0f2, stop:1 #4585c7);
            }
            QPushButton:pressed {
                background: #2d5aa0;
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
            QLabel#filePathLabel {
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
            QListWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1e1e2e, stop:1 #2d2d44);
                color: #ffffff;
                border: 2px solid #555;
                border-radius: 8px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 5px;
            }
            QListWidget::item:selected {
                background: #00d4ff;
                color: #ffffff;
            }
            QScrollBar:vertical {
                background: #2a2a3e;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #00d4ff;
                border-radius: 6px;
                min-height: 20px;
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
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff) 
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
            }
            QScrollBar:vertical, QScrollBar:horizontal {
                width: 0px;
                height: 0px;
            }
        """)
        
        

        scroll_content_widget = QWidget()
        scroll_content_layout = QVBoxLayout(scroll_content_widget)
        scroll_content_layout.setSpacing(15)
        scroll_content_layout.setContentsMargins(0, 0, 0, 0)

        # -----------------
        hide_group = QGroupBox("🔒 Hide Data in Metadata")
        hide_box_layout = QVBoxLayout()
        hide_box_layout.setSpacing(10)

        file_selection_frame = QFrame()
        file_selection_frame.setObjectName("card")
        file_selection_layout = QHBoxLayout(file_selection_frame)
        file_selection_layout.setSpacing(10)

        self.select_file_button = QPushButton("🔍 Browse File")
        self.select_file_button.clicked.connect(self.select_file_for_info)
        file_selection_layout.addWidget(self.select_file_button)

        self.selected_file_label = QLabel("Drag & Drop File or Use Browse Button")
        self.selected_file_label.setObjectName("filePathLabel")
        self.selected_file_label.setWordWrap(True)
        self.selected_file_label.setAlignment(Qt.AlignCenter)
        file_selection_layout.addWidget(self.selected_file_label, 1)

        hide_box_layout.addWidget(file_selection_frame)

        metadata_secret_layout = QHBoxLayout()
        metadata_layout = QVBoxLayout()

        self.metadata_field = QComboBox()
        standard_fields = ["comment", "title", "artist", "genre", "album", "composer", "copyright", "description"]
        self.metadata_field.addItems(standard_fields)
        self.metadata_field.setMinimumWidth(150)
        self.metadata_field.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        metadata_layout.addWidget(self.metadata_field)

        metadata_secret_layout.addLayout(metadata_layout, 1)

        secret_layout = QVBoxLayout()
        self.secret_text = QLineEdit()
        self.secret_text.setPlaceholderText("กรอกข้อความที่ต้องการซ่อน...")
        secret_layout.addWidget(self.secret_text)
        metadata_secret_layout.addLayout(secret_layout, 2)

        metadata_secret_layout.addStretch()
        hide_box_layout.addLayout(metadata_secret_layout)

        hide_row_layout = QHBoxLayout()
        hide_row_layout.setSpacing(20)
        hide_row_layout.addStretch()

        self.hide_button = QPushButton("🔒 Hide Data")
        self.hide_button.setObjectName("hideButton")
        self.hide_button.clicked.connect(self.hide_metadata)
        hide_row_layout.addWidget(self.hide_button)

        self.open_output_folder_button = QPushButton("📁 Output Folder")
        self.open_output_folder_button.setObjectName("folderButton")
        self.open_output_folder_button.clicked.connect(self.open_output_folder)
        hide_row_layout.addWidget(self.open_output_folder_button)

        hide_row_layout.addStretch()
        hide_box_layout.addLayout(hide_row_layout)

        hide_group.setLayout(hide_box_layout)
        scroll_content_layout.addWidget(hide_group)

        # -----------------
        extract_group = QGroupBox("🔓 Extract Hidden Data")
        extract_box_layout = QVBoxLayout()
        extract_box_layout.setSpacing(5)

        extract_button_frame = QFrame()
        extract_button_frame.setObjectName("card")
        extract_button_layout = QHBoxLayout(extract_button_frame)
        extract_button_layout.addStretch()

        self.extract_button = QPushButton("🔓 Extract All Hidden Data")
        self.extract_button.setObjectName("extractButton")
        self.extract_button.clicked.connect(self.extract_hidden_data)
        extract_button_layout.addWidget(self.extract_button)

        extract_button_layout.addStretch()
        extract_box_layout.addWidget(extract_button_frame)

        self.hidden_data_list = QListWidget()
        self.hidden_data_list.setMinimumHeight(150)
        extract_box_layout.addWidget(QLabel("Extracted Data:"))
        extract_box_layout.addWidget(self.hidden_data_list)

        extract_group.setLayout(extract_box_layout)

        # -----------------
        file_details_group = QGroupBox("📋 File Details & Metadata")
        file_details_layout = QVBoxLayout()
        self.file_info_text = QTextEdit()
        self.file_info_text.setReadOnly(True)
        self.file_info_text.setPlaceholderText("File details and metadata will appear here after selecting a file...")
        self.file_info_text.setMinimumHeight(200)
        file_details_layout.addWidget(self.file_info_text)
        file_details_group.setLayout(file_details_layout)

        # -----------------
        extract_and_details_layout = QHBoxLayout()
        extract_and_details_layout.setSpacing(15)
        extract_and_details_layout.addWidget(extract_group, 1)
        extract_and_details_layout.addWidget(file_details_group, 2)

        scroll_content_layout.addLayout(extract_and_details_layout)

        # -----------------
        scroll_area.setWidget(scroll_content_widget)
        main_layout.addWidget(scroll_area)
        self.setLayout(main_layout)


    def open_output_folder(self):
        if hasattr(self, 'selected_file') and self.selected_file:
            file_directory = os.path.dirname(self.selected_file)
            if os.path.exists(file_directory):
                subprocess.Popen(['explorer', file_directory])
            else:
                QMessageBox.warning(self, "ข้อผิดพลาด", "ไม่พบโฟลเดอร์ของไฟล์ที่เลือก")
        else:
            QMessageBox.warning(self, "แจ้งเตือน", "กรุณาเลือกไฟล์ก่อน")

    def select_file_for_info(self):
        file_filters = [
            "Media Files (*.mp3 *.mp4 *.m4a *.wav *.avi *.mkv *.flv *.mov *.ogg *.wma *.aac)",
            "Audio Files (*.mp3 *.wav *.m4a *.ogg *.wma *.aac)",
            "Video Files (*.mp4 *.avi *.mkv *.flv *.mov)",
            "All Files (*.*)"
        ]
        filters_string = ";;".join(file_filters)
        file_dialog = QFileDialog(self)
        file_path, _ = file_dialog.getOpenFileName(self, "Select a File", "", filters_string)
        if file_path:
            self.selected_file = file_path
            self.selected_file_label.setText(os.path.basename(file_path))
            self.show_file_details(file_path)
            self.hidden_data = {}
            self.hidden_data_list.clear()

    def hide_metadata(self):
        if not hasattr(self, 'selected_file') or not self.selected_file:
            QMessageBox.warning(self, "แจ้งเตือน", "กรุณาเลือกไฟล์ก่อน")
            return
        secret = self.secret_text.text()
        if not secret:
            QMessageBox.warning(self, "แจ้งเตือน", "กรุณากรอกข้อความที่ต้องการซ่อน")
            return
        selected_field = self.metadata_field.currentText()
        if not selected_field:
            QMessageBox.warning(self, "แจ้งเตือน", "กรุณาเลือกฟิลด์มาตรฐาน")
            return
        try:
            file_name = os.path.basename(self.selected_file)
            base_name, ext = os.path.splitext(file_name)
            dir_name = os.path.dirname(self.selected_file)
            temp_file = os.path.join(dir_name, f"{base_name}_temp{ext}")
            output_file = os.path.join(dir_name, f"{base_name}{ext}")
            encoded_secret = string_to_binary(secret)
            ffmpeg_cmd = ffmpeg.input(self.selected_file)
            args = []
            if ext.lower() in self.supported_formats:
                args = self.supported_formats[ext.lower()]
            ffmpeg_cmd = ffmpeg_cmd.output(
                temp_file,
                metadata=f"{selected_field}={encoded_secret}",
                codec="copy"
            ).global_args(*args).overwrite_output()
            try:
                ffmpeg_cmd.run(capture_stdout=True, capture_stderr=True, overwrite_output=True)
            except ffmpeg.Error as e:
                stdout = e.stdout.decode('utf-8', errors='ignore') if e.stdout else ''
                stderr = e.stderr.decode('utf-8', errors='ignore') if e.stderr else ''
                QMessageBox.critical(self, "FFmpeg Error", f"FFmpeg Error:\n{stderr}")
            if os.path.exists(output_file):
                os.remove(output_file)
            os.rename(temp_file, output_file)
            self.selected_file = output_file
            self.selected_file_label.setText(os.path.basename(output_file))
            self.show_file_details(output_file)
            QMessageBox.information(
                self,
                "สำเร็จ",
                f"ซ่อนข้อมูลสำเร็จในฟิลด์: {selected_field}\n"
                f"ไฟล์ถูกบันทึกที่: {output_file}\n"
                f"ไฟล์ใหม่ถูกเลือกโดยอัตโนมัติแล้ว"
            )
            self.secret_text.clear()
        except ffmpeg.Error as e:
            stderr = e.stderr.decode('utf-8', errors='ignore')
            QMessageBox.critical(self, "ข้อผิดพลาด", f"FFmpeg error: {stderr}")
        except Exception as e:
            QMessageBox.critical(self, "ข้อผิดพลาด", f"เกิดข้อผิดพลาด: {str(e)}")

    def extract_hidden_data(self):
        if not hasattr(self, 'selected_file') or not self.selected_file:
            QMessageBox.warning(self, "แจ้งเตือน", "กรุณาเลือกไฟล์ก่อน")
            return
        try:
            self.hidden_data = {}
            self.hidden_data_list.clear()
            media_info = self.get_media_info(self.selected_file)
            if 'tags' in media_info:
                tags = media_info['tags']
                found_hidden = False
                for field, value in tags.items():
                    if isinstance(value, str) and all(c in '01 ' for c in value.strip()):
                        decoded = binary_to_string2(value.strip())
                        if decoded:
                            self.hidden_data[field] = decoded
                            self.hidden_data_list.addItem(f"{field}: {decoded}")
                            found_hidden = True
                if not found_hidden:
                    QMessageBox.information(self, "ผลการค้นหา", "ไม่พบข้อมูลที่ซ่อนไว้ในไฟล์นี้")
            else:
                QMessageBox.warning(self, "แจ้งเตือน", "ไม่สามารถดึงข้อมูล metadata จากไฟล์นี้ได้")
        except Exception as e:
            QMessageBox.critical(self, "ข้อผิดพลาด", f"เกิดข้อผิดพลาดในการดึงข้อมูล: {str(e)}")

    def show_file_details(self, file_path):
        try:
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            size_text = self.format_size(file_size)
            mime_type = mimetypes.guess_type(file_path)[0] or "unknown"
            detailed_info = [
                f"<span style='color: #00d4ff; font-size: 14px; font-weight: bold;'>📝 File Details</span>",
                f"<span style='color: #555;'>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</span>",
                f"📋 <span style='color: #ccc;'>File Name:</span> <span style='color: #fff;'>{file_name}</span>",
                f"📊 <span style='color: #ccc;'>Size:</span> <span style='color: #fff;'>{size_text}</span>",
                f"🏷️ <span style='color: #ccc;'>Type:</span> <span style='color: #fff;'>{mime_type}</span>",
            ]
            if mime_type.startswith(('video/', 'audio/')):
                media_info = self.get_media_info(file_path)
                if 'general' in media_info:
                    general = media_info['general']
                    detailed_info.extend([
                        f"\n<span style='color: #00d4ff; font-size: 14px; font-weight: bold;'>📌 General Information</span>",
                        f"<span style='color: #555;'>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</span>",
                    ])
                    general_fields = {
                        '⏱️ Duration': f"{float(general.get('duration', 0)):.2f} seconds",
                        '📊 Total Bit Rate': f"{int(general.get('bit_rate', 0)) // 1000} kbps",
                    }
                    for label, value in general_fields.items():
                        detailed_info.append(f"<span style='color: #ccc;'>{label}:</span> <span style='color: #fff;'>{value}</span>")
                if 'tags' in media_info:
                    detailed_info.extend([
                        f"\n<span style='color: #00d4ff; font-size: 14px; font-weight: bold;'>🔖 Metadata Fields</span>",
                        f"<span style='color: #555;'>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</span>",
                    ])
                    tags = media_info['tags']
                    for field, value in tags.items():
                        if value != 'N/A':
                            hidden_text = ""
                            if isinstance(value, str) and all(c in '01 ' for c in value.strip()):
                                decoded = binary_to_string2(value.strip())
                                if decoded:
                                    hidden_text = f" <span style='color: #00ff88;'>(Hidden: {decoded})</span>"
                                else:
                                    hidden_text = f" <span style='color: #ff4444;'>(Binary, No Message)</span>"
                            detailed_info.append(f"<span style='color: #ccc;'>{field}:</span> <span style='color: #fff;'>{value}</span>{hidden_text}")
                if 'video' in media_info and media_info['video']:
                    video = media_info['video']
                    detailed_info.extend([
                        f"\n<span style='color: #00d4ff; font-size: 14px; font-weight: bold;'>🎥 Video Information</span>",
                        f"<span style='color: #555;'>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</span>",
                        f"🖼️ <span style='color: #ccc;'>Resolution:</span> <span style='color: #fff;'>{video.get('width', 'N/A')}x{video.get('height', 'N/A')}</span>",
                    ])
                    frame_rate = video.get('frame_rate', 'N/A')
                    if frame_rate != 'N/A':
                        try:
                            frame_rate = f"{eval(frame_rate):.2f} fps"
                        except:
                            frame_rate = 'N/A'
                    detailed_info.append(f"🎞️ <span style='color: #ccc;'>Frame Rate:</span> <span style='color: #fff;'>{frame_rate}</span>")
                    video_bit_rate = video.get('bit_rate', 'N/A')
                    if video_bit_rate != 'N/A' and str(video_bit_rate).isdigit():
                        video_bit_rate = f"{int(video_bit_rate) // 1000} kbps"
                    else:
                        video_bit_rate = 'N/A'
                    detailed_info.append(f"📊 <span style='color: #ccc;'>Video Bit Rate:</span> <span style='color: #fff;'>{video_bit_rate}</span>")
                    detailed_info.extend([
                        f"🎯 <span style='color: #ccc;'>Codec:</span> <span style='color: #fff;'>{video.get('codec', 'N/A')}</span>",
                        f"🎨 <span style='color: #ccc;'>Pixel Format:</span> <span style='color: #fff;'>{video.get('pixel_format', 'N/A')}</span>",
                    ])
                if 'audio' in media_info and media_info['audio']:
                    audio = media_info['audio']
                    detailed_info.extend([
                        f"\n<span style='color: #00d4ff; font-size: 14px; font-weight: bold;'>🔊 Audio Information</span>",
                        f"<span style='color: #555;'>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</span>",
                    ])
                    sample_rate = audio.get('sample_rate', 'N/A')
                    if sample_rate != 'N/A' and str(sample_rate).isdigit():
                        sample_rate = f"{int(sample_rate) // 1000} kHz"
                    else:
                        sample_rate = 'N/A'
                    detailed_info.append(f"🎵 <span style='color: #ccc;'>Sample Rate:</span> <span style='color: #fff;'>{sample_rate}</span>")
                    detailed_info.extend([
                        f"📢 <span style='color: #ccc;'>Channels:</span> <span style='color: #fff;'>{audio.get('channels', 'N/A')} ({audio.get('channel_layout', 'N/A')})</span>",
                    ])
                    audio_bit_rate = audio.get('bit_rate', 'N/A')
                    if audio_bit_rate != 'N/A' and str(audio_bit_rate).isdigit():
                        audio_bit_rate = f"{int(audio_bit_rate) // 1000} kbps"
                    else:
                        audio_bit_rate = 'N/A'
                    detailed_info.append(f"📊 <span style='color: #ccc;'>Audio Bit Rate:</span> <span style='color: #fff;'>{audio_bit_rate}</span>")
                    detailed_info.append(f"🎯 <span style='color: #ccc;'>Codec:</span> <span style='color: #fff;'>{audio.get('codec', 'N/A')}</span>")
            self.file_info_text.setHtml("<br>".join(detailed_info))
        except Exception as e:
            self.file_info_text.setText(f"Error occurred: {str(e)}")

    def format_size(self, size):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0

    def get_media_info(self, file_path):
        try:
            command = [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                '-show_streams',
                file_path
            ]
            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=False
            )
            stdout = result.stdout.decode('utf-8', errors='ignore')
            stderr = result.stderr.decode('utf-8', errors='ignore')
            data = json.loads(stdout)
            media_info = {
                'general': {},
                'video': {},
                'audio': {},
                'tags': {}
            }
            if 'format' in data:
                format_data = data['format']
                media_info['general'] = {
                    'duration': format_data.get('duration', 'N/A'),
                    'size': format_data.get('size', 'N/A'),
                    'bit_rate': format_data.get('bit_rate', 'N/A'),
                    'format_name': format_data.get('format_name', 'N/A'),
                }
                if 'tags' in format_data:
                    media_info['tags'] = format_data['tags']
                    media_info['general'].update({
                        'title': format_data['tags'].get('title', 'N/A'),
                        'artist': format_data['tags'].get('artist', 'N/A'),
                        'date': format_data['tags'].get('date', 'N/A'),
                        'comment': format_data['tags'].get('comment', 'N/A'),
                        'genre': format_data['tags'].get('genre', 'N/A'),
                    })
            if 'streams' in data:
                for stream in data['streams']:
                    if 'tags' in stream:
                        media_info['tags'].update(stream['tags'])
                    if stream['codec_type'] == 'video':
                        media_info['video'] = {
                            'codec': stream.get('codec_name', 'N/A'),
                            'width': stream.get('width', 'N/A'),
                            'height': stream.get('height', 'N/A'),
                            'frame_rate': stream.get('r_frame_rate', 'N/A'),
                            'bit_rate': stream.get('bit_rate', 'N/A'),
                            'total_frames': stream.get('nb_frames', 'N/A'),
                            'pixel_format': stream.get('pix_fmt', 'N/A'),
                        }
                    elif stream['codec_type'] == 'audio':
                        media_info['audio'] = {
                            'codec': stream.get('codec_name', 'N/A'),
                            'sample_rate': stream.get('sample_rate', 'N/A'),
                            'channels': stream.get('channels', 'N/A'),
                            'bit_rate': stream.get('bit_rate', 'N/A'),
                            'channel_layout': stream.get('channel_layout', 'N/A'),
                        }
            return media_info
        except subprocess.CalledProcessError as e:
            return {'general': {}, 'error': f"ffprobe error: {e.stderr.decode('utf-8', errors='ignore')}"}
        except json.JSONDecodeError:
            return {'general': {}, 'error': "Failed to parse ffprobe output (invalid JSON)."}
        except Exception as e:
            return {'general': {}, 'error': f"ไม่สามารถดึงข้อมูลมัลติมีเดียได้: {str(e)}"}

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            if os.path.isfile(file_path) and file_path.lower().endswith((
                '.mp3', '.mp4', '.m4a', '.wav', '.avi', '.mkv',
                '.flv', '.mov', '.ogg', '.wma', '.aac')):
                self.selected_file = file_path
                self.selected_file_label.setText(os.path.basename(file_path))
                self.show_file_details(file_path)
                QMessageBox.information(self, "ไฟล์ที่เลือก", f"เลือกไฟล์ผ่านการลากและวาง: {file_path}")
            else:
                QMessageBox.warning(self, "ข้อผิดพลาด", "ไฟล์ที่ลากเข้ามาไม่ใช่ประเภทที่รองรับ")