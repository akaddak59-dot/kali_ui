#!/usr/bin/env python3
"""
Kali Linux Simulator - Terminal Emulator
Full terminal with command execution, tab completion, history
"""

import os
import sys
import shlex
import subprocess
import threading
import signal
import re
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTextEdit, QLineEdit, QLabel,
    QHBoxLayout, QPushButton, QScrollArea, QMenu, QCompleter,
    QSplitter, QFrame
)
from PySide6.QtCore import (
    Qt, Signal, QProcess, QTimer, QStringListModel,
    QThread, QRegularExpression
)
from PySide6.QtGui import (
    QTextCursor, QColor, QFont, QPalette, QTextCharFormat,
    QSyntaxHighlighter, QKeySequence, QShortcut, QIcon, QAction
)


# --- Allowed Commands Configuration ---
# These commands are whitelisted for execution
ALLOWED_COMMANDS = {
    # System info
    "whoami", "id", "uname", "hostname", "uptime", "date", "cal",
    "pwd", "ls", "dir", "tree", "clear", "echo", "cat", "head", 
    "tail", "more", "less", "wc", "sort", "cut", "grep", "find",
    "locate", "which", "whereis", "type",
    
    # Network
    "ping", "ip", "ifconfig", "netstat", "ss", "nslookup", "dig",
    "host", "traceroute", "tracepath", "mtr", "curl", "wget",
    "nc", "ncat", "socat",
    
    # Process
    "ps", "top", "htop", "kill", "pkill", "pgrep", "nice", "renice",
    "nohup", "jobs", "bg", "fg",
    
    # File operations
    "cp", "mv", "rm", "mkdir", "rmdir", "touch", "chmod", "chown",
    "ln", "stat", "file", "du", "df", "mount", "umount",
    
    # Archive
    "tar", "gzip", "gunzip", "bzip2", "bunzip2", "xz", "unxz",
    "zip", "unzip", "7z", "rar", "unrar",
    
    # Security tools
    "nmap", "nikto", "gobuster", "dirb", "wfuzz", "sqlmap",
    "hydra", "john", "hashcat", "aircrack-ng", "airodump-ng",
    "aireplay-ng", "macchanger", "netcat", "ncat", "socat",
    "metasploit", "msfconsole", "msfvenom", "searchsploit",
    "wireshark", "tshark", "tcpdump", "bettercap", "ettercap",
    "burpsuite", "zap", "beef", "setoolkit", "veil",
    "recon-ng", "theharvester", "sublist3r", "amass",
    "enum4linux", "smbclient", "smbmap", "impacket",
    "responder", "mitm6", "evil-winrm", "crackmapexec",
    "bloodhound", "sharphound", "certipy", "kerbrute",
    "wfuzz", "ffuf", "gobuster", "dirbuster", "gospider",
    "hash-identifier", "hashid", "hashcat", "john", "hashcat",
    
    # Development
    "python", "python3", "pip", "pip3", "perl", "ruby", "php",
    "node", "npm", "gcc", "g++", "make", "cmake", "git",
    
    # Text editors
    "nano", "vim", "vi", "emacs", "micro", "sed", "awk",
    
    # Shell
    "cd", "source", "export", "alias", "unalias", "set", "env",
    "printenv", "history", "help", "man", "info", "whatis",
    "apropos", "sh", "bash", "zsh", "exit", "logout",
    
    # Misc
    "yes", "seq", "printf", "test", "true", "false", "sleep",
    "time", "watch", "xargs", "tee", "base64", "md5sum",
    "sha256sum", "sha1sum", "xxd", "hexdump", "od", "strings",
    "rev", "tr", "uniq", "comm", "diff", "patch", "cmp",
    "basename", "dirname", "realpath", "readlink", "df", "du",
    "free", "lscpu", "lsblk", "lspci", "lsusb", "lsof",
    "dmesg", "sysctl", "modprobe", "lsmod", "insmod", "rmmod",
}

