"""
Main window implementation for the MP4 Transcriber GUI application.
"""

import os
import sys
import time
import datetime
import multiprocessing
from mp4_transcriber.gui.processor import GUIProcessor
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QCheckBox,
    QLabel,
    QFileDialog,
    QComboBox,
    QTableWidget,
    QTableWidgetItem,
    QProgressBar,
    QTextEdit,
    QHeaderView,
    QGroupBox,
    QLineEdit,
)
from PyQt6.QtCore import Qt, QThreadPool, QDir, pyqtSignal, QObject, QRunnable, pyqtSlot


class WorkerSignals(QObject):
    """
    Defines the signals available from a running worker thread.
    """

    started = pyqtSignal(str)
    progress = pyqtSignal(str, int, str)
    completed = pyqtSignal(str)
    error = pyqtSignal(str, str)
    log = pyqtSignal(str)


class TranscriptionWorker(QRunnable):
    """
    Worker thread for handling transcription tasks.
    """

    def __init__(
        self, file_path, output_dir, model, include_timestamps, auto_clean, keep_audio
    ):
        super().__init__()
        self.file_path = file_path
        self.output_dir = output_dir
        self.model = model
        self.include_timestamps = include_timestamps
        self.auto_clean = auto_clean
        self.keep_audio = keep_audio
        self.signals = WorkerSignals()
        self.processor = None

    @pyqtSlot()
    def run(self):
        """
        Execute the transcription process using multiprocessing.
        """
        try:
            self.signals.started.emit(self.file_path)
            self.signals.log.emit(
                f"Started processing {os.path.basename(self.file_path)}"
            )

            # Create processor and process the file
            self.processor = GUIProcessor(self.signals)
            self.processor.process_file(
                self.file_path,
                self.output_dir,
                self.model,
                self.include_timestamps,
                self.auto_clean,
                self.keep_audio,
            )

        except Exception as e:
            self.signals.error.emit(self.file_path, str(e))
            self.signals.log.emit(
                f"Error processing {os.path.basename(self.file_path)}: {str(e)}"
            )


