#!/usr/bin/env python3
"""
Kali Linux Simulator - Web Browser
Simple browser with web rendering capabilities
"""

import sys
import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QTabWidget, QToolButton, QLabel, QProgressBar, QStatusBar,
    QFrame, QMenu
)
from PySide6.QtCore import Qt, QUrl, Signal, QTimer
from PySide6.QtGui import QIcon, QKeySequence, QShortcut, QAction

try:
    from PySide6.QtWebEngineWidgets import QWebEngineView
    from PySide6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile
    WEBENGINE_AVAILABLE = True
except ImportError:
    WEBENGINE_AVAILABLE = False
    print("Warning: Qt WebEngine not available. Browser will use fallback mode.")


class BrowserTab(QWidget):
    """Individual browser tab"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        if WEBENGINE_AVAILABLE:
            self.web_view = QWebEngineView()
            self.web_view.setStyleSheet("background-color: #ffffff;")
            self.web_view.urlChanged.connect(self.on_url_changed)
            self.web_view.loadFinished.connect(self.on_loaded)
            self.web_view.loadProgress.connect(self.on_progress)
        else:
            # Fallback label
            self.web_view = QLabel("WebEngine not available.\nInstall PySide6-QtWebEngine:\npip install PySide6[webengine]")
            self.web_view.setAlignment(Qt.AlignCenter)
            self.web_view.setStyleSheet("color: #00ff00; font-size: 16px; padding: 50px;")
        
        layout.addWidget(self.web_view)
        self.setLayout(layout)
        self.current_url = ""
        
    def load_url(self, url: str):
        """Load a URL in this tab"""
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        
        if WEBENGINE_AVAILABLE:
            self.web_view.load(QUrl(url))
        self.current_url = url
    
    def on_url_changed(self, url: QUrl):
        """Handle URL changed event"""
        self.current_url = url.toString()
    
    def on_loaded(self, ok: bool):
        """Handle page load completion"""
        pass
    
    def on_progress(self, progress: int):
        """Handle load progress"""
        pass


class BrowserWidget(QWidget):
    """Main browser widget"""
    
    def __init__(self, session_manager):
        super().__init__()
        self.session = session_manager
        self.setup_ui()
        self.add_tab()
    
    def setup_ui(self):
        """Setup browser UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Navigation toolbar
        nav_bar = QFrame()
        nav_bar.setFixedHeight(40)
        nav_bar.setStyleSheet("""
            background-color: #111111;
            border-bottom: 1px solid #333333;
        """)
        
        nav_layout = QHBoxLayout()
        nav_layout.setContentsMargins(5, 2, 5, 2)
        nav_layout.setSpacing(3)
        
        # Back/Forward
        self.back_btn = QToolButton()
        self.back_btn.setText("◀")
        self.back_btn.setStyleSheet("color: #00ff00; border: none; padding: 5px;")
        self.back_btn.clicked.connect(self.go_back)
        
        self.forward_btn = QToolButton()
        self.forward_btn.setText("▶")
        self.forward_btn.setStyleSheet("color: #00ff00; border: none; padding: 5px;")
        self.forward_btn.clicked.connect(self.go_forward)
        
        self.refresh_btn = QToolButton()
        self.refresh_btn.setText("🔄")
        self.refresh_btn.setStyleSheet("color: #00ff00; border: none; padding: 5px;")
        self.refresh_btn.clicked.connect(self.refresh_page)
        
        # URL bar
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Enter URL...")
        self.url_bar.setStyleSheet("""
            QLineEdit {
                background-color: #1a1a1a;
                color: #00ff00;
                border: 1px solid #333333;
                border-radius: 15px;
                padding: 5px 15px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 1px solid #00ff00;
            }
        """)
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        
        # New tab button
        self.new_tab_btn = QPushButton("+")
        self.new_tab_btn.setFixedSize(30, 30)
        self.new_tab_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #00ff00;
                border: 1px solid #333333;
                border-radius: 15px;
                font-size: 18px;
            }
            QPushButton:hover {
                border: 1px solid #00ff00;
            }
        """)
        self.new_tab_btn.clicked.connect(lambda: self.add_tab())
        
        nav_layout.addWidget(self.back_btn)
        nav_layout.addWidget(self.forward_btn)
        nav_layout.addWidget(self.refresh_btn)
        nav_layout.addWidget(self.url_bar, 1)
        nav_layout.addWidget(self.new_tab_btn)
        
        nav_bar.setLayout(nav_layout)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background-color: #0a0a0a;
            }
            QTabBar::tab {
                background-color: #1a1a1a;
                color: #888888;
                border: 1px solid #333333;
                padding: 5px 15px;
                margin-right: 2px;
                font-size: 11px;
            }
            QTabBar::tab:selected {
                background-color: #0a0a0a;
                color: #00ff00;
                border-bottom: 2px solid #00ff00;
            }
            QTabBar::tab:hover {
                background-color: #2a2a2a;
                color: #00ff00;
            }
        """)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(3)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #1a1a1a;
                border: none;
                border-radius: 0;
            }
            QProgressBar::chunk {
                background-color: #00ff00;
            }
        """)
        self.progress_bar.hide()
        
        # Status bar
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet("""
            QStatusBar {
                background-color: #111111;
                color: #00ff00;
                border-top: 1px solid #333333;
                font-size: 11px;
            }
        """)
        self.status_bar.showMessage("Ready")
        
        layout.addWidget(nav_bar)
        layout.addWidget(self.tab_widget, 1)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.status_bar)
        
        self.setLayout(layout)
        
        # Shortcuts
        QShortcut(QKeySequence("Ctrl+T"), self, lambda: self.add_tab())
        QShortcut(QKeySequence("Ctrl+W"), self, lambda: self.close_tab(self.tab_widget.currentIndex()))
        QShortcut(QKeySequence("F5"), self, self.refresh_page)
        QShortcut(QKeySequence("Ctrl+L"), self, lambda: self.url_bar.selectAll())
    
    def add_tab(self, url: str = "https://www.duckduckgo.com"):
        """Add a new browser tab"""
        tab = BrowserTab(self)
        index = self.tab_widget.addTab(tab, "New Tab")
        self.tab_widget.setCurrentIndex(index)
        tab.load_url(url)
        self.tab_widget.setTabText(index, url[:20])
        return tab
    
    def close_tab(self, index: int):
        """Close a tab"""
        if self.tab_widget.count() > 1:
            self.tab_widget.removeTab(index)
    
    def navigate_to_url(self):
        """Navigate to URL in current tab"""
        url = self.url_bar.text().strip()
        if url:
            current_tab = self.tab_widget.currentWidget()
            if current_tab:
                current_tab.load_url(url)
                self.tab_widget.setTabText(self.tab_widget.currentIndex(), url[:20])
    
    def on_tab_changed(self, index: int):
        """Handle tab change"""
        if index >= 0:
            tab = self.tab_widget.widget(index)
            if tab and hasattr(tab, 'current_url'):
                self.url_bar.setText(tab.current_url)
    
    def go_back(self):
        if WEBENGINE_AVAILABLE:
            tab = self.tab_widget.currentWidget()
            if tab and hasattr(tab, 'web_view'):
                tab.web_view.back()
    
    def go_forward(self):
        if WEBENGINE_AVAILABLE:
            tab = self.tab_widget.currentWidget()
            if tab and hasattr(tab, 'web_view'):
                tab.web_view.forward()
    
    def refresh_page(self):
        if WEBENGINE_AVAILABLE:
            tab = self.tab_widget.currentWidget()
            if tab and hasattr(tab, 'web_view'):
                tab.web_view.reload()