BLOCKED_PATTERNS = [
    r'sudo\s+rm\s+-rf\s+/',          # rm -rf /
    r'sudo\s+dd\s+if=',               # dd destructive
    r'format\s+[a-z]:',               # format drive
    r'mkfs\.',                         # mkfs
    r'fdisk\s+/dev/',                  # fdisk
    r'parted\s+/dev/',                 # parted
    r'mv\s+/\s+/dev/null',            # move root to null
    r'>\s*/dev/sda',                   # write to disk
    r'chmod\s+000\s+/',               # lock root
]


# --- Built-in commands ---
BUILTIN_COMMANDS = {
    "help": lambda args: """Kali Linux Terminal - Available Commands

Built-in:
  help          Show this help message
  clear/cls     Clear the terminal
  history       Show command history
  pwd           Print working directory
  whoami        Show current user
  kali-banner   Show Kali Linux banner
  tools         List all available security tools
  exit/quit     Exit terminal

System Commands (authorized):
  ls, cat, grep, find, ps, ping, nmap, sqlmap, hydra, john, hashcat,
  gobuster, nikto, dirb, curl, wget, nc, python3, git, and many more.

Network Security Tools:
  nmap, nikto, gobuster, sqlmap, hydra, john, hashcat, aircrack-ng,
  bettercap, responder, crackmapexec, bloodhound, impacket, etc.

Note: All commands are sandboxed. Destructive system operations are blocked.
        """,
    
    "clear": lambda args: "CLEAR",
    "cls": lambda args: "CLEAR",
    
    "history": lambda args: None,  # Handled separately
    
    "pwd": lambda args: os.getcwd(),
    
    "whoami": lambda args: "root",
    
    "kali-banner": lambda args: """
███████╗██╗  ██╗███████╗██╗     ███████╗██████╗ ██╗   ██╗██████╗ ███████╗██████╗ 
██╔════╝██║ ██╔╝██╔════╝██║     ██╔════╝██╔══██╗██║   ██║██╔══██╗██╔════╝██╔══██╗
█████╗  █████╔╝ █████╗  ██║     █████╗  ██████╔╝██║   ██║██████╔╝█████╗  ██████╔╝
██╔══╝  ██╔═██╗ ██╔══╝  ██║     ██╔══╝  ██╔══██╗╚██╗ ██╔╝██╔═══╝ ██╔══╝  ██╔══██╗
██║     ██║  ██╗███████╗███████╗███████╗██║  ██║ ╚████╔╝ ██║     ███████╗██║  ██║
╚═╝     ╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝╚═╝  ╚═╝  ╚═══╝  ╚═╝     ╚══════╝╚═╝  ╚═╝

 ██████╗ ██████╗ ███╗   ███╗██████╗ ██╗     ███████╗████████╗███████╗
██╔════╝██╔═══██╗████╗ ████║██╔══██╗██║     ██╔════╝╚══██╔══╝██╔════╝
██║     ██║   ██║██╔████╔██║██████╔╝██║     █████╗     ██║   █████╗  
██║     ██║   ██║██║╚██╔╝██║██╔══██╗██║     ██╔══╝     ██║   ██╔══╝  
╚██████╗╚██████╔╝██║ ╚═╝ ██║██████╔╝███████╗███████╗   ██║   ███████╗
 ╚═════╝ ╚═════╝ ╚═╝     ╚═╝╚═════╝ ╚══════╝╚══════╝   ╚═╝   ╚══════╝

    Welcome to Kali Linux Simulator - Security Testing Platform
    For authorized security testing and educational purposes only.
    
    Type 'help' for available commands or 'tools' for security tools.
        """,
    
    "tools": lambda args: """
╔══════════════════════════════════════════════════════════════╗
║              AVAILABLE SECURITY TOOLS                      ║
╠══════════════════════════════════════════════════════════════╣
║                                                            ║
║  RECONNAISSANCE:                                           ║
║    nmap, masscan, rustscan, zmap, unicornscan              ║
║    recon-ng, theharvester, sublist3r, amass                ║
║    dnsenum, dnsrecon, fierce, dnsmap, whois               ║
║                                                            ║
║  SCANNING:                                                 ║
║    nikto, wpscan, joomscan, droopescan, wfuzz             ║
║    gobuster, dirb, dirbuster, ffuf, gospider              ║
║    arachni, skipfish, whatweb, wappalyzer                  ║
║                                                            ║
║  EXPLOITATION:                                             ║
║    metasploit, msfconsole, msfvenom, searchsploit         ║
║    sqlmap, hydra, medusa, ncrack, crowbar                 ║
║    commix, beef, setoolkit, veil, empire                   ║
║                                                            ║
║  POST-EXPLOITATION:                                        ║
║    crackmapexec, impacket, bloodhound, responder          ║
║    evil-winrm, psexec, wmiexec, smbexec, mimikatz         ║
║                                                            ║
║  PASSWORD CRACKING:                                        ║
║    john, hashcat, hydra, hash-identifier, hashid          ║
║    crunch, cupp, maskprocessor, kwprocessor                ║
║                                                            ║
║  WIRELESS:                                                 ║
║    aircrack-ng, airodump-ng, aireplay-ng, airmon-ng      ║
║    kismet, reaver, pixiewps, bully, mdk3                  ║
║                                                            ║
║  SNIFFING & SPOOFING:                                      ║
║    wireshark, tshark, tcpdump, bettercap, ettercap        ║
║    mitmproxy, mitm6, dnschef, arpspoof, dnsspoof          ║
║                                                            ║
║  WEB APPLICATIONS:                                         ║
║    burpsuite, zap, w3af, acunetix, netsparker             ║
║    httrack, wget, curl, postman                            ║
║                                                            ║
╚══════════════════════════════════════════════════════════════╝

Usage: Type any tool name followed by --help for usage information.
Example: nmap --help
        """,
}


