#!/usr/bin/env python3
"""Generate placeholder icons for the Kali Simulator"""
import os
from PySide6.QtGui import QPixmap, QPainter, QColor, QFont, QPen
from PySide6.QtCore import Qt, QRect

ICONS = {
    "terminal.png": ("🖥", QColor(0, 255, 0)),
    "files.png": ("📁", QColor(100, 200, 255)),
    "browser.png": ("🌐", QColor(50, 150, 255)),
    "tools.png": ("⚔", QColor(255, 100, 50)),
    "settings.png": ("⚙", QColor(200, 200, 200)),
    "kali-logo.png": ("K", QColor(0, 255, 0)),
    "splash.png": ("KALI", QColor(0, 255, 0)),
}

os.makedirs("assets/icons", exist_ok=True)

for filename, (text, color) in ICONS.items():
    pixmap = QPixmap(128, 128)
    pixmap.fill(QColor(10, 10, 10))
    
    painter = QPainter(pixmap)
    painter.setPen(QPen(color, 2))
    painter.setFont(QFont("Monospace", 48, QFont.Bold))
    painter.drawText(QRect(0, 0, 128, 128), Qt.AlignCenter, text)
    painter.end()
    
    pixmap.save(f"assets/icons/{filename}")
    print(f"Created: assets/icons/{filename}")

print("All icons created successfully!")
