#!/usr/bin/env python3
"""
Kali Linux Simulator - Settings Dialog
System configuration and preferences
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QLabel, QPushButton, QSlider, QCheckBox, QComboBox,
    QLineEdit, QColorDialog, QFontDialog, QSpinBox,
    QGroupBox, QRadioButton, QButtonGroup, QFormLayout,
    QFrame, QListWidget, QListWidgetItem
)
from PySide6.QtCore import Qt, QSettings, Signal, QSize
from PySide6.QtGui import QFont, QColor, QPalette, QIcon


class SettingsDialog(QDialog):
    """System settings dialog"""
    
    settings_changed = Signal()
    
    def __init__(self, parent=None, session_manager=None):
        super().__init__(parent)
        self.session = session_manager
        self.settings = QSettings("KaliSim", "KaliLinuxSimulator")
        self.setWindowTitle("System Settings")
        self.setGeometry(200, 200, 700, 500)
        self.setStyleSheet("""
            QDialog {
                background-color: #0a0a0a;
                color: #cccccc;
            }
        """)
        
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        """Setup settings UI with tabs"""
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # Title
        title = QLabel("⚙ SYSTEM SETTINGS")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #00ff00; letter-spacing: 4px; padding: 10px;")
        layout.addWidget(title)
        
        # Tab widget
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #333333;
                background-color: #111111;
            }
            QTabBar::tab {
                background-color: #1a1a1a;
                color: #888888;
                border: 1px solid #333333;
                padding: 8px 20px;
            }
            QTabBar::tab:selected {
                background-color: #111111;
                color: #00ff00;
                border-bottom: 2px solid #00ff00;
            }
        """)
        
        # Appearance tab
        appearance_tab = self.create_appearance_tab()
        tabs.addTab(appearance_tab, "🎨 Appearance")
        
        # Terminal tab
        terminal_tab = self.create_terminal_tab()
        tabs.addTab(terminal_tab, "🖥 Terminal")
        
        # Network tab
        network_tab = self.create_network_tab()
        tabs.addTab(network_tab, "🌐 Network")
        
        # Security tab
        security_tab = self.create_security_tab()
        tabs.addTab(security_tab, "🔒 Security")
        
        # About tab
        about_tab = self.create_about_tab()
        tabs.addTab(about_tab, "ℹ About")
        
        layout.addWidget(tabs, 1)
        
        # Bottom buttons
        btn_layout = QHBoxLayout()
        
        apply_btn = QPushButton("Apply")
        apply_btn.setStyleSheet("""
            QPushButton {
                background-color: #003300;
                color: #00ff00;
                border: 1px solid #00ff00;
                padding: 8px 20px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #005500;
            }
        """)
        apply_btn.clicked.connect(self.apply_settings)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #330000;
                color: #ff4444;
                border: 1px solid #ff4444;
                padding: 8px 20px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #550000;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addStretch()
        btn_layout.addWidget(apply_btn)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
    
    def create_appearance_tab(self):
        """Create appearance settings tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Theme
        theme_group = QGroupBox("Theme")
        theme_group.setStyleSheet("""
            QGroupBox {
                color: #00ff00;
                border: 1px solid #333333;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 15px;
                font-weight: bold;
            }
        """)
        theme_layout = QVBoxLayout()
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Kali Dark (Default)", "Classic Green", "Matrix", "Night Vision", "Stealth Mode"])
        self.theme_combo.setStyleSheet("""
            QComboBox {
                background-color: #1a1a1a;
                color: #00ff00;
                border: 1px solid #333333;
                padding: 5px;
                border-radius: 3px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #1a1a1a;
                color: #00ff00;
                selection-background-color: #003300;
            }
        """)
        theme_layout.addWidget(self.theme_combo)
        theme_group.setLayout(theme_layout)
        layout.addWidget(theme_group)
        
        # Font settings
        font_group = QGroupBox("Font Settings")
        font_group.setStyleSheet(theme_group.styleSheet())
        font_layout = QFormLayout()
        
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 24)
        self.font_size_spin.setValue(11)
        self.font_size_spin.setStyleSheet("""
            QSpinBox {
                background-color: #1a1a1a;
                color: #00ff00;
                border: 1px solid #333333;
                padding: 5px;
            }
        """)
        font_layout.addRow("Terminal Font Size:", self.font_size_spin)
        
        font_group.setLayout(font_layout)
        layout.addWidget(font_group)
        
        # Desktop settings
        desktop_group = QGroupBox("Desktop")
        desktop_group.setStyleSheet(theme_group.styleSheet())
        desktop_layout = QVBoxLayout()
        
        self.show_icons_check = QCheckBox("Show Desktop Icons")
        self.show_icons_check.setChecked(True)
        self.show_icons_check.setStyleSheet("color: #cccccc;")
        desktop_layout.addWidget(self.show_icons_check)
        
        self.transparency_slider = QSlider(Qt.Horizontal)
        self.transparency_slider.setRange(50, 255)
        self.transparency_slider.setValue(200)
        self.transparency_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                background: #333333;
                height: 6px;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #00ff00;
                width: 14px;
                height: 14px;
                margin: -5px 0;
                border-radius: 7px;
            }
        """)
        desktop_layout.addWidget(QLabel("Window Transparency:"))
        desktop_layout.addWidget(self.transparency_slider)
        
        desktop_group.setLayout(desktop_layout)
        layout.addWidget(desktop_group)
        
        layout.addStretch()
        tab.setLayout(layout)
        return tab
    
    def create_terminal_tab(self):
        """Create terminal settings tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Shell settings
        shell_group = QGroupBox("Shell Configuration")
        shell_group.setStyleSheet("""
            QGroupBox {
                color: #00ff00;
                border: 1px solid #333333;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 15px;
                font-weight: bold;
            }
        """)
        shell_layout = QFormLayout()
        
        self.shell_combo = QComboBox()
        self.shell_combo.addItems(["/bin/bash", "/bin/zsh", "/bin/sh", "/bin/dash"])
        self.shell_combo.setStyleSheet("""
            QComboBox {
                background-color: #1a1a1a;
                color: #00ff00;
                border: 1px solid #333333;
                padding: 5px;
            }
            QComboBox::drop-down { border: none; }
            QComboBox QAbstractItemView {
                background-color: #1a1a1a;
                color: #00ff00;
                selection-background-color: #003300;
            }
        """)
        shell_layout.addRow("Default Shell:", self.shell_combo)
        
        shell_group.setLayout(shell_layout)
        layout.addWidget(shell_group)
        
        # History
        history_group = QGroupBox("Command History")
        history_group.setStyleSheet(shell_group.styleSheet())
        history_layout = QFormLayout()
        
        self.history_size_spin = QSpinBox()
        self.history_size_spin.setRange(100, 10000)
        self.history_size_spin.setValue(1000)
        self.history_size_spin.setStyleSheet("""
            QSpinBox {
                background-color: #1a1a1a;
                color: #00ff00;
                border: 1px solid #333333;
                padding: 5px;
            }
        """)
        history_layout.addRow("History Size:", self.history_size_spin)
        
        history_group.setLayout(history_layout)
        layout.addWidget(history_group)
        
        layout.addStretch()
        tab.setLayout(layout)
        return tab
    
    def create_network_tab(self):
        """Create network settings tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Proxy
        proxy_group = QGroupBox("Proxy Configuration")
        proxy_group.setStyleSheet("""
            QGroupBox {
                color: #00ff00;
                border: 1px solid #333333;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 15px;
                font-weight: bold;
            }
        """)
        proxy_layout = QFormLayout()
        
        self.proxy_host = QLineEdit()
        self.proxy_host.setPlaceholderText("127.0.0.1")
        self.proxy_host.setStyleSheet("""
            QLineEdit {
                background-color: #1a1a1a;
                color: #00ff00;
                border: 1px solid #333333;
                padding: 5px;
            }
        """)
        proxy_layout.addRow("Proxy Host:", self.proxy_host)
        
        self.proxy_port = QSpinBox()
        self.proxy_port.setRange(1, 65535)
        self.proxy_port.setValue(8080)
        self.proxy_port.setStyleSheet("""
            QSpinBox {
                background-color: #1a1a1a;
                color: #00ff00;
                border: 1px solid #333333;
                padding: 5px;
            }
        """)
        proxy_layout.addRow("Proxy Port:", self.proxy_port)
        
        self.proxy_check = QCheckBox("Enable Proxy")
        self.proxy_check.setStyleSheet("color: #cccccc;")
        proxy_layout.addRow("", self.proxy_check)
        
        proxy_group.setLayout(proxy_layout)
        layout.addWidget(proxy_group)
        
        layout.addStretch()
        tab.setLayout(layout)
        return tab
    
    def create_security_tab(self):
        """Create security settings tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Session
        session_group = QGroupBox("Session Security")
        session_group.setStyleSheet("""
            QGroupBox {
                color: #00ff00;
                border: 1px solid #333333;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 15px;
                font-weight: bold;
            }
        """)
        session_layout = QVBoxLayout()
        
        self.auto_lock_check = QCheckBox("Auto-lock on inactivity")
        self.auto_lock_check.setChecked(True)
        self.auto_lock_check.setStyleSheet("color: #cccccc;")
        session_layout.addWidget(self.auto_lock_check)
        
        self.clear_logs_check = QCheckBox("Clear logs on logout")
        self.clear_logs_check.setChecked(True)
        self.clear_logs_check.setStyleSheet("color: #cccccc;")
        session_layout.addWidget(self.clear_logs_check)
        
        session_group.setLayout(session_layout)
        layout.addWidget(session_group)
        
        layout.addStretch()
        tab.setLayout(layout)
        return tab
    
    def create_about_tab(self):
        """Create about tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        
        about_text = """
        <div style='text-align: center;'>
            <h1 style='color: #00ff00;'>Kali Linux Simulator</h1>
            <h3 style='color: #888888;'>Security Testing Platform</h3>
            <p style='color: #aaaaaa;'>Version 2024.3</p>
            <br>
            <p style='color: #666666;'>
            Built with Python 3 & PySide6<br>
            For authorized security testing only<br><br>
            ⚠ WARNING: For authorized use only.<br>
            Unauthorized access is illegal.
            </p>
        </div>
        """
        
        label = QLabel(about_text)
        label.setTextFormat(Qt.RichText)
        label.setWordWrap(True)
        layout.addWidget(label)
        
        tab.setLayout(layout)
        return tab
    
    def load_settings(self):
        """Load saved settings"""
        # Would load from QSettings in production
        pass
    
    def apply_settings(self):
        """Apply settings and close"""
        # Save settings
        self.settings.setValue("theme", self.theme_combo.currentText())
        self.settings.setValue("font_size", self.font_size_spin.value())
        self.settings.setValue("show_icons", self.show_icons_check.isChecked())
        self.settings.setValue("transparency", self.transparency_slider.value())
        self.settings.setValue("shell", self.shell_combo.currentText())
        self.settings.setValue("history_size", self.history_size_spin.value())
        self.settings.setValue("proxy_host", self.proxy_host.text())
        self.settings.setValue("proxy_port", self.proxy_port.value())
        self.settings.setValue("proxy_enabled", self.proxy_check.isChecked())
        self.settings.setValue("auto_lock", self.auto_lock_check.isChecked())
        self.settings.setValue("clear_logs", self.clear_logs_check.isChecked())
        
        self.settings_changed.emit()
        self.accept()
