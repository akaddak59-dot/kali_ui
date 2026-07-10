#!/usr/bin/env python3
"""
Kali Linux Simulator - Security Tools Panel
Complete categorized security tools interface with search and execution
"""

import subprocess
import threading
import os
import sys
from typing import Dict, List
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QPushButton, QLineEdit, QScrollArea, QFrame, QGroupBox,
    QTreeWidget, QTreeWidgetItem, QTextEdit, QSplitter,
    QTabWidget, QApplication, QComboBox
)
from PySide6.QtCore import Qt, Signal, QTimer, QSize
from PySide6.QtGui import QFont, QIcon, QColor, QPixmap


class ToolCard(QFrame):
    """Individual tool card with icon, name, and action"""
    
    def __init__(self, name: str, category: str, description: str, 
                 command: str, icon_char: str = "🔧"):
        super().__init__()
        self.name = name
        self.category = category
        self.description = description
        self.command = command
        self.icon_char = icon_char
        
        self.setup_ui()
        
    def setup_ui(self):
        self.setFixedSize(180, 120)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("""
            ToolCard {
                background-color: rgba(15, 15, 15, 220);
                border: 1px solid #333333;
                border-radius: 8px;
                padding: 8px;
            }
            ToolCard:hover {
                border: 1px solid #00ff00;
                background-color: rgba(0, 50, 0, 100);
            }
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)
        
        # Icon
        icon_label = QLabel(self.icon_char)
        icon_label.setStyleSheet("font-size: 24px;")
        layout.addWidget(icon_label)
        
        # Name
        name_label = QLabel(self.name)
        name_label.setStyleSheet("color: #00ff00; font-weight: bold; font-size: 12px;")
        layout.addWidget(name_label)
        
        # Description
        desc_label = QLabel(self.description[:40] + "...")
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #888888; font-size: 9px;")
        layout.addWidget(desc_label)
        
        # Command hint
        cmd_label = QLabel(f"$ {self.command}")
        cmd_label.setStyleSheet("color: #555555; font-size: 8px; font-family: monospace;")
        layout.addWidget(cmd_label)
        
        layout.addStretch()
        self.setLayout(layout)


class ToolsPanel(QWidget):
    """Main security tools panel with categories"""
    
    # Comprehensive tools database
    TOOLS = {
        "Information Gathering": [
            ("nmap", "Network scanner - port discovery & service detection", "nmap -sV target"),
            ("masscan", "Mass IP port scanner", "masscan 192.168.1.0/24 -p80"),
            ("rustscan", "Fast port scanner written in Rust", "rustscan -a target"),
            ("recon-ng", "Full-featured recon framework", "recon-ng"),
            ("theharvester", "Email, domain & subdomain enumeration", "theharvester -d domain.com"),
            ("sublist3r", "Fast subdomain enumeration", "sublist3r -d domain.com"),
            ("amass", "In-depth DNS enumeration & OSINT", "amass enum -d domain.com"),
            ("dnsenum", "DNS enumeration tool", "dnsenum domain.com"),
            ("dnsrecon", "DNS reconnaissance tool", "dnsrecon -d domain.com"),
            ("whois", "Domain registration lookup", "whois domain.com"),
            ("shodan", "Shodan search engine CLI", "shodan search 'port:22'"),
            ("censys", "Censys search CLI", "censys search 'services.port:22'"),
        ],
        "Vulnerability Analysis": [
            ("nikto", "Web server vulnerability scanner", "nikto -h target"),
            ("wpscan", "WordPress vulnerability scanner", "wpscan --url target.com"),
            ("joomscan", "Joomla vulnerability scanner", "joomscan -u target.com"),
            ("droopescan", "Drupal/Joomla/Moodle scanner", "droopescan scan drupal -u target.com"),
            ("openvas", "Open Vulnerability Assessment System", "gvm-start"),
            ("nessus", "Nessus vulnerability scanner", "nessuscli"),
            ("nuclei", "Fast vulnerability scanner", "nuclei -u target.com"),
            ("wapiti", "Web application vulnerability scanner", "wapiti -u target.com"),
            ("arachni", "Web application security scanner", "arachni target.com"),
            ("skipfish", "Web application security scanner", "skipfish -o output target.com"),
            ("whatweb", "Web technology identification", "whatweb target.com"),
            ("wappalyzer", "Web technology detector", "wappalyzer target.com"),
        ],
        "Web Application Testing": [
            ("sqlmap", "SQL injection automation tool", "sqlmap -u 'target.com?id=1'"),
            ("gobuster", "Directory/file brute-forcing", "gobuster dir -u target.com -w wordlist.txt"),
            ("dirb", "Web content scanner", "dirb http://target.com"),
            ("wfuzz", "Web fuzzer for parameter discovery", "wfuzz -c -z file,wordlist.txt target.com/FUZZ"),
            ("ffuf", "Fast web fuzzer", "ffuf -u target.com/FUZZ -w wordlist.txt"),
            ("burpsuite", "Web application testing platform", "burpsuite"),
            ("zap", "OWASP ZAP proxy", "zap.sh"),
            ("commix", "Command injection automation", "commix -u 'target.com?cmd='"),
            ("beef", "Browser exploitation framework", "beef-xss"),
            ("setoolkit", "Social Engineer Toolkit", "setoolkit"),
            ("hydra", "Online password brute-forcer", "hydra -l admin -P wordlist.txt target.com http-post-form"),
            ("medusa", "Parallel password brute-forcer", "medusa -h target -u admin -P wordlist.txt -M http"),
        ],
        "Exploitation": [
            ("metasploit", "Exploitation framework", "msfconsole"),
            ("msfvenom", "Payload generator", "msfvenom -p linux/x64/shell_reverse_tcp"),
            ("searchsploit", "Exploit database search", "searchsploit apache 2.4"),
            ("veil", "Payload generator (AV evasion)", "veil"),
            ("empire", "Post-exploitation framework", "powershell-empire"),
            ("crackmapexec", "Network service exploitation", "crackmapexec smb 192.168.1.0/24"),
            ("impacket", "Protocol exploitation toolkit", "impacket-smbexec domain/user:pass@target"),
            ("responder", "LLMNR/NBT-NS/mDNS poisoner", "responder -I eth0"),
            ("evil-winrm", "WinRM shell for testing", "evil-winrm -i target -u user -p pass"),
            ("psexec", "Remote command execution", "impacket-psexec domain/user:pass@target"),
            ("wmiexec", "WMI command execution", "impacket-wmiexec domain/user:pass@target"),
        ],
        "Password Attacks": [
            ("john", "John the Ripper - password cracker", "john --wordlist=wordlist.txt hash.txt"),
            ("hashcat", "GPU-accelerated password recovery", "hashcat -m 0 -a 0 hash.txt wordlist.txt"),
            ("hydra", "Online password brute-forcer", "hydra -l admin -P wordlist.txt ssh://target"),
            ("hash-identifier", "Hash type identification", "hash-identifier"),
            ("hashid", "Hash type identification", "hashid hash.txt"),
            ("crunch", "Wordlist generator", "crunch 8 10 abcdef123 > wordlist.txt"),
            ("cupp", "Common User Passwords Profiler", "cupp -i"),
            ("maskprocessor", "Mask-based password generator", "mp64 ?l?l?l?l?l?l?d?d"),
            ("cewl", "Custom wordlist generator from URL", "cewl target.com -w wordlist.txt"),
            ("rsmangler", "Wordlist mutation tool", "rsmangler wordlist.txt > mutated.txt"),
            ("pdfcrack", "PDF password cracker", "pdfcrack -f file.pdf"),
        ],
        "Wireless Testing": [
            ("aircrack-ng", "WEP/WPA cracker suite", "aircrack-ng -w wordlist.txt capture.cap"),
            ("airodump-ng", "Wireless packet capture", "airodump-ng wlan0"),
            ("aireplay-ng", "Packet injection tool", "aireplay-ng -0 5 -a AP_MAC wlan0"),
            ("airmon-ng", "WLAN monitor mode manager", "airmon-ng start wlan0"),
            ("kismet", "Wireless network detector", "kismet"),
            ("reaver", "WPS brute-force tool", "reaver -i mon0 -b BSSID"),
            ("pixiewps", "WPS offline PIN cracking", "pixiewps -e ..."),
            ("bully", "WPS brute-force (reaver alternative)", "bully mon0 -b BSSID"),
            ("mdk3", "Wireless DoS testing", "mdk3 mon0 a -a BSSID"),
            ("hcxdumptool", "PMKID capture tool", "hcxdumptool -o capture.pcapng -i wlan0"),
            ("hcxpcaptool", "Convert capture to hashcat format", "hcxpcaptool -z hash.txt capture.pcapng"),
        ],
        "Sniffing & Spoofing": [
            ("wireshark", "Network protocol analyzer", "wireshark"),
            ("tshark", "CLI packet analyzer", "tshark -i eth0 -w capture.pcap"),
            ("tcpdump", "CLI packet capture", "tcpdump -i eth0 -w capture.pcap"),
            ("bettercap", "MITM framework with UI", "bettercap -eval 'set net.sniff.verbose true; net.sniff on'"),
            ("ettercap", "MITM attack framework", "ettercap -T -M arp /target// /gateway//"),
            ("mitmproxy", "HTTPS interception proxy", "mitmproxy"),
            ("mitm6", "IPv6 MITM attack tool", "mitm6 -d domain.com"),
            ("arpspoof", "ARP spoofing tool", "arpspoof -i eth0 -t target gateway"),
            ("dnsspoof", "DNS spoofing tool", "dnsspoof -i eth0"),
            ("dnschef", "DNS proxy/spoofer", "dnschef --fakeip 192.168.1.100"),
            ("netsniff-ng", "Zero-copy packet analyzer", "netsniff-ng -i eth0"),
        ],
        "Post-Exploitation": [
            ("bloodhound", "AD relationship visualizer", "bloodhound"),
            ("sharphound", "BloodHound ingestor", "Sharphound.exe -c All"),
            ("certipy", "AD certificate abuse tool", "certipy find -u user@domain -p pass -dc-ip target"),
            ("kerbrute", "Kerberos pre-auth brute-force", "kerbrute userenum -d domain.com userlist.txt"),
            ("ldapdomaindump", "LDAP domain information dump", "ldapdomaindump ldap://target -u domain\\user -p pass"),
            ("rubeus", "Kerberos abuse toolkit", "Rubeus.exe kerberoast"),
            ("mimikatz", "Windows credential extraction", "mimikatz"),
            ("chisel", "TCP/UDP tunneling tool", "chisel server -p 8080 --reverse"),
            ("ligolo-ng", "Advanced tunneling/pivoting", "ligolo-ng -selfcert"),
            ("gost", "Secure tunnel proxy", "gost -L :8080"),
        ],
        "Reverse Engineering": [
            ("gdb", "GNU Debugger", "gdb ./binary"),
            ("radare2", "Reverse engineering framework", "r2 ./binary"),
            ("ghidra", "NSA reverse engineering tool", "ghidra"),
            ("ida", "Interactive disassembler", "ida64"),
            ("ollydbg", "32-bit debugger", "ollydbg.exe"),
            ("x64dbg", "64-bit debugger", "x64dbg.exe"),
            ("strings", "Extract strings from binary", "strings binary"),
            ("objdump", "Display binary information", "objdump -d binary"),
            ("nm", "Symbol listing from binary", "nm binary"),
            ("strace", "System call tracer", "strace -f ./binary"),
            ("ltrace", "Library call tracer", "ltrace ./binary"),
        ],
        "Forensics": [
            ("autopsy", "Digital forensics platform", "autopsy"),
            ("sleuthkit", "Forensic analysis toolkit", "fls -r image.dd"),
            ("foremost", "File carving tool", "foremost -i image.dd"),
            ("scalpel", "Fast file carver", "scalpel image.dd"),
            ("bulk_extractor", "Digital media feature extractor", "bulk_extractor image.dd"),
            ("volatility", "Memory forensics framework", "volatility -f memory.dump imageinfo"),
            ("binwalk", "Firmware analysis tool", "binwalk firmware.bin"),
            ("dcfldd", "Enhanced dd for forensics", "dcfldd if=/dev/sda of=image.dd"),
            ("guymager", "Disk imaging tool", "guymager"),
            ("testdisk", "Data recovery tool", "testdisk /dev/sda"),
            ("photorec", "Photo recovery tool", "photorec /dev/sda"),
        ],
    }
    
    def __init__(self, session_manager):
        super().__init__()
        self.session = session_manager
        self.setup_ui()
        self.populate_tools()
    
    def setup_ui(self):
        """Setup the tools panel UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Header
        header = QLabel("⚔ KALI SECURITY TOOLS ⚔")
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #00ff00;
            letter-spacing: 4px;
            padding: 10px;
        """)
        layout.addWidget(header)
        
        # Search bar
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search tools (name or category)...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #1a1a1a;
                color: #00ff00;
                border: 1px solid #333333;
                border-radius: 4px;
                padding: 8px 15px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 1px solid #00ff00;
            }
        """)
        self.search_input.textChanged.connect(self.filter_tools)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        
        # Tab widget for categories
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #333333;
                background-color: #0a0a0a;
                border-radius: 4px;
            }
            QTabBar::tab {
                background-color: #1a1a1a;
                color: #888888;
                border: 1px solid #333333;
                padding: 8px 15px;
                margin-right: 2px;
                font-size: 10px;
            }
            QTabBar::tab:selected {
                background-color: #0a0a0a;
                color: #00ff00;
                border-bottom: 2px solid #00ff00;
            }
            QTabBar::tab:hover {
                background-color: #2a2a2a;
            }
        """)
        
        # Stats label
        self.stats_label = QLabel()
        self.stats_label.setStyleSheet("color: #888888; font-size: 10px; padding: 5px;")
        
        layout.addWidget(self.tab_widget, 1)
        layout.addWidget(self.stats_label)
        
        self.setLayout(layout)
    
    def populate_tools(self, filter_text: str = ""):
        """Populate tool cards in categories"""
        self.tab_widget.clear()
        
        total_tools = 0
        
        for category, tools in self.TOOLS.items():
            if filter_text:
                filtered = [t for t in tools if filter_text.lower() in t[0].lower() or 
                           filter_text.lower() in t[1].lower() or
                           filter_text.lower() in category.lower()]
                if not filtered:
                    continue
            else:
                filtered = tools
            
            # Create tab content
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
            
            content = QWidget()
            content.setStyleSheet("background: transparent;")
            grid = QGridLayout()
            grid.setSpacing(8)
            
            icons = ["🔍", "🌐", "💻", "⚡", "🔑", "📡", "🕵️", "🛠️", "🧬", "🔬"]
            
            for i, (name, desc, cmd) in enumerate(filtered):
                tool_card = ToolCard(name, category, desc, cmd, icons[i % len(icons)])
                row = i // 3
                col = i % 3
                grid.addWidget(tool_card, row, col)
            
            grid.addItem(QVBoxLayout().addStretch(), (len(filtered) // 3) + 1, 0)
            content.setLayout(grid)
            scroll.setWidget(content)
            
            self.tab_widget.addTab(scroll, f"  {category} ({len(filtered)})  ")
            total_tools += len(filtered)
        
        self.stats_label.setText(f"📊 Total: {total_tools} tools available | Authorized Security Testing Only")
    
    def filter_tools(self, text: str):
        """Filter tools by search text"""
        self.populate_tools(text)
