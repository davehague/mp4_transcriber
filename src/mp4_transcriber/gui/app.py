"""
Entry point for the MP4 Transcriber GUI application.
"""
import sys
import os
import multiprocessing
from PyQt6.QtWidgets import QApplication
from mp4_transcriber.gui.main_window import MP4TranscriberGUI
from dotenv import load_dotenv

# Ensure proper multiprocessing behavior on macOS
if __name__ == "__main__":
    multiprocessing.set_start_method('spawn', force=True)

def run_gui():
    """Launch the MP4 Transcriber GUI application."""
    # Load environment variables from .env file if it exists
    load_dotenv()
    
    # On macOS, we need to use the spawn method for multiprocessing
    if sys.platform == 'darwin' and multiprocessing.get_start_method() != 'spawn':
        multiprocessing.set_start_method('spawn', force=True)
        
    app = QApplication(sys.argv)
    window = MP4TranscriberGUI()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    run_gui()
