#!/usr/bin/env python3
"""
Kali Linux Simulator - Desktop Environment
Full desktop with taskbar, applications menu, and wallpaper
"""

import subprocess
import threading
import os
import sys
from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, 
    QPushButton, QFrame, QScrollArea, QMainWindow, QDialog,
    QLineEdit, QListWidget, QListWidgetItem, QMenu, QSystemTrayIcon,
    QSizePolicy, QStackedWidget
)
from PySide6.QtCore import (
    Qt, Signal, QTimer, QPoint, QPropertyAnimation, 
    QEasingCurve, QRect, QSize
)
from PySide6.QtGui import (
    QPixmap, QFont, QIcon, QColor, QAction, QPainter,
    QPen, QBrush, QLinearGradient, QPalette
)

from terminal import TerminalWidget
from file_manager import FileManager
from browser import BrowserWidget
from settings import SettingsDialog
from tools import ToolsPanel


class Taskbar(QFrame):
    """Windows-style taskbar at the bottom"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(40)
        self.setObjectName("taskbar")
        self.setStyleSheet("""
            #taskbar {
                background-color: rgba(15, 15, 15, 230);
                border-top: 1px solid #00ff00;
            }
        """)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(5, 2, 5, 2)
        layout.setSpacing(5)
        
        # Start menu button
        self.start_btn = QPushButton("KALI")
        self.start_btn.setFixedSize(70, 34)
        self.start_btn.setCursor(Qt.PointingHandCursor)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #00ff00;
                color: #000000;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 11px;
                letter-spacing: 2px;
            }
            QPushButton:hover {
                background-color: #00cc00;
            }
            QPushButton:pressed {
                background-color: #009900;
            }
        """)
        layout.addWidget(self.start_btn)
        
        # Running applications list
        self.app_list = QHBoxLayout()
        self.app_list.setSpacing(3)
        layout.addLayout(self.app_list, 1)
        
        # System tray area
        tray_layout = QHBoxLayout()
        tray_layout.setSpacing(8)
        
        self.clock_label = QLabel()
        self.clock_label.setStyleSheet("color: #00ff00; font-size: 11px;")
        layout.addLayout(tray_layout)
        layout.addWidget(self.clock_label)
        
        self.setLayout(layout)
        
        # Update clock
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_clock)
        self.timer.start(1000)
        self.update_clock()
        
    def update_clock(self):
        from datetime import datetime
        now = datetime.now()
        self.clock_label.setText(now.strftime("%H:%M:%S  %d/%m/%Y"))
        
    def add_app_button(self, name: str, callback):
        """Add a running app to the taskbar"""
        btn = QPushButton(name[:8])
        btn.setFixedSize(80, 30)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet("""
            QPushButton {
                background-color: #2a2a2a;
                color: #cccccc;
                border: 1px solid #444444;
                border-radius: 3px;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #3a3a3a;
                border: 1px solid #00ff00;
            }
        """)
        btn.clicked.connect(callback)
        self.app_list.addWidget(btn)