class MP4TranscriberGUI(QMainWindow):
    """
    Main window for the MP4 Transcriber GUI application.
    """

    def __init__(self):
        super().__init__()

        self.threadpool = QThreadPool()
        self.file_queue = []  # List of dicts with file info and status
        self.processing = False
        self.current_file = None
        self.current_worker = None  # Keep track of current worker

        self.init_ui()

    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("MP4 Transcriber")
        self.setMinimumSize(800, 600)

        # Main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # Action buttons
        action_layout = QHBoxLayout()
        self.add_btn = QPushButton("Add Files")
        self.remove_btn = QPushButton("Remove Selected")
        self.start_btn = QPushButton("Start")
        self.stop_btn = QPushButton("Stop")

        self.add_btn.clicked.connect(self.add_files)
        self.remove_btn.clicked.connect(self.remove_selected)
        self.start_btn.clicked.connect(self.start_processing)
        self.stop_btn.clicked.connect(self.stop_processing)
        self.stop_btn.setEnabled(False)

        action_layout.addWidget(self.add_btn)
        action_layout.addWidget(self.remove_btn)
        action_layout.addWidget(self.start_btn)
        action_layout.addWidget(self.stop_btn)
        main_layout.addLayout(action_layout)

        # Files table
        files_group = QGroupBox("Files to Transcribe:")
        files_layout = QVBoxLayout()
        files_group.setLayout(files_layout)

        # Enable drops on the group box
        files_group.setAcceptDrops(True)

        self.files_table = QTableWidget(
            0, 3
        )  # Rows will be added dynamically, 3 columns
        self.files_table.setHorizontalHeaderLabels(["✓", "File", "Status"])
        self.files_table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self.files_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        files_layout.addWidget(self.files_table)
        main_layout.addWidget(files_group)

        # Options group
        options_group = QGroupBox("Transcription Options:")
        options_layout = QVBoxLayout()
        options_group.setLayout(options_layout)

        # Model selection
        model_layout = QHBoxLayout()
        model_layout.addWidget(QLabel("Model:"))
        self.model_combo = QComboBox()
        self.model_combo.addItems(["tiny", "base", "small", "medium", "large"])
        self.model_combo.setCurrentText("tiny")  # Changed default to tiny
        model_layout.addWidget(self.model_combo)
        model_layout.addStretch()
        options_layout.addLayout(model_layout)

        # Checkboxes
        self.timestamps_cb = QCheckBox("Include timestamps")
        self.clean_cb = QCheckBox("Auto-clean transcript")
        self.keep_audio_cb = QCheckBox("Keep temporary audio files")

        self.timestamps_cb.setChecked(False)  # Changed to unchecked by default
        self.clean_cb.setChecked(True)

        options_layout.addWidget(self.timestamps_cb)
        options_layout.addWidget(self.clean_cb)
        options_layout.addWidget(self.keep_audio_cb)

        # Output folder
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("Output folder:"))
        self.output_edit = QLineEdit()

        # Get default output location from environment or use fallback
        default_output = os.environ.get(
            "DEFAULT_OUTPUT_LOCATION", os.path.expanduser("~/Downloads")
        )
        self.output_edit.setText(default_output)

        self.browse_btn = QPushButton("Browse")
        self.browse_btn.clicked.connect(self.browse_output)

        output_layout.addWidget(self.output_edit)
        output_layout.addWidget(self.browse_btn)
        options_layout.addLayout(output_layout)

        main_layout.addWidget(options_group)

        # Progress group
        progress_group = QGroupBox("Current Progress:")
        progress_layout = QVBoxLayout()
        progress_group.setLayout(progress_layout)

        self.current_file_label = QLabel("No file processing")
        self.current_operation_label = QLabel("")
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)

        progress_layout.addWidget(self.current_file_label)
        progress_layout.addWidget(self.current_operation_label)
        progress_layout.addWidget(self.progress_bar)

        main_layout.addWidget(progress_group)

        # Logs
        logs_group = QGroupBox("Logs:")
        logs_layout = QVBoxLayout()
        logs_group.setLayout(logs_layout)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        logs_layout.addWidget(self.log_text)

        main_layout.addWidget(logs_group)

        # Set layout proportions
        main_layout.setStretch(1, 2)  # Files table gets more space
        main_layout.setStretch(2, 1)  # Options gets less space
        main_layout.setStretch(3, 1)  # Progress gets less space
        main_layout.setStretch(4, 2)  # Logs get more space

        self.log_message("Application started")

    def _add_file_paths(self, file_paths):
        """Adds a list of file paths to the queue, checking for duplicates."""
        added_count = 0
        for file_path in file_paths:
            # Basic check for file extension
            if file_path.lower().endswith((".mp4", ".mp3")):
                # Check if file is already in queue
                if not any(item["path"] == file_path for item in self.file_queue):
                    self.file_queue.append(
                        {
                            "path": file_path,
                            "name": os.path.basename(file_path),
                            "status": "Queued",
                            "progress": 0,
                        }
                    )
                    added_count += 1
            else:
                self.log_message(
                    f"Skipped non-MP4/MP3 file: {os.path.basename(file_path)}"
                )

        if added_count > 0:
            self.update_files_table()
            self.log_message(f"Added {added_count} file(s) to queue")

    def add_files(self):
        """Open file dialog to add MP4/MP3 files to the queue"""
        # Get default input location from environment or use fallback
        default_input = os.environ.get(
            "DEFAULT_INPUT_LOCATION", os.path.expanduser("~/Movies")
        )

        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select MP4/MP3 Files",
            default_input,
            "Media Files (*.mp4 *.mp3);;MP4 Files (*.mp4);;MP3 Files (*.mp3);;All Files (*)",  # Added MP3 support
        )

        if files:
            self._add_file_paths(files)

    def update_files_table(self):
        """Update the files table with current queue contents"""
        self.files_table.setRowCount(len(self.file_queue))

        for row, file_info in enumerate(self.file_queue):
            # Checkbox column
            checkbox = QTableWidgetItem()
            checkbox.setFlags(
                Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled
            )
            checkbox.setCheckState(Qt.CheckState.Unchecked)
            self.files_table.setItem(row, 0, checkbox)

            # File name column
            name_item = QTableWidgetItem(file_info["name"])
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.files_table.setItem(row, 1, name_item)

            # Status column
            status_item = QTableWidgetItem(file_info["status"])
            status_item.setFlags(status_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.files_table.setItem(row, 2, status_item)

    def remove_selected(self):
        """Remove selected files from the queue"""
        selected_rows = []

        for row in range(self.files_table.rowCount()):
            if self.files_table.item(row, 0).checkState() == Qt.CheckState.Checked:
                selected_rows.append(row)

        # Remove from highest index to lowest to avoid index shifting issues
        for row in sorted(selected_rows, reverse=True):
            file_name = self.file_queue[row]["name"]
            self.file_queue.pop(row)
            self.log_message(f"Removed {file_name} from queue")

        self.update_files_table()

    def browse_output(self):
        """Open folder dialog to select output directory"""
        folder = QFileDialog.getExistingDirectory(
            self, "Select Output Folder", self.output_edit.text()
        )

        if folder:
            self.output_edit.setText(folder)
            self.log_message(f"Output folder set to: {folder}")

    def start_processing(self):
        """Start processing the file queue"""
        # Check if any files are checked
        has_checked_files = False
        for row in range(self.files_table.rowCount()):
            if self.files_table.item(row, 0).checkState() == Qt.CheckState.Checked:
                has_checked_files = True
                break

        if not has_checked_files:
            self.log_message("No files are checked for processing")
            return

        if self.processing:
            return

        self.processing = True
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)

        # Disable options while processing
        self.model_combo.setEnabled(False)
        self.timestamps_cb.setEnabled(False)
        self.clean_cb.setEnabled(False)
        self.keep_audio_cb.setEnabled(False)
        self.output_edit.setEnabled(False)
        self.browse_btn.setEnabled(False)

        # Start processing the first file
        self.process_next_file()

    def stop_processing(self):
        """Stop the processing queue"""
        self.processing = False
        self.stop_btn.setEnabled(False)
        self.start_btn.setEnabled(True)

        # Re-enable options
        self.model_combo.setEnabled(True)
        self.timestamps_cb.setEnabled(True)
        self.clean_cb.setEnabled(True)
        self.keep_audio_cb.setEnabled(True)
        self.output_edit.setEnabled(True)
        self.browse_btn.setEnabled(True)

        self.log_message("Processing stopped")
        self.current_file_label.setText("Processing stopped")
        self.current_operation_label.setText("")

        # Terminate any running processes
        if (
            self.current_worker
            and hasattr(self.current_worker, "processor")
            and self.current_worker.processor
        ):
            try:
                self.current_worker.processor.terminate()
            except Exception:
                pass

        # Also try to clear the thread pool
        self.threadpool.clear()

    def process_next_file(self):
        """Process the next file in the queue"""
        # Find next checked file regardless of status
        next_file = None
        next_index = -1

        for i, file_info in enumerate(self.file_queue):
            # Check if the file is checked in the table
            if self.files_table.item(i, 0).checkState() == Qt.CheckState.Checked:
                next_file = file_info
                next_index = i
                break

        if next_file is None:
            # No more files to process
            self.processing = False
            self.stop_btn.setEnabled(False)
            self.start_btn.setEnabled(True)

            # Re-enable options
            self.model_combo.setEnabled(True)
            self.timestamps_cb.setEnabled(True)
            self.clean_cb.setEnabled(True)
            self.keep_audio_cb.setEnabled(True)
            self.output_edit.setEnabled(True)
            self.browse_btn.setEnabled(True)

            self.current_file_label.setText("All checked files processed")
            self.current_operation_label.setText("")
            self.progress_bar.setValue(0)
            self.log_message("Queue processing completed")
            return

        # Set current file
        self.current_file = next_file
        self.current_file_label.setText(f"Processing {next_file['name']}")

        # Update table
        self.file_queue[next_index]["status"] = "Processing 0%"
        self.update_files_table()

        # Create worker
        worker = TranscriptionWorker(
            next_file["path"],
            self.output_edit.text(),
            self.model_combo.currentText(),
            self.timestamps_cb.isChecked(),
            self.clean_cb.isChecked(),
            self.keep_audio_cb.isChecked(),
        )

        # Connect signals
        worker.signals.started.connect(self.on_worker_started)
        worker.signals.progress.connect(self.on_worker_progress)
        worker.signals.completed.connect(self.on_worker_completed)
        worker.signals.error.connect(self.on_worker_error)
        worker.signals.log.connect(self.log_message)

        # Store current worker reference
        self.current_worker = worker

        # Execute
        self.threadpool.start(worker)

    def on_worker_started(self, file_path):
        """Handle worker started signal"""
        pass  # Already handled in the process_next_file method

    def on_worker_progress(self, file_path, progress, operation):
        """Handle worker progress signal"""
        # Find the file in the queue
        for i, file_info in enumerate(self.file_queue):
            if file_info["path"] == file_path:
                self.file_queue[i]["status"] = f"Processing {progress}%"
                self.file_queue[i]["progress"] = progress
                self.update_files_table()
                break

        self.progress_bar.setValue(progress)
        self.current_operation_label.setText(operation)

    def on_worker_completed(self, file_path):
        """Handle worker completed signal"""
        # Find the file in the queue
        for i, file_info in enumerate(self.file_queue):
            if file_info["path"] == file_path:
                self.file_queue[i]["status"] = "Completed"
                self.update_files_table()
                break

        if self.processing:
            # Start the next file
            self.process_next_file()

    def on_worker_error(self, file_path, error_msg):
        """Handle worker error signal"""
        # Only log errors that aren't related to stopping the process
        if (
            "terminated" not in error_msg.lower()
            and "cancelled" not in error_msg.lower()
        ):
            # Find the file in the queue
            for i, file_info in enumerate(self.file_queue):
                if file_info["path"] == file_path:
                    self.file_queue[i]["status"] = "Error"
                    self.update_files_table()
                    break

            self.log_message(
                f"Error processing {os.path.basename(file_path)}: {error_msg}"
            )

        if self.processing:
            # Continue with the next file
            self.process_next_file()

    def log_message(self, message):
        """Add a message to the log with timestamp"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"{timestamp} - {message}")

    # --- Drag and Drop Event Handlers ---

    def dragEnterEvent(self, event):
        """Handle drag enter event."""
        # Check if the event contains URLs
        if event.mimeData().hasUrls():
            # Check if any URL is an MP4 or MP3 file
            for url in event.mimeData().urls():
                if url.isLocalFile() and url.toLocalFile().lower().endswith(
                    (".mp4", ".mp3")
                ):
                    event.acceptProposedAction()
                    return
        event.ignore()

    def dropEvent(self, event):
        """Handle drop event."""
        files = []
        for url in event.mimeData().urls():
            if url.isLocalFile():
                file_path = url.toLocalFile()
                if file_path.lower().endswith((".mp4", ".mp3")):
                    files.append(file_path)

        if files:
            self._add_file_paths(files)
            event.acceptProposedAction()
        else:
            event.ignore()
