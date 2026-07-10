def on_tree_click(self, index: QModelIndex):
        """Handle click on directory tree"""
        path = self.tree_model.filePath(index)
        if os.path.isdir(path):
            self.load_directory(path)
            
    def go_up(self):
        """Navigate to parent directory"""
        parent = os.path.dirname(self.current_path)
        if parent and parent != self.current_path:
            self.load_directory(parent)
    
    def on_file_double_click(self, index: QModelIndex):
        """Handle double-click on file or directory"""
        path = self.file_model.filePath(index)
        if os.path.isdir(path):
            self.load_directory(path)
        else:
            # Try to open file
            self.open_file(path)
    
    def open_file(self, path: str):
        """Open file with appropriate application"""
        import subprocess
        try:
            if sys.platform == 'linux':
                subprocess.Popen(['xdg-open', path])
            elif sys.platform == 'darwin':
                subprocess.Popen(['open', path])
            elif sys.platform == 'win32':
                os.startfile(path)
        except Exception as e:
            # Show file content in terminal
            self.show_file_content(path)
    
    def show_file_content(self, path: str):
        """Show file content in a dialog"""
        try:
            with open(path, 'r', errors='ignore') as f:
                content = f.read()
            from PySide6.QtWidgets import QDialog, QTextEdit, QVBoxLayout
            dialog = QDialog(self)
            dialog.setWindowTitle(f"File: {os.path.basename(path)}")
            dialog.setGeometry(200, 200, 800, 600)
            layout = QVBoxLayout()
            text_edit = QTextEdit()
            text_edit.setPlainText(content)
            text_edit.setReadOnly(True)
            text_edit.setStyleSheet("background-color: #0a0a0a; color: #00ff00; font-family: monospace;")
            layout.addWidget(text_edit)
            dialog.setLayout(layout)
            dialog.exec()
        except:
            pass
    
    def show_context_menu(self, pos):
        """Show right-click context menu"""
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #1a1a1a;
                color: #cccccc;
                border: 1px solid #00ff00;
                padding: 5px;
            }
            QMenu::item {
                padding: 8px 30px;
            }
            QMenu::item:selected {
                background-color: #003300;
                color: #00ff00;
            }
            QMenu::separator {
                height: 1px;
                background-color: #333333;
                margin: 5px 10px;
            }
        """)
        
        index = self.file_view.indexAt(pos)
        has_selection = index.isValid()
        
        new_folder = QAction("📁 New Folder", self)
        new_folder.triggered.connect(self.new_folder)
        menu.addAction(new_folder)
        
        menu.addSeparator()
        
        if has_selection:
            open_action = QAction("📂 Open", self)
            open_action.triggered.connect(lambda: self.on_file_double_click(index))
            menu.addAction(open_action)
            
            copy_action = QAction("📋 Copy", self)
            copy_action.triggered.connect(self.copy_files)
            menu.addAction(copy_action)
            
            cut_action = QAction("✂️ Cut", self)
            cut_action.triggered.connect(self.cut_files)
            menu.addAction(cut_action)
            
            paste_action = QAction("📌 Paste", self)
            paste_action.triggered.connect(self.paste_files)
            menu.addAction(paste_action)
            
            menu.addSeparator()
            
            rename_action = QAction("✏️ Rename", self)
            rename_action.triggered.connect(self.rename_file)
            menu.addAction(rename_action)
            
            delete_action = QAction("🗑️ Delete", self)
            delete_action.triggered.connect(self.delete_files)
            menu.addAction(delete_action)
            
            menu.addSeparator()
            
            properties_action = QAction("ℹ️ Properties", self)
            properties_action.triggered.connect(lambda: self.show_properties(index))
            menu.addAction(properties_action)
        
        menu.addSeparator()
        terminal_action = QAction("🖥️ Open Terminal Here", self)
        terminal_action.triggered.connect(self.open_terminal_here)
        menu.addAction(terminal_action)
        
        menu.exec(self.file_view.viewport().mapToGlobal(pos))
    
    def new_folder(self):
        """Create a new folder"""
        name, ok = QInputDialog.getText(self, "New Folder", "Folder name:")
        if ok and name:
            path = os.path.join(self.current_path, name)
            try:
                os.makedirs(path, exist_ok=True)
                self.load_directory(self.current_path)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not create folder: {str(e)}")
    
    def copy_files(self):
        """Copy selected files to clipboard"""
        indexes = self.file_view.selectedIndexes()
        if not indexes:
            return
        self.clipboard = [self.file_model.filePath(idx) for idx in indexes if idx.column() == 0]
        self.clipboard_action = 'copy'
        self.status_bar.showMessage(f"{len(self.clipboard)} items copied")
    
    def cut_files(self):
        """Cut selected files"""
        indexes = self.file_view.selectedIndexes()
        if not indexes:
            return
        self.clipboard = [self.file_model.filePath(idx) for idx in indexes if idx.column() == 0]
        self.clipboard_action = 'cut'
        self.status_bar.showMessage(f"{len(self.clipboard)} items cut")
    
    def paste_files(self):
        """Paste files from clipboard"""
        if not self.clipboard:
            return
        
        for src in self.clipboard:
            basename = os.path.basename(src)
            dst = os.path.join(self.current_path, basename)
            try:
                if self.clipboard_action == 'copy':
                    if os.path.isdir(src):
                        shutil.copytree(src, dst)
                    else:
                        shutil.copy2(src, dst)
                elif self.clipboard_action == 'cut':
                    shutil.move(src, dst)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not paste: {str(e)}")
        
        self.clipboard = []
        self.clipboard_action = None
        self.load_directory(self.current_path)
    
    def delete_files(self):
        """Delete selected files"""
        indexes = self.file_view.selectedIndexes()
        if not indexes:
            return
        
        paths = [self.file_model.filePath(idx) for idx in indexes if idx.column() == 0]
        names = "\n".join(os.path.basename(p) for p in paths)
        
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Permanently delete these {len(paths)} items?\n{names}",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            for path in paths:
                try:
                    if os.path.isdir(path):
                        shutil.rmtree(path)
                    else:
                        os.remove(path)
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Could not delete: {str(e)}")
            self.load_directory(self.current_path)
    
    def rename_file(self):
        """Rename selected file"""
        indexes = self.file_view.selectedIndexes()
        if not indexes:
            return
        
        path = self.file_model.filePath(indexes[0])
        old_name = os.path.basename(path)
        
        name, ok = QInputDialog.getText(self, "Rename", "New name:", text=old_name)
        if ok and name:
            new_path = os.path.join(os.path.dirname(path), name)
            try:
                os.rename(path, new_path)
                self.load_directory(self.current_path)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not rename: {str(e)}")
    
    def filter_files(self, text: str):
        """Filter files by name"""
        self.file_model.setNameFilters([f"*{text}*"] if text else [])
        self.file_model.setNameFilterDisables(False)
    
    def show_properties(self, index):
        """Show file properties dialog"""
        path = self.file_model.filePath(index)
        if not os.path.exists(path):
            return
        
        info = os.stat(path)
        name = os.path.basename(path)
        is_dir = os.path.isdir(path)
        
        props = f"""
        Name: {name}
        Type: {'Directory' if is_dir else 'File'}
        Location: {os.path.dirname(path)}
        Size: {self.format_size(info.st_size)}
        Created: {datetime.fromtimestamp(info.st_ctime).strftime('%Y-%m-%d %H:%M:%S')}
        Modified: {datetime.fromtimestamp(info.st_mtime).strftime('%Y-%m-%d %H:%M:%S')}
        Permissions: {oct(stat.S_IMODE(info.st_mode))}
        Owner: {info.st_uid}
        Group: {info.st_gid}
        """
        
        QMessageBox.information(self, f"Properties: {name}", props)
    
    def format_size(self, size: int) -> str:
        """Format file size in human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024
        return f"{size:.2f} PB"
    
    def open_terminal_here(self):
        """Open terminal in current directory"""
        from desktop import DesktopScreen
        # This would emit a signal to open terminal - simplified
        self.status_bar.showMessage(f"Terminal opened at: {self.current_path}")