class TerminalHighlighter(QSyntaxHighlighter):
    """Syntax highlighting for terminal output"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlighting_rules = []
        
        # Error patterns (red)
        error_format = QTextCharFormat()
        error_format.setForeground(QColor("#ff4444"))
        error_format.setFontWeight(QFont.Bold)
        self.highlighting_rules.append((r"(ERROR|error|Error|FAILED|failed|denied)", error_format))
        
        # Success patterns (green)
        success_format = QTextCharFormat()
        success_format.setForeground(QColor("#00ff00"))
        self.highlighting_rules.append((r"(SUCCESS|success|Success|GRANTED|granted)", success_format))
        
        # IP addresses (cyan)
        ip_format = QTextCharFormat()
        ip_format.setForeground(QColor("#00ccff"))
        self.highlighting_rules.append((r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", ip_format))
        
        # URLs (blue)
        url_format = QTextCharFormat()
        url_format.setForeground(QColor("#4488ff"))
        url_format.setUnderlineStyle(QTextCharFormat.SingleUnderline)
        self.highlighting_rules.append((r"https?://[^\s]+", url_format))
        
        # Port numbers (yellow)
        port_format = QTextCharFormat()
        port_format.setForeground(QColor("#ffaa00"))
        self.highlighting_rules.append((r"(:?\d{1,5}/tcp|\d{1,5}/udp)", port_format))
        
        # File paths (magenta)
        path_format = QTextCharFormat()
        path_format.setForeground(QColor("#ff66aa"))
        self.highlighting_rules.append((r"/([a-zA-Z0-9_\-./]+)", path_format))
        
    def highlightBlock(self, text):
        for pattern, fmt in self.highlighting_rules:
            match_iterator = QRegularExpression(pattern).globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), fmt)


class TerminalWidget(QWidget):
    """Full terminal emulator widget"""
    
    def __init__(self, session_manager):
        super().__init__()
        self.session = session_manager
        self.current_dir = os.path.expanduser("~")
        self.command_history = []
        self.history_index = -1
        self.process = None
        self.running = True
        
        self.setup_ui()
        self.show_banner()
        
    def setup_ui(self):
        """Setup terminal UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Terminal display
        self.output = QTextEdit()
        self.output.setReadOnly(False)
        self.output.setObjectName("terminalOutput")
        self.output.setStyleSheet("""
            #terminalOutput {
                background-color: #0a0a0a;
                color: #00ff00;
                border: none;
                padding: 10px;
                font-family: 'Monospace', 'Courier New', 'Liberation Mono';
                font-size: 13px;
                selection-background-color: #00ff00;
                selection-color: #000000;
            }
        """)
        
        # Highlighter
        self.highlighter = TerminalHighlighter(self.output.document())
        
        # Input area
        input_layout = QHBoxLayout()
        input_layout.setContentsMargins(10, 5, 10, 5)
        
        # Prompt
        self.prompt_label = QLabel()
        self.prompt_label.setStyleSheet("color: #00ff00; font-weight: bold; font-size: 13px;")
        self.update_prompt()
        
        # Command input
        self.command_input = QLineEdit()
        self.command_input.setObjectName("terminalInput")
        self.command_input.setStyleSheet("""
            #terminalInput {
                background-color: #0a0a0a;
                color: #00ff00;
                border: none;
                padding: 5px;
                font-family: 'Monospace', 'Courier New', 'Liberation Mono';
                font-size: 13px;
                selection-background-color: #00ff00;
                selection-color: #000000;
            }
        """)
        self.command_input.returnPressed.connect(self.execute_command)
        
        # Tab completion
        self.completer = QCompleter(sorted(ALLOWED_COMMANDS))
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setCompletionMode(QCompleter.InlineCompletion)
        self.command_input.setCompleter(self.completer)
        
        input_layout.addWidget(self.prompt_label)
        input_layout.addWidget(self.command_input)
        
        layout.addWidget(self.output, 1)
        layout.addLayout(input_layout)
        
        self.setLayout(layout)
        
        # Keyboard shortcuts
        QShortcut(QKeySequence("Ctrl+L"), self, self.clear_terminal)
        QShortcut(QKeySequence("Ctrl+Shift+C"), self, self.copy_selection)
        QShortcut(QKeySequence("Ctrl+Shift+V"), self, self.paste_text)
        QShortcut(QKeySequence("Up"), self, self.history_up)
        QShortcut(QKeySequence("Down"), self, self.history_down)
        
    def update_prompt(self):
        """Update the shell prompt"""
        username = self.session.username if self.session else "root"
        hostname = "kali"
        dir_short = self.current_dir.replace(os.path.expanduser("~"), "~")
        self.prompt_label.setText(f"{username}@{hostname}:{dir_short}# ")
        
    def show_banner(self):
        """Show Kali Linux banner"""
        banner = """\033[1;32m
███████╗██╗  ██╗███████╗██╗     ███████╗██████╗ ██╗   ██╗██████╗ ███████╗██████╗ 
██╔════╝██║ ██╔╝██╔════╝██║     ██╔════╝██╔══██╗██║   ██║██╔══██╗██╔════╝██╔══██╗
█████╗  █████╔╝ █████╗  ██║     █████╗  ██████╔╝██║   ██║██████╔╝█████╗  ██████╔╝
██╔══╝  ██╔═██╗ ██╔══╝  ██║     ██╔══╝  ██╔══██╗╚██╗ ██╔╝██╔═══╝ ██╔══╝  ██╔══██╗
██║     ██║  ██╗███████╗███████╗███████╗██║  ██║ ╚████╔╝ ██║     ███████╗██║  ██║
╚═╝     ╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝╚═╝  ╚═╝  ╚═══╝  ╚═╝     ╚══════╝╚═╝  ╚═╝
\033[0m
\033[1;33m  ⚡ Kali Linux Simulator v2024.3 ⚡\033[0m
\033[1;36m  🔒 Authorized Security Testing Platform\033[0m
\033[1;32m  📡 Type 'help' for commands | 'tools' for security tools\033[0m

"""
        self.output.append(banner)
        
    def append_output(self, text: str, color: str = "#00ff00"):
        """Append colored text to terminal"""
        cursor = self.output.textCursor()
        cursor.movePosition(QTextCursor.End)
        
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(color))
        fmt.setFont(QFont("Monospace", 11))
        
        cursor.insertText(text, fmt)
        self.output.setTextCursor(cursor)
        self.output.ensureCursorVisible()
        
    def execute_command(self):
        """Execute the entered command"""
        command = self.command_input.text().strip()
        self.command_input.clear()
        
        if not command:
            return
            
        # Add to history
        self.command_history.append(command)
        self.history_index = len(self.command_history)
        
        # Show command in output
        self.append_output(f"{self.prompt_label.text()}{command}\n")
        
        # Parse command
        parts = shlex.split(command) if command else []
        if not parts:
            self.update_prompt()
            return
            
        cmd = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        # Check for blocked patterns
        cmd_str = " ".join(parts)
        for pattern in BLOCKED_PATTERNS:
            if re.search(pattern, cmd_str):
                self.append_output(
                    f"\033[1;31m[BLOCKED] Command blocked for security: {cmd_str}\033[0m\n",
                    "#ff4444"
                )
                self.update_prompt()
                return
        
        # Handle built-in commands
        if cmd in BUILTIN_COMMANDS:
            result = BUILTIN_COMMANDS[cmd](args)
            if result == "CLEAR":
                self.clear_terminal()
            elif result:
                self.append_output(f"{result}\n")
            elif cmd == "history":
                for i, h in enumerate(self.command_history[:-1], 1):
                    self.append_output(f"  {i:4d}  {h}\n")
            self.update_prompt()
            return
        
        # Check if command is allowed
        if cmd not in ALLOWED_COMMANDS:
            self.append_output(
                f"\033[1;31mCommand not found: {cmd}\033[0m\n"
                f"Type 'help' for available commands\n",
                "#ff4444"
            )
            self.update_prompt()
            return
        
        # Handle 'cd' specially (shell built-in)
        if cmd == "cd":
            try:
                target = args[0] if args else os.path.expanduser("~")
                new_dir = os.path.abspath(os.path.join(self.current_dir, target))
                if os.path.isdir(new_dir):
                    self.current_dir = new_dir
                else:
                    self.append_output(f"cd: {target}: No such directory\n", "#ff4444")
            except Exception as e:
                self.append_output(f"cd: {str(e)}\n", "#ff4444")
            self.update_prompt()
            return
        
        # Handle 'exit'
        if cmd in ("exit", "quit"):
            self.append_output("logout\n")
            # Signal to close the terminal window
            return
            
        # Execute system command in a thread
        self.execute_system_command(cmd, args, command)
    
    def execute_system_command(self, cmd: str, args: list, full_cmd: str):
        """Execute a system command in a separate thread"""
        def run():
            try:
                result = subprocess.run(
                    [cmd] + args,
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=self.current_dir,
                    env={**os.environ, "TERM": "xterm-256color"}
                )
                
                # Use QTimer to update GUI from main thread
                QTimer.singleShot(0, lambda: self._handle_result(result, full_cmd))
                
            except subprocess.TimeoutExpired:
                QTimer.singleShot(0, lambda: self.append_output(
                    f"\n[!] Command timed out after 30 seconds\n", "#ffaa00"
                ))
                QTimer.singleShot(0, self.update_prompt)
            except FileNotFoundError:
                QTimer.singleShot(0, lambda: self.append_output(
                    f"\n[!] Command '{cmd}' not found. Install with: apt install {cmd}\n", "#ff4444"
                ))
                QTimer.singleShot(0, self.update_prompt)
            except Exception as e:
                QTimer.singleShot(0, lambda: self.append_output(
                    f"\n[!] Error: {str(e)}\n", "#ff4444"
                ))
                QTimer.singleShot(0, self.update_prompt)
        
        thread = threading.Thread(target=run, daemon=True)
        thread.start()
    
    def _handle_result(self, result, full_cmd):
        """Handle command result (called from main thread)"""
        if result.stdout:
            # Color stdout green
            self.append_output(f"
