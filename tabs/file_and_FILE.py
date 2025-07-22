import logging
import shutil
import struct
import time
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QGroupBox, QPushButton, QFileDialog,
    QTextEdit, QScrollArea, QGridLayout, QMessageBox, QHBoxLayout, QFrame
)
from PyQt5.QtGui import QPixmap, QIcon, QDragEnterEvent, QDropEvent
from PyQt5.QtCore import Qt, QUrl
import os

class FileAndFileTab(QWidget):
    def __init__(self):
        super().__init__()
        self.files_to_append = []
        self.initUI()
        self.setAcceptDrops(True)

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
            QPushButton#clearButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #e74c3c, stop:1 #c0392b);
            }
            QPushButton#clearButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f55c4c, stop:1 #d0493b);
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
        horizontal_group_layout = QHBoxLayout()
        horizontal_group_layout.setSpacing(15)
        
        group_text = QGroupBox("📝 Append & Extract Text")
        layout_text = QVBoxLayout()
        layout_text.setSpacing(10)
        text_input_frame = QFrame()
        text_input_frame.setObjectName("card")
        text_input_layout = QVBoxLayout(text_input_frame)
        text_input_layout.setContentsMargins(5,5,5,5)
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText("Enter text to append...")
        self.text_input.setMinimumHeight(150)
        text_input_layout.addWidget(self.text_input)
        layout_text.addWidget(text_input_frame)
        text_buttons_layout = QHBoxLayout()
        text_buttons_layout.setSpacing(10)
        self.button_append_text = QPushButton("🔒 Append Text")
        self.button_append_text.setObjectName("hideButton")
        self.button_append_text.clicked.connect(self.append_text_to_image)
        self.button_append_text.setMinimumHeight(40)
        
        self.button_extract_text = QPushButton("🔓 Extract Text")
        self.button_extract_text.setObjectName("extractButton")
        self.button_extract_text.clicked.connect(self.extract_text_content)
        self.button_extract_text.setMinimumHeight(40)
        
                # --- เพิ่มปุ่มเปิดโฟลเดอร์ output ---
        self.button_open_output = QPushButton("📂 Output Folder")
        self.button_open_output.setObjectName("folderButton")
        self.button_open_output.clicked.connect(self.open_output_folder)
        self.button_open_output.setMinimumHeight(40)


        
        text_buttons_layout.addStretch()
        text_buttons_layout.addWidget(self.button_append_text)
        text_buttons_layout.addWidget(self.button_extract_text)
        text_buttons_layout.addWidget(self.button_open_output) 
        text_buttons_layout.addStretch()
        layout_text.addLayout(text_buttons_layout)
        group_text.setLayout(layout_text)
        horizontal_group_layout.addWidget(group_text)
        
        group_file = QGroupBox("📁 Append & Extract Files")
        layout_file = QVBoxLayout()
        layout_file.setSpacing(10)
        file_selection_frame = QFrame()
        file_selection_frame.setObjectName("card")
        file_selection_layout = QVBoxLayout(file_selection_frame)
        file_selection_layout.setContentsMargins(5,5,5,5)
        self.info_label = QLabel("No files selected")
        self.info_label.setStyleSheet("color: #00d4ff; font-size: 12px; margin-bottom: 5px;")
        file_selection_layout.addWidget(self.info_label)
        self.scroll_area_preview = QScrollArea()
        self.scroll_area_preview.setWidgetResizable(True)
        self.scroll_area_preview.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.preview_container = QWidget()
        self.preview_layout = QGridLayout()
        self.preview_container.setLayout(self.preview_layout)
        self.scroll_area_preview.setWidget(self.preview_container)
        self.scroll_area_preview.setMinimumHeight(150)
        file_selection_layout.addWidget(self.scroll_area_preview)
        file_buttons_row1 = QHBoxLayout()
        file_buttons_row1.setSpacing(10)
        self.button_select_files = QPushButton("➕ Select Files")
        self.button_select_files.clicked.connect(self.select_files)
        self.button_select_files.setMinimumHeight(35)
        self.button_clear_all = QPushButton("🗑️ Clear All")
        self.button_clear_all.setObjectName("clearButton")
        self.button_clear_all.clicked.connect(self.clear_all_files)
        self.button_clear_all.setMinimumHeight(35)
        file_buttons_row1.addWidget(self.button_select_files)
        file_buttons_row1.addWidget(self.button_clear_all)
        file_selection_layout.addLayout(file_buttons_row1)
        layout_file.addWidget(file_selection_frame)
        file_buttons_row2 = QHBoxLayout()
        file_buttons_row2.setSpacing(10)
        self.button_append_files = QPushButton("🔒 Append Files")
        self.button_append_files.setObjectName("hideButton")
        self.button_append_files.clicked.connect(self.file_to)
        self.button_append_files.setMinimumHeight(40)
        self.button_extract_files = QPushButton("🔓 Extract Files")
        self.button_extract_files.setObjectName("extractButton")
        self.button_extract_files.clicked.connect(self.ex_file)
        self.button_extract_files.setMinimumHeight(40)
        file_buttons_row2.addStretch()
        file_buttons_row2.addWidget(self.button_append_files)
        file_buttons_row2.addWidget(self.button_extract_files)
        file_buttons_row2.addStretch()
        layout_file.addLayout(file_buttons_row2)
        group_file.setLayout(layout_file)
        horizontal_group_layout.addWidget(group_file)
        scroll_content_layout.addLayout(horizontal_group_layout)
        output_group = QGroupBox("📊 Process Log")
        output_layout = QVBoxLayout()
        output_layout.setSpacing(10)
        self.file_content_display = QTextEdit()
        self.file_content_display.setReadOnly(True)
        self.file_content_display.setPlaceholderText("Process results and logs will appear here...")
        self.file_content_display.setMinimumHeight(180)
        output_layout.addWidget(self.file_content_display)
        output_group.setLayout(output_layout)
        scroll_content_layout.addWidget(output_group)
        scroll_area.setWidget(scroll_content_widget)
        main_layout.addWidget(scroll_area)
        self.setLayout(main_layout)

    def append_files_to_image(self, image_path, file_paths):
        if not file_paths:
            raise ValueError("No files selected to append.")
        base_name, ext = os.path.splitext(os.path.basename(image_path))
        output_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "output_files")
        os.makedirs(output_dir, exist_ok=True)
        modified_image_path = os.path.join(output_dir, f"{base_name}_appended_{int(time.time())}{ext}")
        shutil.copy2(image_path, modified_image_path)
        with open(modified_image_path, 'ab') as image_file:
            original_size = os.path.getsize(image_path)
            image_file.write(struct.pack('<I', len(file_paths)))
            for file_path in file_paths:
                _, ext = os.path.splitext(file_path)
                ext = ext[1:].encode('ascii')
                with open(file_path, 'rb') as f:
                    file_data = f.read()
                image_file.write(struct.pack('<I', len(ext)))
                image_file.write(ext)
                image_file.write(struct.pack('<Q', len(file_data)))
                image_file.write(file_data)
            image_file.write(struct.pack('<Q', original_size))
        return modified_image_path

    def append_text_to_image(self):
        image_path, _ = QFileDialog.getOpenFileName(self, "Select Image File", "", "Images (*.png *.jpg *.jpeg)")
        if not image_path:
            self.file_content_display.append("<span style='color: #ff4444;'>❌ Please select an image file first.</span>")
            return
        text = self.text_input.toPlainText()
        if not text:
            self.file_content_display.append("<span style='color: #ff4444;'>❌ No text to append.</span>")
            return
        base_name, ext = os.path.splitext(os.path.basename(image_path))
        output_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "output_files")
        os.makedirs(output_dir, exist_ok=True)
        modified_image_path = os.path.join(output_dir, f"{base_name}_text_appended_{int(time.time())}{ext}")
        shutil.copy2(image_path, modified_image_path)
        try:
            with open(modified_image_path, 'ab') as image_file:
                image_file.write(struct.pack('<I', 1))
                image_file.write(struct.pack('<I', len('txt'.encode('ascii'))))
                image_file.write(b'txt')
                file_data = text.encode('utf-8')
                image_file.write(struct.pack('<Q', len(file_data)))
                image_file.write(file_data)
                image_file.write(struct.pack('<Q', os.path.getsize(image_path)))
            self.file_content_display.append(f"<span style='color: #00ff88;'>✅ Text appended to: <font color='#00d4ff'>{os.path.basename(modified_image_path)}</font></span>")
            self.text_input.clear()
        except Exception as e:
            self.file_content_display.append(f"<span style='color: #ff4444;'>❌ Error appending text: {e}</span>")

    def file_to(self):
        image_path, _ = QFileDialog.getOpenFileName(self, "Select Image File", "", "Images (*.png *.jpg *.jpeg)")
        if not image_path:
            self.file_content_display.append("<span style='color: #ff4444;'>❌ Please select an image file first.</span>")
            return
        if not self.files_to_append:
            self.file_content_display.append("<span style='color: #ff4444;'>❌ No files selected to append.</span>")
            return
        try:
            modified_image = self.append_files_to_image(image_path, self.files_to_append)
            self.file_content_display.append(f"<span style='color: #00ff88;'>✅ Files appended to: <font color='#00d4ff'>{os.path.basename(modified_image)}</font></span>")
            self.clear_all_files()
        except Exception as e:
            self.file_content_display.append(f"<span style='color: #ff4444;'>❌ Error appending files: {e}</span>")

    def extract_appended_files(self, image_path):
        extracted_files = []
        try:
            with open(image_path, 'rb') as f:
                f.seek(-8, os.SEEK_END)
                original_size = struct.unpack('<Q', f.read(8))[0]
                f.seek(original_size)
                num_files = struct.unpack('<I', f.read(4))[0]
                for _ in range(num_files):
                    ext_len = struct.unpack('<I', f.read(4))[0]
                    file_ext = f.read(ext_len).decode('ascii', errors='ignore')
                    file_size = struct.unpack('<Q', f.read(8))[0]
                    file_data = f.read(file_size)
                    extracted_files.append({
                        'type': 'text' if file_ext.lower() == 'txt' else 'binary',
                        'ext': file_ext,
                        'data': file_data,
                        'content': file_data.decode('utf-8', errors='replace') if file_ext.lower() == 'txt' else None
                    })
        except struct.error:
            self.file_content_display.append("<span style='color: #ff4444;'>❌ No appended data found or file is corrupted.</span>")
            return []
        except Exception as e:
            self.file_content_display.append(f"<span style='color: #ff4444;'>❌ Error extracting files: {e}</span>")
            return []
        return extracted_files

    def ex_file(self):
        image_path, _ = QFileDialog.getOpenFileName(self, "Select Modified Image File", "", "Images (*.png *.jpg *.jpeg)")
        if not image_path:
            self.file_content_display.append("<span style='color: #ff4444;'>❌ Please select an image file first.</span>")
            return
        output_folder = QFileDialog.getExistingDirectory(self, "Select Folder to Save Extracted Files")
        if not output_folder:
            self.file_content_display.append("<span style='color: #ff4444;'>❌ Please select an output folder.</span>")
            return
        try:
            os.makedirs(output_folder, exist_ok=True)
            extracted_files = self.extract_appended_files(image_path)
            if not extracted_files:
                self.file_content_display.append("<span style='color: #ff4444;'>❌ No appended files found in this image.</span>")
                return
            text_content_found = False
            binary_files_saved = []
            for i, file_info in enumerate(extracted_files):
                if file_info['type'] == 'text':
                    self.file_content_display.append(
                        f"<span style='color: #00ff88;'>✅ Extracted Text:</span><br>"
                        f"<div style='background: rgba(0, 255, 136, 0.1); padding: 8px; "
                        f"border-radius: 6px; margin: 3px 0; border-left: 3px solid #00ff88;'>"
                        f"<span style='color: #ffffff;'>{file_info['content']}</span></div>"
                    )
                    text_content_found = True
                else:
                    file_path = os.path.join(output_folder, f"extracted_file_{i + 1}.{file_info['ext']}")
                    with open(file_path, 'wb') as f:
                        f.write(file_info['data'])
                    binary_files_saved.append(os.path.basename(file_path))
            if binary_files_saved:
                self.file_content_display.append(f"<span style='color: #00ff88;'>✅ Other files saved to: <font color='#00d4ff'>{output_folder}</font></span>")
                for fname in binary_files_saved:
                    self.file_content_display.append(f"  - {fname}")
            if not text_content_found and not binary_files_saved:
                self.file_content_display.append("<span style='color: #ff4444;'>❌ No extractable content found.</span>")
        except Exception as e:
            self.file_content_display.append(f"<span style='color: #ff4444;'>❌ Error during extraction: {e}</span>")

    def extract_text_content(self):
        image_path, _ = QFileDialog.getOpenFileName(self, "Select Modified Image File", "", "Images (*.png *.jpg *.jpeg)")
        if not image_path:
            self.file_content_display.append("<span style='color: #ff4444;'>❌ Please select an image file first.</span>")
            return
        try:
            extracted_files = self.extract_appended_files(image_path)
            found_text = False
            for file_info in extracted_files:
                if file_info['type'] == 'text':
                    self.file_content_display.append(
                        f"<span style='color: #00ff88;'>✅ Extracted Text:</span><br>"
                        f"<div style='background: rgba(0, 255, 136, 0.1); padding: 8px; "
                        f"border-radius: 6px; margin: 3px 0; border-left: 3px solid #00ff88;'>"
                        f"<span style='color: #ffffff;'>{file_info['content']}</span></div>"
                    )
                    found_text = True
                    break
            if not found_text:
                self.file_content_display.append("<span style='color: #ff4444;'>❌ No appended text found in this image.</span>")
        except Exception as e:
            self.file_content_display.append(f"<span style='color: #ff4444;'>❌ Error extracting text: {e}</span>")

    def select_files(self):
        file_paths, _ = QFileDialog.getOpenFileNames(self, "Select Files to Append", "", "All Files (*.*)")
        if file_paths:
            self.files_to_append.extend(file_paths)
            self.info_label.setText(f"Selected {len(self.files_to_append)} files")
            self.update_preview(self.files_to_append)
            self.file_content_display.append(f"<span style='color: #00d4ff;'>➕ Added {len(file_paths)} files for appending.</span>")
            for fp in file_paths:
                self.file_content_display.append(f"  - {os.path.basename(fp)}")

    def clear_all_files(self):
        if not self.files_to_append:
            return
        reply = QMessageBox.question(self, "Confirm Clear", "Are you sure you want to clear all selected files?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.files_to_append.clear()
            for i in reversed(range(self.preview_layout.count())):
                widget = self.preview_layout.itemAt(i).widget()
                if widget:
                    widget.setParent(None)
            self.info_label.setText("No files selected")
            self.file_content_display.append("<span style='color: #ff4444;'>🗑️ All selected files cleared.</span>")




    def update_preview(self, file_paths):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        icon_dir = os.path.join(base_dir, "photoexample", "potofle")
        
        
        ext_icon_map = {
            '.asc': 'asc.png',
            '.bat': 'bat.png',
            '.css': 'css.png',
            '.dat': 'dat.png',
            '.gradle': 'gradle.png',
            '.html': 'html.png',
            '.iml': 'iml.png',
            '.js': 'js.png',
            '.json': 'json.png',
            '.md': 'md.png',
            '.msi': 'msi.png',
            '.pdf': 'pdf.png',
            '.pkg': 'pkg.png',
            '.ppt': 'pp.png',
            '.pptx': 'pp.png',
            '.py': 'py.png',
            '.txt': 'txt.png',
            '.xml': 'xml.png',
            '.yaml': 'yaml.png',
            '.yml': 'yaml.png',
            '.zip': 'zip.png',
            '.xls': 'excel.png',
            '.xlsx': 'excel.png',
            '.exe': 'exe.png',
            '.doc': 'word.png',
            '.docx': 'word.png',
        }

        image_exts = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg']

        # เคลียร์ layout เดิม
        for i in reversed(range(self.preview_layout.count())):
            widget = self.preview_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        row, col = 0, 0
        for file_path in file_paths:
            container = QFrame()
            container.setObjectName("card")
            container_layout = QVBoxLayout(container)
            container_layout.setContentsMargins(5,5,5,5)
            container_layout.setAlignment(Qt.AlignCenter)

            icon_label = QLabel()
            icon_label.setAlignment(Qt.AlignCenter)

            ext = os.path.splitext(file_path)[1].lower()

            # ----- เช็คว่าเป็นไฟล์ภาพไหม -----
            if ext in image_exts:
                pixmap = QPixmap(file_path)
                if not pixmap.isNull():
                    pixmap = pixmap.scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    icon_label.setPixmap(pixmap)
                else:
                    icon_label.setText("🖼️")
                    icon_label.setStyleSheet("font-size: 36px; color: #00d4ff;")
            else:
                # ถ้าไม่ใช่ภาพ ใช้ icon จาก map
                icon_file = ext_icon_map.get(ext, 'default.png')
                icon_path = os.path.join(icon_dir, icon_file).replace('\\', '/')
                pixmap = QPixmap(icon_path)
                if not pixmap.isNull():
                    pixmap = pixmap.scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    icon_label.setPixmap(pixmap)
                else:
                    icon_label.setText("📄")
                    icon_label.setStyleSheet("font-size: 36px; color: #00d4ff;")

            # ----- Label + Button -----
            name_label = QLabel(os.path.basename(file_path))
            name_label.setAlignment(Qt.AlignCenter)
            name_label.setWordWrap(True)
            name_label.setStyleSheet("font-size: 11px; color: #cccccc;")

            delete_button = QPushButton("Del")
            delete_button.setObjectName("clearButton")
            delete_button.setFixedSize(60, 25)
            delete_button.clicked.connect(lambda _, fp=file_path: self.remove_preview(fp))

            container_layout.addWidget(icon_label)
            container_layout.addWidget(name_label)
            container_layout.addWidget(delete_button)

            self.preview_layout.addWidget(container, row, col)
            col += 1
            if col > 3:
                col = 0
                row += 1


    def open_output_folder(self):
        script_dir = os.path.dirname(os.path.realpath(__file__))
        output_dir = os.path.join(script_dir, "..", "output_files")

        if os.path.exists(output_dir):
            if os.name == 'nt':  # Windows
                os.startfile(output_dir)
            elif os.name == 'posix':
                if sys.platform == 'darwin':  # macOS
                    os.system(f"open '{output_dir}'")
                else:  # Linux
                    os.system(f"xdg-open '{output_dir}'")
            self.file_content_display.append(f"<span style='color: #00d4ff;'>📁 Opening output folder: {output_dir}</span>")
        else:
            self.file_content_display.append(f"<span style='color: #ff4444;'>❌ Output folder does not exist: {output_dir}</span>")

    def remove_preview(self, file_path):
        if file_path in self.files_to_append:
            self.files_to_append.remove(file_path)
            self.update_preview(self.files_to_append)
            self.info_label.setText(f"Selected {len(self.files_to_append)} files")
            self.file_content_display.append(f"<span style='color: #ff4444;'>➖ Removed: {os.path.basename(file_path)}</span>")

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        file_paths = [url.toLocalFile() for url in urls if url.isLocalFile()]
        if file_paths:
            self.files_to_append.extend(file_paths)
            self.update_preview(self.files_to_append)
            self.info_label.setText(f"Selected {len(self.files_to_append)} files")
            self.file_content_display.append(f"<span style='color: #00d4ff;'>➕ Dropped {len(file_paths)} files.</span>")
            for fp in file_paths:
                self.file_content_display.append(f"  - {os.path.basename(fp)}")