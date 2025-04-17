import os
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QLineEdit,
    QFileDialog,
    QMessageBox,
    QHeaderView,
    QAbstractItemView,
    QInputDialog,  # Import QInputDialog
)
from PyQt6.QtCore import Qt


class QuickPathDialog(QDialog):
    """
    Dialog for managing quick access paths (name and directory).
    """

    def __init__(self, current_paths, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Manage Quick Paths")
        self.setMinimumSize(500, 300)

        # Store a copy of the paths to modify
        self.paths = current_paths.copy()

        # Main layout
        layout = QVBoxLayout(self)

        # Table to display paths
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Name", "Path"])
        self.table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )  # Only allow selecting one row
        self.populate_table()
        layout.addWidget(self.table)

        # Buttons for editing
        button_layout = QHBoxLayout()
        self.add_btn = QPushButton("Add")
        self.edit_btn = QPushButton("Edit")
        self.delete_btn = QPushButton("Delete")

        self.add_btn.clicked.connect(self.add_path)
        self.edit_btn.clicked.connect(self.edit_path)
        self.delete_btn.clicked.connect(self.delete_path)

        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.edit_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addStretch()
        layout.addLayout(button_layout)

        # Dialog buttons (Save/Cancel)
        dialog_button_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save")
        self.cancel_btn = QPushButton("Cancel")

        self.save_btn.clicked.connect(
            self.accept
        )  # accept() closes dialog and returns QDialog.DialogCode.Accepted
        self.cancel_btn.clicked.connect(
            self.reject
        )  # reject() closes dialog and returns QDialog.DialogCode.Rejected

        dialog_button_layout.addStretch()
        dialog_button_layout.addWidget(self.save_btn)
        dialog_button_layout.addWidget(self.cancel_btn)
        layout.addLayout(dialog_button_layout)

        self.setLayout(layout)

    def populate_table(self):
        """Fills the table with the current paths."""
        self.table.setRowCount(len(self.paths))
        for row, (name, path) in enumerate(self.paths.items()):
            name_item = QTableWidgetItem(name)
            path_item = QTableWidgetItem(path)
            # Make items non-editable directly in the table
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            path_item.setFlags(path_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 0, name_item)
            self.table.setItem(row, 1, path_item)

    def add_path(self):
        """Adds a new path entry."""
        # Use QInputDialog to get the name
        name, ok1 = QInputDialog.getText(self, "Add Path", "Enter a name:")
        if ok1 and name:
            # Ensure name is not empty after stripping whitespace
            name = name.strip()
            if not name:
                QMessageBox.warning(self, "Invalid Name", "The name cannot be empty.")
                return

            path = QFileDialog.getExistingDirectory(
                self, "Select Directory", os.path.expanduser("~")
            )
            if path:
                if name in self.paths:
                    QMessageBox.warning(
                        self, "Duplicate Name", f"The name '{name}' already exists."
                    )
                    return
                self.paths[name] = path
                self.populate_table()  # Refresh table

    def edit_path(self):
        """Edits the selected path entry."""
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(
                self, "Selection Required", "Please select a path to edit."
            )
            return

        old_name = self.table.item(selected_row, 0).text()
        old_path = self.table.item(selected_row, 1).text()

        # Get new name using QInputDialog
        new_name, ok1 = QInputDialog.getText(
            self,
            "Edit Path Name",
            "Enter new name:",
            QLineEdit.EchoMode.Normal,
            old_name,
        )
        if not ok1:
            return  # User cancelled name edit

        new_name = new_name.strip()  # Remove leading/trailing whitespace
        if not new_name:
            QMessageBox.warning(self, "Invalid Name", "The name cannot be empty.")
            return

        # Check if name changed and if the new name conflicts
        if new_name != old_name and new_name in self.paths:
            QMessageBox.warning(
                self, "Duplicate Name", f"The name '{new_name}' already exists."
            )
            return

        # Get new path
        new_path = QFileDialog.getExistingDirectory(
            self, "Select New Directory", old_path
        )
        if not new_path:
            return  # User cancelled path selection

        # Update the dictionary
        del self.paths[old_name]  # Remove old entry
        self.paths[new_name] = new_path  # Add new entry
        self.populate_table()  # Refresh table

    def delete_path(self):
        """Deletes the selected path entry."""
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(
                self, "Selection Required", "Please select a path to delete."
            )
            return

        name_to_delete = self.table.item(selected_row, 0).text()

        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete the path '{name_to_delete}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            if name_to_delete in self.paths:
                del self.paths[name_to_delete]
                self.populate_table()  # Refresh table

    def get_paths(self):
        """Returns the modified paths dictionary."""
        return self.paths


# Example usage (for testing)
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    # Example initial paths
    initial_paths = {
        "Downloads": os.path.expanduser("~/Downloads"),
        "Documents": os.path.expanduser("~/Documents"),
    }
    dialog = QuickPathDialog(initial_paths)
    if dialog.exec():  # Show the dialog modally
        print("Saved paths:", dialog.get_paths())
    else:
        print("Cancelled")
    sys.exit()
