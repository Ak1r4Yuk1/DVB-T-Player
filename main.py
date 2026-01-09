import sys
import os
import subprocess
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QPushButton, QListWidget, QHBoxLayout, QFrame, 
                             QLabel, QLineEdit, QSplitter, QProgressBar)
from PyQt6.QtCore import Qt, QProcess, QSize
from PyQt6.QtGui import QFont, QIcon, QShortcut, QKeySequence

class MeTVClone(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DVB-T Standalone Player")
        self.setMinimumSize(1200, 800)
        
        self.conf_file = "channels.conf"
        self.tuning_data = "it-All"
        
        # Pulizia cartella MPV per evitare warning
        if os.path.exists(os.path.expanduser("~/.mpv")):
            os.system("rm -rf ~/.mpv")

        self.init_ui()
        self.load_channels_from_conf()

        # Shortcut CTRL+F per lanciare MPV esternamente in fullscreen
        self.fs_shortcut = QShortcut(QKeySequence("Ctrl+F"), self)
        self.fs_shortcut.activated.connect(self.play_external_fullscreen)

    def init_ui(self):
        # Tema scuro e stili (NON TOCCATI)
        self.setStyleSheet("""
            QMainWindow { background-color: #121212; }
            QWidget { background-color: #121212; color: #e0e0e0; font-family: 'Segoe UI', sans-serif; }
            QListWidget { 
                background-color: #1e1e1e; 
                border: 1px solid #333; 
                border-radius: 5px; 
                outline: none;
                padding: 5px;
            }
            QListWidget::item { padding: 10px; border-bottom: 1px solid #252525; }
            QListWidget::item:selected { background-color: #005fb8; color: white; border-radius: 3px; }
            QLineEdit { 
                padding: 8px; 
                background-color: #252525; 
                border: 1px solid #333; 
                border-radius: 4px; 
                color: white; 
            }
            QPushButton { 
                padding: 8px 15px; 
                background-color: #333; 
                border-radius: 4px; 
                font-weight: bold; 
            }
            QPushButton:hover { background-color: #444; }
            QPushButton#scanBtn { background-color: #004a8d; }
            QPushButton#scanBtn:hover { background-color: #005fb8; }
            QLabel#status { color: #888; font-size: 11px; }
        """)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)

        # Barra superiore (Ricerca e Scansione)
        top_bar = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Cerca canale... (CTRL+F per Fullscreen esterno)")
        self.search_input.textChanged.connect(self.filter_channels)
        
        self.btn_scan = QPushButton("Avvia Nuova Scansione")
        self.btn_scan.setObjectName("scanBtn")
        self.btn_scan.clicked.connect(self.run_full_scan)
        
        top_bar.addWidget(self.search_input)
        top_bar.addWidget(self.btn_scan)
        main_layout.addLayout(top_bar)

        # Splitter centrale
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Sidebar sinistra
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0,0,0,0)
        
        self.list_widget = QListWidget()
        self.list_widget.itemDoubleClicked.connect(self.play_channel)
        left_layout.addWidget(self.list_widget)
        
        self.status_label = QLabel("Pronto")
        self.status_label.setObjectName("status")
        left_layout.addWidget(self.status_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("height: 10px;")
        left_layout.addWidget(self.progress_bar)

        # Area Video destra
        self.video_frame = QFrame()
        self.video_frame.setStyleSheet("background-color: #000; border-radius: 8px;")
        
        self.splitter.addWidget(left_widget)
        self.splitter.addWidget(self.video_frame)
        self.splitter.setStretchFactor(1, 4)
        
        main_layout.addWidget(self.splitter)

        # Processo per la scansione
        self.scan_process = QProcess()
        self.scan_process.readyReadStandardOutput.connect(self.handle_scan_output)
        self.scan_process.finished.connect(self.on_scan_finished)

    def load_channels_from_conf(self):
        self.all_channel_names = []
        if os.path.exists(self.conf_file):
            with open(self.conf_file, 'r') as f:
                for line in f:
                    if line.startswith("["):
                        self.all_channel_names.append(line.strip("[]\n "))
            self.update_list(self.all_channel_names)
            self.status_label.setText(f"Caricati {len(self.all_channel_names)} canali da {self.conf_file}")
        else:
            self.status_label.setText("Nessuna lista canali trovata. Avvia una scansione.")

    def update_list(self, items):
        self.list_widget.clear()
        self.list_widget.addItems(items)

    def filter_channels(self):
        search_text = self.search_input.text().lower()
        filtered = [name for name in self.all_channel_names if search_text in name.lower()]
        self.update_list(filtered)

    def run_full_scan(self):
        if not os.path.exists(self.tuning_data):
            self.status_label.setText("Download it-All...")
            os.system(f"curl -L https://git.linuxtv.org/dtv-scan-tables.git/plain/dvb-t/it-All -o {self.tuning_data}")

        self.btn_scan.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        self.status_label.setText("Scansione hardware in corso... attendere...")
        self.list_widget.clear()
        
        if os.path.exists(self.conf_file):
            os.remove(self.conf_file)
            
        self.scan_process.start("dvbv5-scan", [self.tuning_data, "-o", self.conf_file])

    def handle_scan_output(self):
        out = self.scan_process.readAllStandardOutput().data().decode()
        if "scanning" in out.lower():
            self.status_label.setText(f"Scansione frequenza...")

    def on_scan_finished(self):
        self.btn_scan.setEnabled(True)
        self.progress_bar.setVisible(False)
        self._deduplicate_channels_file(self.conf_file) # Deduplicate the file on disk
        self.load_channels_from_conf()

    def stop_all(self):
        os.system("killall -9 dvbv5-zap mpv 2>/dev/null")

    def play_channel(self):
        item = self.list_widget.currentItem()
        if not item: return
        
        channel_name = item.text()
        wid = int(self.video_frame.winId())
        self.stop_all()
        
        zap_cmd = f'dvbv5-zap -c {self.conf_file} -r -p -o - "{channel_name}"'
        player_cmd = f'mpv --wid={wid} --vo=x11 --cache=yes --no-video-aspect-override fd://0'
        
        full_command = f"{zap_cmd} | {player_cmd} &"
        self.status_label.setText(f"Sintonizzato su: {channel_name}")
        os.system(full_command)

    def play_external_fullscreen(self):
        """Lancia lo stream in una finestra MPV esterna separata con fullscreen attivo"""
        item = self.list_widget.currentItem()
        if not item: return
        
        channel_name = item.text()
        self.stop_all()
        
        # Lancio esterno: rimosso --wid, aggiunto --fs (fullscreen)
        zap_cmd = f'dvbv5-zap -c {self.conf_file} -r -p -o - "{channel_name}"'
        player_cmd = f'mpv --fs --vo=gpu --cache=yes fd://0'
        
        full_command = f"{zap_cmd} | {player_cmd} &"
        self.status_label.setText(f"Fullscreen esterno: {channel_name}")
        os.system(full_command)

    def closeEvent(self, event):
        self.stop_all()
        event.accept()

    def _deduplicate_channels_file(self, conf_file_path):
        if not os.path.exists(conf_file_path):
            return

        lines_to_write = []
        seen_channel_names = set()
        current_channel_block = []
        current_channel_name = None

        with open(conf_file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                stripped_line = line.strip()
                if stripped_line.startswith('[') and stripped_line.endswith(']'):
                    # New channel block starts
                    if current_channel_block:
                        # Process previous block if it exists
                        if current_channel_name and current_channel_name not in seen_channel_names:
                            lines_to_write.extend(current_channel_block)
                            seen_channel_names.add(current_channel_name)
                    
                    # Start new block
                    current_channel_name = stripped_line[1:-1].strip()
                    current_channel_block = [line] # Add the '[' line
                else:
                    # Line belongs to current channel block
                    current_channel_block.append(line)
            
            # Process the last channel block
            if current_channel_block and current_channel_name and current_channel_name not in seen_channel_names:
                lines_to_write.extend(current_channel_block)

        # Write the deduplicated content back to the file
        with open(conf_file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines_to_write)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = MeTVClone()
    win.show()
    sys.exit(app.exec())