import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QLabel, QFrame, QPushButton, QSystemTrayIcon, QMenu,QMessageBox,
    QSplashScreen
)
from PyQt5.QtGui import QIcon, QFont, QPainter, QPixmap
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QCoreApplication
import psutil
import tabs.image_tab as image_tab
import tabs.audio_tab as audio_tab
import tabs.file_info_tab as info_tab
import tabs.encryption_tab as encryption_tab
import tabs.file_and_FILE as file_and_FILE
import tabs.video_tab as video_tab
import tabs.integrated_mode_tab as integrated_mode_tab
import tabs.pgp_tab as pgp_tab

class MarqueeLabel(QLabel):
    def __init__(self, text, parent=None, speed=30):
        super().__init__(parent)
        self._text = text
        self.offset = 0
        self.speed = speed
        self.setFixedHeight(40)
        self.setStyleSheet("color: #00d4ff; font-size: 28px; font-weight: bold; letter-spacing: 3px; background: transparent;")
        self.setText("")
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._scroll_text)
        self.timer.start(self.speed)

    def _scroll_text(self):
        self.offset += 2
        if self.offset > self.fontMetrics().width(self._text):
            self.offset = 0
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(self.palette().windowText().color())
        text_width = self.fontMetrics().width(self._text)
        x = -self.offset
        y = self.height() // 2 + self.fontMetrics().ascent() // 2 - 4
        painter.drawText(x, y, self._text)
        painter.drawText(x + text_width + 50, y, self._text)

class EnhancedSteganographyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SIENG : Secure Incognito ENcryption Guard")
        self.setGeometry(100, 100, 1400, 900)
        
        self.setWindowIcon(QIcon("icom.png"))
        self.setMinimumSize(1200, 800)
        self.current_file_path = None
        self.setup_styles()
        self.initUI()
        self.setup_system_tray()
        self.memory_timer = QTimer(self)
        self.memory_timer.timeout.connect(self.update_memory_usage)
        self.memory_timer.start(1000) 
        

    def setup_styles(self):
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0c0c0c, stop:0.3 #1a1a2e, stop:0.7 #16213e, stop:1 #0f3460);
                color: #ffffff;
                font-family: 'Segoe UI', 'Roboto', Arial, sans-serif;
            }
            QFrame#headerFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1a1a2e, stop:0.5 #16213e, stop:1 #0f3460);
                border-radius: 15px;
                border: 2px solid #00d4ff;
                margin: 10px;
            }
            QTabWidget {
                background: transparent;
                border: none;
            }
            QTabWidget::pane {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2d2d44, stop:1 #1e1e2e);
                border: 2px solid #444;
                border-radius: 12px;
                margin-top: 5px;
            }
            QTabBar {
                background: transparent;
            }
            QTabBar::tab {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3a3a54, stop:1 #2a2a3e);
                color: #cccccc;
                border: 2px solid #444;
                border-bottom: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                padding: 12px 20px;
                margin-right: 2px;
                font-size: 13px;
                font-weight: bold;
                min-width: 120px;
            }
            QTabBar::tab:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4a4a64, stop:1 #3a3a4e);
                color: #00d4ff;
                border-color: #00d4ff;
            }
            QTabBar::tab:selected {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #00d4ff, stop:1 #0099cc);
                color: #ffffff;
                border-color: #00d4ff;
                font-weight: bold;
            }
            QTabBar::tab:!selected {
                margin-top: 3px;
            }
            QFrame#statusFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2d2d44, stop:1 #1e1e2e);
                border: 1px solid #444;
                border-radius: 8px;
                margin: 5px;
                padding: 5px;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4a90e2, stop:1 #357abd);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 12px;
                font-weight: bold;
                min-height: 25px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5ba0f2, stop:1 #4585c7);
            }
            QPushButton:pressed {
                background: #2d5aa0;
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

    def initUI(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        header_frame = self.create_header()
        main_layout.addWidget(header_frame)
        content_frame = QFrame()
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(15, 10, 15, 10)
        tabs = self.create_tab_widget()
        content_layout.addWidget(tabs)
        content_frame.setLayout(content_layout)
        main_layout.addWidget(content_frame, 1)
        status_frame = self.create_status_bar()
        main_layout.addWidget(status_frame)
        self.setLayout(main_layout)

    def create_header(self):
        header_frame = QFrame()
        header_frame.setObjectName("headerFrame")
        header_frame.setFixedHeight(100)
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(20, 10, 20, 10)
        left_layout = QVBoxLayout()
        title_label = MarqueeLabel("🔒 SECURE INCOGNITO ENCRYPTION GUARD", speed=25)
        subtitle_label = QLabel("Advanced Multi-Format Steganography & Encryption Suite")
        subtitle_label.setStyleSheet("""
            QLabel {
                color: #888;
                font-size: 14px;
                font-style: italic;
                background: transparent;
                border: none;
            }
        """)
        left_layout.addWidget(title_label)
        left_layout.addWidget(subtitle_label)
        left_layout.addStretch()
        right_layout = QVBoxLayout()
        right_layout.setAlignment(Qt.AlignTop | Qt.AlignRight)
        quick_actions_layout = QHBoxLayout()
        self.help_btn = QPushButton("❓")
        self.help_btn.setFixedSize(45, 45)
        self.help_btn.clicked.connect(self.show_help)
        self.settings_btn = QPushButton("⚙️")
        self.settings_btn.setFixedSize(50, 50)
        self.settings_btn.clicked.connect(self.show_settings)
        for btn in [ self.help_btn, self.settings_btn]:
            btn.setStyleSheet("""
                QPushButton {
                    background: rgba(255, 255, 255, 0.1);
                    border: 1px solid #555;
                    border-radius: 17px;
                    font-size: 16px;
                }
                QPushButton:hover {
                    background: rgba(255, 255, 255, 0.2);
                }
            """)
        quick_actions_layout.addWidget(self.help_btn)
        quick_actions_layout.addWidget(self.settings_btn)
        version_label = QLabel("v2.0.1 | Build 2024.01")
        version_label.setStyleSheet("""
            QLabel {
                color: #666;
                font-size: 11px;
                background: transparent;
                border: none;
                margin-top: 10px;
            }
        """)
        version_label.setAlignment(Qt.AlignRight)
        right_layout.addLayout(quick_actions_layout)
        right_layout.addWidget(version_label)
        header_layout.addLayout(left_layout, 1)
        header_layout.addLayout(right_layout)
        header_frame.setLayout(header_layout)
        return header_frame

    def create_tab_widget(self):
        tabs = QTabWidget()
        tabs.setStyleSheet("""
    QTabWidget::pane {
        border: none;
    }""")
        tab_configs = [
            {
                'widget': image_tab.ImageTab(),
                'title': '🖼️ Image',
                'tooltip': 'Hide and extract messages from image files'
            },
            {
                'widget': audio_tab.AudioTab(),
                'title': '🎵 Audio',
                'tooltip': 'Hide and extract messages from audio files'
            },
            {
                'widget': video_tab.VideoTab(),
                'title': '🎬 Video',
                'tooltip': 'Hide and extract messages from video files'
            },
            {
                'widget': info_tab.FileInfoTab(),
                'title': '📋 Metadata',
                'tooltip': 'Hide messages in file metadata and tags'
            },
            {
                'widget': file_and_FILE.FileAndFileTab(),
                'title': '📁 File-to-File',
                'tooltip': 'Hide files within other files'
            },
            {
                'widget': encryption_tab.EncryptionTab(),
                'title': '🔐 Encryption',
                'tooltip': 'Advanced encryption and decryption tools'
            },
            {
                'widget': pgp_tab.PGPTab(),
                'title': '🔑 PGP Security',
                'tooltip': 'PGP encryption and digital signatures'
            },
            {
                'widget': integrated_mode_tab.IntegrationTab(),
                'title': '🔗 Integration',
                'tooltip': 'Combined steganography and encryption'
            }
        ]
        for config in tab_configs:
            tab_widget = config['widget']
            tabs.addTab(tab_widget, config['title'])
            tab_index = tabs.count() - 1
            tabs.setTabToolTip(tab_index, config['tooltip'])
        self.image_tab = tab_configs[0]['widget']
        self.audio_tab = tab_configs[1]['widget']
        self.video_tab = tab_configs[2]['widget']
        self.info_tab = tab_configs[3]['widget']
        self.file_tab = tab_configs[4]['widget']
        self.encryption_tab = tab_configs[5]['widget']
        self.pgp_tab = tab_configs[6]['widget']
        self.integrated_mode_tab = tab_configs[7]['widget']
        return tabs

    def create_status_bar(self):
        import psutil
        status_frame = QFrame()
        status_frame.setObjectName("statusFrame")
        status_frame.setFixedHeight(40)
        status_frame.setStyleSheet("background: transparent; border: none;")
        status_layout = QHBoxLayout()
        status_layout.setContentsMargins(0, 0, 0, 0)
        self.status_label = QLabel("🟢 Ready")
        self.status_label.setStyleSheet("""
            QLabel {
                background: transparent;
                border: none;
                color: #00ff88;
                font-weight: bold;
                font-size: 12px;
            }
        """)
        self.memory_label = QLabel("💾 Memory: 0.0 MB")
        self.memory_label.setStyleSheet("""
            QLabel {
                background: transparent;
                border: none;
                color: #00d4ff;
                font-size: 11px;
            }
        """)
        security_label = QLabel("🛡️ Security: Active")
        security_label.setStyleSheet("""
            QLabel {
                background: transparent;
                border: none;
                color: #00ff88;
                font-size: 11px;
            }
        """)
        separator_label = QLabel("|")
        separator_label.setStyleSheet("""
            QLabel {
                background: transparent;
                border: none;
                color: #888;
                font-size: 12px;
            }
        """)
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        status_layout.addWidget(self.memory_label)
        status_layout.addWidget(separator_label)
        status_layout.addWidget(security_label)
        status_frame.setLayout(status_layout)
        from PyQt5.QtCore import QTimer
        self.memory_timer = QTimer(self)
        self.memory_timer.timeout.connect(self.update_memory_usage)
        self.memory_timer.start(1000)
        return status_frame

    def update_memory_usage(self):
        import psutil
        process = psutil.Process()
        mem_bytes = process.memory_info().rss
        mem_mb = mem_bytes / (1024 * 1024)
        self.memory_label.setText(f"💾 Memory: {mem_mb:.1f} MB")

    def setup_system_tray(self):
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.tray_icon = QSystemTrayIcon(self)
            self.tray_icon.setIcon(QIcon("myicon_in.ico"))
            tray_menu = QMenu()
            show_action = tray_menu.addAction("Show SIENG")
            show_action.triggered.connect(self.show)
            tray_menu.addSeparator()
            quit_action = tray_menu.addAction("Exit")
            quit_action.triggered.connect(QApplication.instance().quit)
            self.tray_icon.setContextMenu(tray_menu)
            self.tray_icon.show()
            self.tray_icon.activated.connect(self.tray_icon_activated)

    def tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.show()
            self.raise_()
            self.activateWindow()

    def show_help(self):
        help_text = (
            "🔒 SECURE INCOGNITO ENCRYPTION GUARD\n"
            "This application allows you to:\n"
            "• Hide & extract messages from images, audio, video, and files\n"
            "• Encrypt / decrypt sensitive data\n"
            "• Use PGP for digital signatures\n"
            "For more help, visit: https://yourapp.help "
        )
        QMessageBox.information(self, "Help & User Guide", help_text)

    def show_settings(self):
        self.status_label.setText("🔵 Settings - Feature coming soon...")
        QTimer.singleShot(3000, lambda: self.status_label.setText("🟢 Ready"))

    def closeEvent(self, event):
        if hasattr(self, 'tray_icon') and self.tray_icon.isVisible():
            self.hide()
            self.tray_icon.showMessage(
                "SIENG",
                "Application minimized to tray",
                QSystemTrayIcon.Information,
                2000
            )
            event.ignore()
        else:
            event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  
    
    
    app.setApplicationName("SIENG")
    app.setApplicationVersion("2.0.1")
    app.setOrganizationName("Security Solutions")

   
    splash_pix = QPixmap("myicon_in.ico")  
    if splash_pix.isNull():
        splash_pix = QPixmap(400, 200)
        splash_pix.fill(Qt.darkBlue)
        painter = QPainter(splash_pix)
        painter.setPen(Qt.white)
        painter.setFont(QFont("Arial", 24, QFont.Bold))
        painter.drawText(splash_pix.rect(), Qt.AlignCenter, "SIENG Loading...")
        painter.end()
    else:
        splash_pix = splash_pix.scaled(800, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation)
       

    splash = QSplashScreen(splash_pix)
    splash.show()

    
    QCoreApplication.processEvents()
    QTimer.singleShot(5000, splash.close)

   
    window = EnhancedSteganographyApp()
    window.show()

    sys.exit(app.exec_())