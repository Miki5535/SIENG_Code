import os
import uuid
import wave
import numpy as np
from PyQt5.QtWidgets import (
  QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog, QHBoxLayout,
  QGroupBox, QComboBox, QTextEdit, QFrame, QGridLayout, QSplitter,
  QScrollArea # Import QScrollArea
)
from PyQt5.QtGui import QPixmap, QDesktopServices, QFont, QIcon
from PyQt5.QtCore import Qt, QUrl, QThread, pyqtSignal
from pydub import AudioSegment
import soundfile as sf
import sounddevice as sd
import utils.steganography as steganography

class AudioTab(QWidget):
    def __init__(self):
        super().__init__()
        self.selected_audio_path = "ไม่ได้เลือกไฟล์" 
        self.total_bits = 0
        self.initUI()
        self.load_example_audio()
        self.setAcceptDrops(True)
        self.audio_message_input.textChanged.connect(self.show_used_bits)
        
    def initUI(self):
        
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
            
            /* Special Button Colors (consistent with ImageTab) */
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
            
            QLabel#audioPathLabel {
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
        

        audio_group = QGroupBox("🎵 Audio File Management")
        audio_layout = QVBoxLayout()
        audio_layout.setSpacing(10)
        

        file_selection_layout = QHBoxLayout()
        file_selection_layout.setSpacing(15) 
        

        example_frame = QFrame()
        example_frame.setObjectName("card")
        example_layout = QVBoxLayout(example_frame) 
        example_layout.setContentsMargins(5,5,5,5)
        
        self.example_audio_dropdown = QComboBox()
        self.example_audio_dropdown.setPlaceholderText("Select example audio")
        self.example_audio_dropdown.currentIndexChanged.connect(self.select_example_audio)
        
        example_layout.addWidget(self.example_audio_dropdown)
        

        select_audio_frame = QFrame()
        select_audio_frame.setObjectName("card")
        select_audio_layout = QVBoxLayout(select_audio_frame) 
        select_audio_layout.setContentsMargins(5,5,5,5)
        
        self.select_audio_button = QPushButton("🔍 Browse Audio")
        self.select_audio_button.clicked.connect(self.select_audio)
        
        select_audio_layout.addWidget(self.select_audio_button)
        
        file_selection_layout.addWidget(example_frame, 1)
        file_selection_layout.addWidget(select_audio_frame, 1)
        
        audio_layout.addLayout(file_selection_layout)
        
 
        path_and_playback_layout = QHBoxLayout()
        path_and_playback_layout.setSpacing(15) 
        

        path_label_frame = QFrame()
        path_label_frame.setObjectName("card")
        path_label_layout = QVBoxLayout(path_label_frame) 
        path_label_layout.setContentsMargins(5,5,5,5)
        
        current_file_label = QLabel("🎵 Current Audio File:")
        current_file_label.setStyleSheet("color: #00d4ff; font-size: 12px;")
        self.audio_path_label = QLabel("No file selected")
        self.audio_path_label.setObjectName("audioPathLabel")
        self.audio_path_label.setAlignment(Qt.AlignCenter)
        
        path_label_layout.addWidget(current_file_label)
        path_label_layout.addWidget(self.audio_path_label)
        

        playback_buttons_frame = QFrame()
        playback_buttons_frame.setObjectName("card")
        playback_buttons_layout = QVBoxLayout(playback_buttons_frame)
        playback_buttons_layout.setContentsMargins(5,5,5,5)
        
        playback_row_layout = QHBoxLayout()
        playback_row_layout.setSpacing(10) 
        self.play_audio_button = QPushButton("Play")
        self.play_audio_button.setObjectName("playButton")
        self.play_audio_button.clicked.connect(self.reset_audio)
        self.play_audio_button.setMinimumHeight(35)
        
        self.stop_audio_button = QPushButton("Stop")
        self.stop_audio_button.setObjectName("stopButton")
        self.stop_audio_button.clicked.connect(self.stop_audio)
        self.stop_audio_button.setMinimumHeight(35)
        
        playback_row_layout.addWidget(self.play_audio_button)
        playback_row_layout.addWidget(self.stop_audio_button)
        
        playback_buttons_layout.addLayout(playback_row_layout)
        
        path_and_playback_layout.addWidget(path_label_frame, 2)
        path_and_playback_layout.addWidget(playback_buttons_frame, 1)
        
        audio_layout.addLayout(path_and_playback_layout)
        
        audio_group.setLayout(audio_layout)
        scroll_content_layout.addWidget(audio_group) 
        

        message_capacity_group = QGroupBox("💬 Message & Capacity")
        message_capacity_layout = QHBoxLayout()
        message_capacity_layout.setSpacing(15)
        

        message_input_frame = QFrame()
        message_input_frame.setObjectName("card")
        message_input_layout = QVBoxLayout(message_input_frame)
        message_input_layout.setContentsMargins(5,5,5,5)
        
        self.audio_message_input = QTextEdit()
        self.audio_message_input.setPlaceholderText("Enter your secret message here...\n\nSupports:\n• Multi-line text\n• Unicode characters\n• Special symbols")
        self.audio_message_input.setMinimumHeight(150) 
        
        message_input_layout.addWidget(self.audio_message_input)
        
        # Remaining Bits Label
        remaining_bits_frame = QFrame()
        remaining_bits_frame.setObjectName("card")
        remaining_bits_layout = QVBoxLayout(remaining_bits_frame) # Set parent for layout
        remaining_bits_layout.setContentsMargins(5,5,5,5)
        
        self.remaining_bits_label = QLabel("Capacity: N/A | Used: 0")
        self.remaining_bits_label.setObjectName("bitInfo")
        self.remaining_bits_label.setAlignment(Qt.AlignCenter)
        self.remaining_bits_label.setMinimumHeight(100) # Adjusted height
        
        remaining_bits_layout.addWidget(self.remaining_bits_label)
        
        message_capacity_layout.addWidget(message_input_frame, 2)
        message_capacity_layout.addWidget(remaining_bits_frame, 1)
        
        message_capacity_group.setLayout(message_capacity_layout)
        scroll_content_layout.addWidget(message_capacity_group) # Add to scroll content
        
        # === BOTTOM SECTION: Actions & Output ===
        actions_output_group = QGroupBox("🚀 Actions & Output")
        actions_output_layout = QVBoxLayout()
        actions_output_layout.setSpacing(10)
        
        # Action Buttons
        action_buttons_layout = QHBoxLayout()
        action_buttons_layout.setSpacing(20) # Increased spacing between buttons
        
        self.hide_audio_button = QPushButton("🔒 Hide") # Shortened text
        self.hide_audio_button.setObjectName("hideButton")
        self.hide_audio_button.clicked.connect(self.hide_message_in_audio)
        self.hide_audio_button.setMinimumHeight(40)
        
        self.extract_audio_button = QPushButton("🔓 Extract") # Shortened text
        self.extract_audio_button.setObjectName("extractButton")
        self.extract_audio_button.clicked.connect(self.extract_message_from_audio)
        self.extract_audio_button.setMinimumHeight(40)
        
        self.open_output_folder_button = QPushButton("📁 Output Folder") # Shortened text
        self.open_output_folder_button.setObjectName("folderButton")
        self.open_output_folder_button.clicked.connect(self.open_output_folder)
        self.open_output_folder_button.setMinimumHeight(40)
        
        action_buttons_layout.addStretch()
        action_buttons_layout.addWidget(self.hide_audio_button)
        action_buttons_layout.addWidget(self.extract_audio_button)
        action_buttons_layout.addWidget(self.open_output_folder_button)
        action_buttons_layout.addStretch()
        
        actions_output_layout.addLayout(action_buttons_layout)
        
        # Result Output Area
        output_label = QLabel("📝 Process Log:")
        output_label.setStyleSheet("color: #00d4ff; font-size: 12px; margin-bottom: 5px; margin-top: 10px;")
        self.result_output = QTextEdit()
        self.result_output.setReadOnly(True)
        self.result_output.setPlaceholderText("Process results and extracted messages will appear here...")
        self.result_output.setMinimumHeight(180) # Increased height for more log visibility
        
        actions_output_layout.addWidget(output_label)
        actions_output_layout.addWidget(self.result_output)
        
        actions_output_group.setLayout(actions_output_layout)
        scroll_content_layout.addWidget(actions_output_group) # Add to scroll content
        
        # Set the scroll_content_widget as the widget for the scroll area
        scroll_area.setWidget(scroll_content_widget)
        
        # Add the scroll area to the main layout
        main_layout.addWidget(scroll_area)
        # self.setLayout(main_layout) # This line is already present and correct

    def load_example_audio(self):
        current_directory = os.path.dirname(os.path.realpath(__file__))
        parent_directory = os.path.dirname(current_directory)
        example_folder_path = os.path.join(parent_directory, "audioexample")
        
        if os.path.exists(example_folder_path):
            audio_files = [f for f in os.listdir(example_folder_path) if f.endswith(('.wav', '.mp3', '.flac'))]
            self.example_audio_dropdown.clear()
            self.example_audio_dropdown.addItem("Select example audio")
            self.example_audio_dropdown.addItems(audio_files)
            if len(audio_files) > 0:
                self.example_audio_dropdown.setCurrentIndex(1) 
        else:
            self.result_output.append("<span style='color: #ff4444;'>❌ Example audio folder not found.</span>")

    def select_example_audio(self):
        current_directory = os.path.dirname(os.path.realpath(__file__))
        parent_directory = os.path.dirname(current_directory)
        example_folder_path = os.path.join(parent_directory, "audioexample")
        selected_audio = self.example_audio_dropdown.currentText()
        
        if selected_audio != "Select example audio":
            selected_audio_path = os.path.join(example_folder_path, selected_audio)
            self.selected_audio_path = selected_audio_path
            self.audio_path_label.setText(f"Selected: {os.path.basename(selected_audio_path)}")
            self.calculate_total_bits()
        else:
            self.selected_audio_path = "ไม่ได้เลือกไฟล์"
            self.audio_path_label.setText("No file selected")
            self.result_output.append("<span style='color: #ff4444;'>❌ No example audio selected.</span>")
            self.total_bits = 0
            self.show_used_bits() 

    def stop_audio(self):
        try:
            sd.stop()
            self.result_output.append("<span style='color: #ff4444;'>⏹️ Audio playback stopped.</span>")
        except Exception as e:
            self.result_output.append(f"<span style='color: #ff4444;'>❌ Error stopping audio: {e}</span>")

    def reset_audio(self):
        try:
            audio_file = self.selected_audio_path
            if audio_file != "ไม่ได้เลือกไฟล์" and os.path.exists(audio_file):
                data, samplerate = sf.read(audio_file)
                sd.stop()
                sd.play(data, samplerate)
                self.result_output.append("<span style='color: #00ff88;'>▶️ Playing audio...</span>")
            else:
                self.result_output.append("<span style='color: #ff4444;'>❌ Please select an audio file to play.</span>")
        except Exception as e:
            self.result_output.append(f"<span style='color: #ff4444;'>❌ Error playing audio: {e}</span>")

    def select_audio(self):
        options = QFileDialog.Options()
        audio_file, _ = QFileDialog.getOpenFileName(self, "Select Audio File", "",
                                                    "Audio Files (*.wav *.mp3 *.flac);;All Files (*)", options=options)
        if audio_file:
            self.selected_audio_path = audio_file
            self.audio_path_label.setText(f"Selected: {os.path.basename(audio_file)}")
           
            self.calculate_total_bits()
        else:
            self.selected_audio_path = "ไม่ได้เลือกไฟล์"
            self.audio_path_label.setText("No file selected")
           
            self.total_bits = 0
            self.show_used_bits() 

    def show_used_bits(self):
        message = self.audio_message_input.toPlainText()
        # Add null terminator for message length calculation
        binary_message = steganography.string_to_binary(message) + '00000000' 
        used_bits = len(binary_message)
        remaining_bits = max(self.total_bits - used_bits, 0)
        
        if self.total_bits == 0:
            self.remaining_bits_label.setText("Capacity: N/A | Used: 0")
            self.remaining_bits_label.setStyleSheet("""
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
            
        self.remaining_bits_label.setText(
            f"📊 Capacity: {self.total_bits:,} bits | Used: {used_bits:,} bits | Free: {remaining_bits:,} bits"
        )
        
        if remaining_bits < 0:
            self.remaining_bits_label.setStyleSheet("""
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
            self.remaining_bits_label.setStyleSheet("""
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

    def calculate_total_bits(self):
        try:
            audio_path = self.selected_audio_path
            if audio_path == "ไม่ได้เลือกไฟล์" or not os.path.exists(audio_path):
                self.total_bits = 0
                self.show_used_bits()
                return
            
            file_extension = os.path.splitext(audio_path)[1].lower()
            temp_wav_path = None
            use_path = audio_path

            if file_extension != ".wav":
                try:
                    audio = AudioSegment.from_file(audio_path)
                    temp_wav_path = os.path.join(os.path.dirname(audio_path), f"temp_{uuid.uuid4().hex}.wav")
                    audio.export(temp_wav_path, format="wav")
                    use_path = temp_wav_path
                except Exception as e:
                    raise RuntimeError(f"Failed to convert to WAV: {e}")

            with wave.open(use_path, 'rb') as wav_file:
                n_channels = wav_file.getnchannels()
                sampwidth = wav_file.getsampwidth()
                n_frames = wav_file.getnframes()
                

                self.total_bits = n_frames * n_channels * sampwidth * 8 
                
            if temp_wav_path and os.path.exists(temp_wav_path):
                os.remove(temp_wav_path)
                
            self.show_used_bits() 
           
        except Exception as e:
            print(f"[DEBUG] Error calculating bits: {e}")
            self.remaining_bits_label.setText("Error calculating capacity")
            self.remaining_bits_label.setStyleSheet("color: red;")
            self.result_output.append(f"<span style='color: #ff4444;'>❌ Error calculating audio capacity: {e}</span>")
            self.total_bits = 0
            self.show_used_bits() 

    def hide_message_in_audio(self):
        message = self.audio_message_input.toPlainText()
        audio_path = self.selected_audio_path
        
        if audio_path == "ไม่ได้เลือกไฟล์" or not os.path.exists(audio_path):
            self.result_output.append("<span style='color: #ff4444;'>❌ Please select an audio file first!</span>")
            return
        if not message.strip():
            self.result_output.append("<span style='color: #ff4444;'>❌ Please enter a message to hide!</span>")
            return
            
        try:
            file_extension = os.path.splitext(audio_path)[1].lower()
            temp_wav_path = None
            use_path = audio_path

            if file_extension != ".wav":
                audio = AudioSegment.from_file(audio_path)
                temp_wav_path = os.path.join(os.path.dirname(audio_path), f"temp_hide_{uuid.uuid4().hex}.wav")
                audio.export(temp_wav_path, format="wav")
                use_path = temp_wav_path

            with wave.open(use_path, 'rb') as audio_file:
                n_channels = audio_file.getnchannels()
                sampwidth = audio_file.getsampwidth()
                framerate = audio_file.getframerate()
                n_frames = audio_file.getnframes()
                frames = audio_file.readframes(n_frames)
                audio_data = np.frombuffer(frames, dtype=np.uint8) # Read as bytes for LSB

            binary_message = steganography.string_to_binary(message) + '00000000' # Add null terminator
            
            if len(binary_message) > len(audio_data):
                raise ValueError(f"Message too long! Max bits: {len(audio_data):,} bits. Your message: {len(binary_message):,} bits.")

            modified_data = audio_data.copy()
            for i in range(len(binary_message)):
                modified_data[i] = (modified_data[i] & 254) | int(binary_message[i]) # LSB hiding

            current_directory = os.path.dirname(os.path.realpath(__file__))
            parent_directory = os.path.dirname(current_directory)
            directory = os.path.join(parent_directory, "audioexample", "output")
            os.makedirs(directory, exist_ok=True)
            
            filename = os.path.splitext(os.path.basename(audio_path))[0]
            output_path = os.path.join(directory, f"{filename}_hidden.wav")

            with wave.open(output_path, 'wb') as output_file:
                output_file.setnchannels(n_channels)
                output_file.setsampwidth(sampwidth)
                output_file.setframerate(framerate)
                output_file.writeframes(modified_data.tobytes())

            if temp_wav_path and os.path.exists(temp_wav_path):
                os.remove(temp_wav_path)
                
            self.result_output.append(f"<span style='color: #00ff88;'>✅ Message hidden in: <font color='#00d4ff'>{os.path.basename(output_path)}</font></span>")
        except Exception as e:
            self.result_output.append(f"<span style='color: #ff4444;'>❌ Error hiding message: {e}</span>")

    def extract_message_from_audio(self):
        audio_path = self.selected_audio_path
        if audio_path == "ไม่ได้เลือกไฟล์" or not os.path.exists(audio_path):
            self.result_output.append("<span style='color: #ff4444;'>❌ Please select an audio file first!</span>")
            return
        try:
            file_extension = os.path.splitext(audio_path)[1].lower()
            temp_wav_path = None
            use_path = audio_path

            if file_extension != ".wav":
                audio = AudioSegment.from_file(audio_path)
                temp_wav_path = os.path.join(os.path.dirname(audio_path), f"temp_extract_{uuid.uuid4().hex}.wav")
                audio.export(temp_wav_path, format="wav")
                use_path = temp_wav_path

            with wave.open(use_path, 'rb') as audio_file:
                frames = audio_file.readframes(audio_file.getnframes())
                audio_data = np.frombuffer(frames, dtype=np.uint8)

            binary_message = ''
            for byte in audio_data:
                binary_message += str(byte & 1)
                if len(binary_message) >= 8 and binary_message[-8:] == '00000000': 
                    break
            
            message = steganography.binary_to_string(binary_message)
            
            if temp_wav_path and os.path.exists(temp_wav_path):
                os.remove(temp_wav_path)

            if message.strip():
                self.result_output.append(
                    f"<span style='color: #00ff88;'>✅ Extracted message:</span><br>"
                    f"<div style='background: rgba(0, 255, 136, 0.1); padding: 8px; "
                    f"border-radius: 6px; margin: 3px 0; border-left: 3px solid #00ff88;'>"
                    f"<span style='color: #ffffff;'>{message}</span></div>"
                )
            else:
                self.result_output.append("<span style='color: #ff4444;'>❌ No hidden message found in this audio.</span>")
        except Exception as e:
            self.result_output.append(f"<span style='color: #ff4444;'>❌ Error extracting message: {e}</span>")

    def open_output_folder(self):
        current_directory = os.path.dirname(os.path.realpath(__file__))
        parent_directory = os.path.dirname(current_directory)
        output_path = os.path.join(parent_directory, "audioexample", "output")
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        QDesktopServices.openUrl(QUrl.fromLocalFile(output_path))
        

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            if os.path.isfile(file_path) and file_path.lower().endswith(('.wav', '.mp3', '.flac')):
                self.selected_audio_path = file_path
                self.audio_path_label.setText(f"Selected: {os.path.basename(file_path)}")
                
                self.calculate_total_bits()
            else:
                self.result_output.append("<span style='color: #ff4444;'>❌ Dropped file is not a supported audio format!</span>")