class DesktopScreen(QWidget):
    """Main desktop environment"""
    
    def __init__(self, session_manager):
        super().__init__()
        self.session = session_manager
        self.open_windows = []
        self.window_counter = 0
        
        self.setup_ui()
        self.create_desktop_icons()
        
    def setup_ui(self):
        """Setup the desktop layout"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Desktop area
        desktop_area = QWidget()
        desktop_area.setObjectName("desktopArea")
        desktop_area.setStyleSheet("""
            #desktopArea {
                background-color: #0a0a0a;
                background-image: url(assets/wallpaper.png);
                background-repeat: no-repeat;
                background-position: center;
                background-size: cover;
            }
        """)
        
        # Create desktop layout with icons on left and workspace in center
        desktop_layout = QHBoxLayout()
        desktop_layout.setContentsMargins(10, 10, 10, 10)
        
        # Desktop icons panel (left side)
        self.icons_panel = QWidget()
        self.icons_panel.setFixedWidth(120)
        self.icons_layout = QVBoxLayout()
        self.icons_layout.setAlignment(Qt.AlignTop)
        self.icons_layout.setSpacing(15)
        self.icons_panel.setLayout(self.icons_layout)
        
        # Workspace area (center)
        self.workspace = QWidget()
        self.workspace.setStyleSheet("background: transparent;")
        workspace_layout = QVBoxLayout()
        workspace_layout.setAlignment(Qt.AlignCenter)
        
        # Welcome message
        self.welcome_label = QLabel("Welcome to Kali Linux Simulator")
        self.welcome_label.setAlignment(Qt.AlignCenter)
        self.welcome_label.setStyleSheet("""
            font-size: 28px;
            color: #00ff00;
            font-weight: bold;
            background: transparent;
        """)
        workspace_layout.addWidget(self.welcome_label)
        
        self.sub_welcome = QLabel("Security Testing Platform | Authorized Use Only")
        self.sub_welcome.setAlignment(Qt.AlignCenter)
        self.sub_welcome.setStyleSheet("""
            font-size: 14px;
            color: #888888;
            background: transparent;
        """)
        workspace_layout.addWidget(self.sub_welcome)
        
        self.workspace.setLayout(workspace_layout)
        
        desktop_layout.addWidget(self.icons_panel)
        desktop_layout.addWidget(self.workspace, 1)
        desktop_area.setLayout(desktop_layout)
        
        main_layout.addWidget(desktop_area, 1)
        
        # Taskbar
        self.taskbar = Taskbar()
        main_layout.addWidget(self.taskbar)
        
        self.setLayout(main_layout)
        
    def create_desktop_icons(self):
        """Create desktop shortcuts"""
        apps = [
            ("Terminal", "terminal.png", self.open_terminal),
            ("Files", "files.png", self.open_file_manager),
            ("Browser", "browser.png", self.open_browser),
            ("Tools", "tools.png", self.open_tools),
            ("Settings", "settings.png", self.open_settings),
        ]
        
        for name, icon_file, callback in apps:
            icon_path = f"assets/icons/{icon_file}"
            btn = QPushButton()
            btn.setFixedSize(100, 90)
            
            icon_pix = QPixmap(icon_path)
            if icon_pix.isNull():
                icon_pix = QPixmap(64, 64)
                icon_pix.fill(QColor(0, 255, 0, 50))
            
            # Create text + icon button
            btn.setText(name)
            btn.setIcon(QIcon(icon_pix))
            btn.setIconSize(QSize(40, 40))
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: rgba(0, 0, 0, 120);
                    border: 1px solid transparent;
                    border-radius: 6px;
                    color: #00ff00;
                    font-size: 10px;
                    padding: 5px;
                }
                QPushButton:hover {
                    border: 1px solid #00ff00;
                    background-color: rgba(0, 255, 0, 30);
                }
            """)
            btn.clicked.connect(callback)
            self.icons_layout.addWidget(btn)
    
    def add_window_to_desktop(self, title: str, widget: QWidget):
        """Add a floating window to the desktop"""
        # Create a window frame
        window_frame = QFrame(self.workspace)
        window_frame.setObjectName(f"window_{self.window_counter}")
        window_frame.setStyleSheet("""
            #window_frame {
                background-color: rgba(20, 20, 20, 240);
                border: 1px solid #00ff00;
                border-radius: 6px;
            }
        """)
        window_frame.setFixedSize(800, 500)
        
        # Title bar
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(5, 5, 5, 5)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #00ff00; font-weight: bold; font-size: 12px;")
        
        close_btn = QPushButton("X")
        close_btn.setFixedSize(24, 24)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #cc0000;
                color: white;
                border: none;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ff0000;
            }
        """)
        
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        title_layout.addWidget(close_btn)
        
        # Window layout
        window_layout = QVBoxLayout()
        window_layout.setContentsMargins(0, 0, 0, 0)
        window_layout.addLayout(title_layout)
        window_layout.addWidget(widget)
        
        window_frame.setLayout(window_layout)
        window_frame.show()
        
        # Center the window
        parent_rect = self.workspace.rect()
        window_frame.move(
            (parent_rect.width() - 800) // 2,
            (parent_rect.height() - 500) // 2 - 20
        )
        
        # Make draggable
        title_label.mousePressEvent = lambda e: self._start_drag(e, window_frame)
        title_label.mouseMoveEvent = lambda e: self._drag(e, window_frame)
        
        close_btn.clicked.connect(lambda: self._close_window(window_frame))
        
        # Add to taskbar
        self.taskbar.add_app_button(title, lambda: self._focus_window(window_frame))
        
        self.window_counter += 1
        
    def _start_drag(self, event, frame):
        if event.button() == Qt.LeftButton:
            self.drag_pos = event.globalPosition().toPoint() - frame.pos()
            event.accept()
            
    def _drag(self, event, frame):
        if event.buttons() == Qt.LeftButton:
            frame.move(event.globalPosition().toPoint() - self.drag_pos)
            event.accept()
            
    def _focus_window(self, frame):
        frame.raise_()
        frame.setStyleSheet(frame.styleSheet())
        
    def _close_window(self, frame):
        frame.hide()
        # Remove from taskbar - simplistic approach
        for i in range(self.taskbar.app_list.count()):
            item = self.taskbar.app_list.itemAt(i)
            if item and item.widget():
                # Would need proper tracking in production
                pass
    
    def open_terminal(self):
        term = TerminalWidget(self.session)
        self.add_window_to_desktop("Terminal", term)
        
    def open_file_manager(self):
        fm = FileManager(self.session)
        self.add_window_to_desktop("File Manager", fm)
        
    def open_browser(self):
        browser = BrowserWidget(self.session)
        self.add_window_to_desktop("Browser", browser)
        
    def open_tools(self):
        tools = ToolsPanel(self.session)
        self.add_window_to_desktop("Security Tools", tools)
        
    def open_settings(self):
        dialog = SettingsDialog(self, self.session)
        dialog.exec()
    
    def start_session(self):
        """Called when user logs in"""
        self.welcome_label.setText(f"Welcome, {self.session.username}!")
        self.sub_welcome.setText("Ready for authorized security testing")
        
    def stop_session(self):
        """Called on logout"""
        # Close all windows
        for child in self.workspace.findChildren(QFrame):
            if child.objectName().startswith("window_"):
                child.deleteLater()
