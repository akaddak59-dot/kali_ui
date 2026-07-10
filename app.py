#!/usr/bin/env python3
"""
Kali Linux Simulator - Main Entry Point
Application that simulates Kali Linux GUI with integrated security tools
"""

import sys
import os
import subprocess
import json
import shlex
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QStackedWidget, QSplashScreen, 
    QMessageBox, QSystemTrayIcon, QMenu
)
from PySide6.QtCore import Qt, QTimer, QDir, Signal, QObject, QThread
from PySide6.QtGui import QIcon, QPixmap, QAction, QFont

# Import app modules
from login import LoginScreen
from desktop import DesktopScreen


class SessionManager(QObject):
    """Manages user session state"""
    
    logged_in = Signal()
    logged_out = Signal()
    
    def __init__(self):
        super().__init__()
        self.username = None
        self.role = None
        
    def login(self, username: str, role: str = "root"):
        self.username = username
        self.role = role
        self.logged_in.emit()
        
    def logout(self):
        self.username = None
        self.role = None
        self.logged_out.emit()
        
    @property
    def is_authenticated(self):
        return self.username is not None


class KaliSimulator(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.session = SessionManager()
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        # Initialize screens
        self.login_screen = LoginScreen(self.session)
        self.desktop_screen = DesktopScreen(self.session)
        
        # Add screens to stack
        self.stacked_widget.addWidget(self.login_screen)   # index 0
        self.stacked_widget.addWidget(self.desktop_screen) # index 1
        
        # Connect signals
        self.session.logged_in.connect(self.on_login_success)
        self.session.logged_out.connect(self.on_logout)
        
        # Window setup
        self.setWindowTitle("Kali Linux Simulator - Security Testing Platform")
        self.setWindowIcon(QIcon("assets/icons/kali-logo.png"))
        self.showFullScreen()
        
        # Style
        self.load_stylesheet()
        
        # Show login
        self.stacked_widget.setCurrentIndex(0)
        
    def load_stylesheet(self):
        """Load QSS stylesheet"""
        qss_path = Path("style.qss")
        if qss_path.exists():
            with open(qss_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        else:
            print("Warning: style.qss not found")
    
    def on_login_success(self):
        """Handle successful login"""
        self.stacked_widget.setCurrentIndex(1)
        self.desktop_screen.start_session()
    
    def on_logout(self):
        """Handle logout"""
        self.desktop_screen.stop_session()
        self.stacked_widget.setCurrentIndex(0)
        self.login_screen.reset_fields()
    
    def closeEvent(self, event):
        """Handle application close"""
        if hasattr(self, 'desktop_screen'):
            self.desktop_screen.stop_session()
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Kali Linux Simulator")
    app.setOrganizationName("KaliSim")
    
    # Set global font
    font = QFont("Monospace", 10)
    font.setStyleHint(QFont.Monospace)
    app.setFont(font)
    
    # Show splash
    splash_pix = QPixmap("assets/icons/splash.png")
    if not splash_pix.isNull():
        splash = QSplashScreen(splash_pix)
        splash.show()
        QTimer.singleShot(2000, splash.close)
    
    window = KaliSimulator()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
