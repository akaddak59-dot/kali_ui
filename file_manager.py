#!/usr/bin/env python3
"""
Kali Linux Simulator - File Manager
Full file browser with tree view, list view, search, and operations
"""

import os
import shutil
import stat
import mimetypes
from pathlib import Path
from datetime import datetime
from typing import Optional

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QTreeView,
    QListView, QTableView, QLineEdit, QPushButton, QLabel,
    QFileSystemModel, QFileIconProvider, QMenu, QMessageBox,
    QInputDialog, QProgressDialog, QToolButton, QComboBox,
    QStackedWidget, QStatusBar, QHeaderView, QAbstractItemView,
    QListWidget, QListWidgetItem, QFrame
)
from PySide6.QtCore import (
    Qt, Signal, QDir, QModelIndex, QSortFilterProxyModel,
    QUrl, QMimeData, QSize, QTimer
)
from PySide6.QtGui import (
    QIcon, QPixmap, QFont, QAction, QColor, QPalette,
    QKeySequence, QShortcut, QDrag, QStandardItemModel,
    QStandardItem, QFileSystemModel
)


class FileManager(QWidget):
    """Full-featured file manager"""
    
    def __init__(self, session_manager):
        super().__init__()
        self.session = session_manager
        self.current_path = os.path.expanduser("~")
        self.clipboard = []  # For copy/paste
        self.clipboard_action = None  # 'copy' or 'cut'
        
        self.setup_ui()
        self.load_directory(self.current_path)
        
    def setup_ui(self):
        """Setup the file manager interface"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Toolbar
        toolbar = QFrame()
        toolbar.setFixedHeight(40)
        toolbar.setStyleSheet("""
            background-color: #111111;
            border-bottom: 1px solid #333333;
        """)
        
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setContentsMargins(5, 2, 5, 2)
        
        # Navigation buttons
        self.back_btn = QToolButton()
        self.back_btn.setArrowType(Qt.LeftArrow)
        self.back_btn.setStyleSheet("""
            QToolButton { color: #00ff00; border: none; padding: 5px; }
            QToolButton:hover { background-color: #333333; }
        """)
        
        self.forward_btn = QToolButton()
        self.forward_btn.setArrowType(Qt.RightArrow)
        self.forward_btn.setStyleSheet("""
            QToolButton { color: #00ff00; border: none; padding: 5px; }
            QToolButton:hover { background-color: #333333; }
        """)
        
        self.up_btn = QToolButton()
        self.up_btn.setText("↑")
        self.up_btn.setStyleSheet("""
            QToolButton { color: #00ff00; border: none; padding: 5px; font-size: 16px; }
            QToolButton:hover { background-color: #333333; }
        """)
        
        # Path bar
        self.path_bar = QLineEdit()
        self.path_bar.setStyleSheet("""
            QLineEdit {
                background-color: #1a1a1a;
                color: #00ff00;
                border: 1px solid #333333;
                border-radius: 3px;
                padding: 5px 10px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 1px solid #00ff00;
            }
        """)
        self.path_bar.returnPressed.connect(self.navigate_to_path)
        
        # Search
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("🔍 Search files...")
        self.search_box.setFixedWidth(200)
        self.search_box.setStyleSheet("""
            QLineEdit {
                background-color: #1a1a1a;
                color: #00ff00;
                border: 1px solid #333333;
                border-radius: 3px;
                padding: 5px 10px;
            }
            QLineEdit:focus {
                border: 1px solid #00ff00;
            }
        """)
        self.search_box.textChanged.connect(self.filter_files)
        
        toolbar_layout.addWidget(self.back_btn)
        toolbar_layout.addWidget(self.forward_btn)
        toolbar_layout.addWidget(self.up_btn)
        toolbar_layout.addWidget(self.path_bar, 1)
        toolbar_layout.addWidget(self.search_box)
        
        toolbar.setLayout(toolbar_layout)
        
        # Main content: splitter with tree and file list
        self.splitter = QSplitter(Qt.Horizontal)
        
        # Directory tree (left panel)
        self.tree_model = QFileSystemModel()
        self.tree_model.setRootPath(QDir.rootPath())
        self.tree_model.setFilter(QDir.AllDirs | QDir.NoDotAndDotDot)
        
        self.tree_view = QTreeView()
        self.tree_view.setModel(self.tree_model)
        self.tree_view.setRootIndex(self.tree_model.index(QDir.rootPath()))
        self.tree_view.setAnimated(True)
        self.tree_view.setIndentation(15)
        self.tree_view.setHeaderHidden(True)
        self.tree_view.hideColumn(1)
        self.tree_view.hideColumn(2)
        self.tree_view.hideColumn(3)
        self.tree_view.setStyleSheet("""
            QTreeView {
                background-color: #0d0d0d;
                color: #cccccc;
                border: none;
                font-size: 12px;
            }
            QTreeView::item:hover {
                background-color: #1a3a1a;
                color: #00ff00;
            }
            QTreeView::item:selected {
                background-color: #003300;
                color: #00ff00;
            }
        """)
        self.tree_view.clicked.connect(self.on_tree_click)
        
        # File list (right panel)
        self.file_model = QFileSystemModel()
        self.file_model.setRootPath(self.current_path)
        self.file_model.setFilter(QDir.AllEntries | QDir.NoDotAndDotDot)
        
        self.file_view = QListView()
        self.file_view.setModel(self.file_model)
        self.file_view.setRootIndex(self.file_model.index(self.current_path))
        self.file_view.setViewMode(QListView.IconMode)
        self.file_view.setIconSize(QSize(48, 48))
        self.file_view.setGridSize(QSize(100, 80))
        self.file_view.setResizeMode(QListView.Adjust)
        self.file_view.setWordWrap(True)
        self.file_view.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.file_view.setDragDropMode(QAbstractItemView.DragDrop)
        self.file_view.setDefaultDropAction(Qt.CopyAction)
        self.file_view.setStyleSheet("""
            QListView {
                background-color: #0a0a0a;
                color: #cccccc;
                border: none;
                font-size: 11px;
                outline: none;
            }
            QListView::item:hover {
                background-color: #1a3a1a;
                border: 1px solid #00ff00;
                border-radius: 4px;
            }
            QListView::item:selected {
                background-color: #003300;
                color: #00ff00;
                border: 1px solid #00ff00;
                border-radius: 4px;
            }
        """)
        self.file_view.doubleClicked.connect(self.on_file_double_click)
        self.file_view.customContextMenuRequested.connect(self.show_context_menu)
        self.file_view.setContextMenuPolicy(Qt.CustomContextMenu)
        
        self.splitter.addWidget(self.tree_view)
        self.splitter.addWidget(self.file_view)
        self.splitter.setSizes([200, 600])
        self.splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #333333;
                width: 2px;
            }
        """)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet("""
            QStatusBar {
                background-color: #111111;
                color: #00ff00;
                border-top: 1px solid #333333;
                font-size: 11px;
                padding: 2px 10px;
            }
        """)
        
        layout.addWidget(toolbar)
        layout.addWidget(self.splitter, 1)
        layout.addWidget(self.status_bar)
        
        self.setLayout(layout)
        
        # Connect toolbar buttons
        self.up_btn.clicked.connect(self.go_up)
        
        # Keyboard shortcuts
        QShortcut(QKeySequence("Ctrl+C"), self, self.copy_files)
        QShortcut(QKeySequence("Ctrl+X"), self, self.cut_files)
        QShortcut(QKeySequence("Ctrl+V"), self, self.paste_files)
        QShortcut(QKeySequence("Delete"), self, self.delete_files)
        QShortcut(QKeySequence("F2"), self, self.rename_file)
        QShortcut(QKeySequence("F5"), self, lambda: self.load_directory(self.current_path))
        QShortcut(QKeySequence("Ctrl+N"), self, self.new_folder)
        
    def load_directory(self, path: str):
        """Load a directory into the file view"""
        if not os.path.isdir(path):
            return
            
        self.current_path = path
        self.path_bar.setText(path)
        
        # Update file model
        self.file_model.setRootPath(path)
        self.file_model.setFilter(QDir.AllEntries | QDir.NoDotAndDotDot)
        self.file_view.setRootIndex(self.file_model.index(path))
        
        # Update status
        try:
            count = len(os.listdir(path))
            self.status_bar.showMessage(f"{count} items | {path}")
        except:
            self.status_bar.showMessage(f"Error reading directory | {path}")
            
    def navigate_to_path(self):
        """Navigate to the path entered in the path bar"""
        path = self.path_bar.text()
        path = os.path.expanduser(path)
        if os.path.isdir(path):
            self.load_directory(path)
        else:
            self.status_bar.showMessage(f"ERROR: Directory not found: {path}")
            
    def on_tree_click(self, index: QModelIndex):
        """Handle click on directory tree"""
        path = self.tree_model.filePath(index)
        if os.path.isdir(path):
            self.load_directory(path
