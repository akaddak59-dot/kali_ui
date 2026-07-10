#!/usr/bin/env python3
"""
Kali Linux Simulator - Login Screen
Authenticates user before granting access to the desktop
"""

import hashlib
import json
from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QGraphicsDropShadowEffect, QMessageBox
)
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QEasingCurve, QTimer
from PySide6.QtGui import QFont, QPixmap, QIcon, QColor


class LoginScreen(QWidget):
    """Login screen with Kali Linux theme"""
    
    def __init__(self, session_manager):
        super().__init__()
        self.session = session_manager
        self.attempts = 0
        self.max_attempts = 5
        self.setup_ui()
        
    def setup_ui(self):
        """Build the login interface"""
        # Main layout
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        
        # Center container
        container = QFrame()
        container.setObjectName("loginContainer")
        container.setFixedWidth(420)
        container.setStyleSheet("""
            #loginContainer {
                background-color: rgba(15, 15, 15, 220);
                border: 1px solid #00ff00;
                border-radius: 12px;
                padding: 30px;
            }
        """)
        
        # Shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(40)
        shadow.setColor(QColor(0, 255, 0, 80))
        shadow.setOffset(0, 0)
        container.setGraphicsEffect(shadow)
        
        container_layout = QVBoxLayout()
        container_layout.setSpacing(15)
        
        # Logo / Title
        title_label = QLabel("KALI LINUX")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 32px;
            font-weight: bold;
            color: #00ff00;
            letter-spacing: 6px;
        """)
        container_layout.addWidget(title_label)
        
        subtitle = QLabel("Security Testing Platform")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("""
            font-size: 12px;
            color: #888888;
            letter-spacing: 3px;
            margin-bottom: 20px;
        """)
        container_layout.addWidget(subtitle)
        
        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("border: 1px solid #00ff00; opacity: 0.3;")
        container_layout.addWidget(sep)
        
        # Username
        username_label = QLabel("USERNAME")
        username_label.setStyleSheet("color: #00ff00; font-size: 11px; letter-spacing: 2px;")
        container_layout.addWidget(username_label)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("root")
        self.username_input.setText("root")
        self.username_input.setStyleSheet("""
            QLineEdit {
                background-color: #1a1a1a;
                border: 1px solid #333333;
                border-radius: 4px;
                padding: 10px;
                color: #00ff00;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #00ff00;
            }
        """)
        container_layout.addWidget(self.username_input)
        
        # Password
        password_label = QLabel("PASSWORD")
        password_label.setStyleSheet("color: #00ff00; font-size: 11px; letter-spacing: 2px;")
        container_layout.addWidget(password_label)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("""
            QLineEdit {
                background-color: #1a1a1a;
                border: 1px solid #333333;
                border-radius: 4px;
                padding: 10px;
                color: #00ff00;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #00ff00;
            }
        """)
        container_layout.addWidget(self.password_input)
        
        # Login button
        self.login_btn = QPushButton("LOGIN")
        self.login_btn.setCursor(Qt.PointingHandCursor)
        self.login_btn.setStyleSheet("""
            QPushButton {
                background-color: #00ff00;
                color: #000000;
                border: none;
                border-radius: 4px;
                padding: 12px;
                font-size: 14px;
                font-weight: bold;
                letter-spacing: 3px;
                margin-top: 15px;
            }
            QPushButton:hover {
                background-color: #00cc00;
            }
            QPushButton:pressed {
                background-color: #009900;
            }
        """)
        self.login_btn.clicked.connect(self.authenticate)
        container_layout.addWidget(self.login_btn)
        
        # Status label
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #ff4444; font-size: 11px; margin-top: 5px;")
        container_layout.addWidget(self.status_label)
        
        container.setLayout(container_layout)
        layout.addWidget(container)
        
        # Version info at bottom
        version_label = QLabel("v2024.3 | Built for authorized security testing only")
        version_label.setAlignment(Qt.AlignCenter)
        version_label.setStyleSheet("""
            color: #555555;
            font-size: 10px;
            position: absolute;
            bottom: 20px;
        """)
        
        main_layout = QVBoxLayout()
        main_layout.addLayout(layout)
        main_layout.addStretch()
        main_layout.addWidget(version_label)
        
        self.setLayout(main_layout)
        
        # Connect Enter key
        self.password_input.returnPressed.connect(self.authenticate)
        self.username_input.returnPressed.connect(lambda: self.password_input.setFocus())
        
    def authenticate(self):
        """Validate credentials"""
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        if not username or not password:
            self.status_label.setText("ERROR: Username and password required")
            self.shake_animation()
            return
        
        # Simple authentication (demo purposes - real auth would use proper validation)
        valid_credentials = {
            "root": "toor",
            "kali": "kali",
            "user": "password"
        }
        
        if username in valid_credentials and password == valid_credentials[username]:
            self.status_label.setText("")
            self.status_label.setStyleSheet("color: #00ff00; font-size: 11px;")
            self.status_label.setText("ACCESS GRANTED")
            
            # Animate and login
            QTimer.singleShot(500, lambda: self.session.login(username, "root" if username == "root" else "user"))
        else:
            self.attempts += 1
            remaining = self.max_attempts - self.attempts
            
            if self.attempts >= self.max_attempts:
                self.status_label.setText("ACCOUNT LOCKED - Too many attempts")
                self.login_btn.setEnabled(False)
                QTimer.singleShot(15000, lambda: self._unlock())
            else:
                self.status_label.setText(f"ACCESS DENIED - {remaining} attempts remaining")
                self.shake_animation()
                
    def shake_animation(self):
        """Shake animation on failed login"""
        anim = QPropertyAnimation(self, b"pos")
        anim.setDuration(300)
        anim.setLoopCount(1)
        anim.setEasingCurve(QEasingCurve.InOutQuad)
        
        current = self.pos()
        anim.setStartValue(current)
        values = [current + QtCore.QPoint(10, 0), current - QtCore.QPoint(10, 0)]
        anim.setKeyValueAt(0.25, values[0])
        anim.setKeyValueAt(0.75, values[1])
        anim.setEndValue(current)
        anim.start()
        
    def _unlock(self):
        self.attempts = 0
        self.login_btn.setEnabled(True)
        self.status_label.setText("")
        
    def reset_fields(self):
        """Reset login fields"""
        self.username_input.setText("root")
        self.password_input.clear()
        self.status_label.setText("")
        self.attempts = 0
        self.login_btn.setEnabled(True)
