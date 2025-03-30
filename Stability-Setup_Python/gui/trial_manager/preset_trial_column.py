from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QListWidget,
    QListWidgetItem,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QAbstractItemView
)
import sys
from constants import Mode, Constants
from helper.global_helpers import custom_print

class TrialColumnWidget(QWidget):
    def __init__(self):
        super().__init__()
        # Set up the overall vertical layout
        main_layout = QVBoxLayout(self)

        # Add a title at the top using a QLabel (non-editable)
        self.title_label = QLabel("Trials")
        main_layout.addWidget(self.title_label)

        # Create a QListWidget to hold the rows
        self.list_widget = QListWidget()
        # Enable dragging and dropping of items within this list
        self.list_widget.setDragEnabled(True)
        self.list_widget.setAcceptDrops(True)
        self.list_widget.setDropIndicatorShown(True)
        self.list_widget.setDragDropMode(QAbstractItemView.InternalMove)
        main_layout.addWidget(self.list_widget)

        # Add a couple of initial rows
        self.add_row("Scan")
        self.add_row("Mppt")

        # Add the "Add Row" widget as the last item in the list widget
        self.add_button_item = QListWidgetItem(self.list_widget)
        self.add_row_widget = AddTrialRowWidget(self)
        self.add_button_item.setSizeHint(self.add_row_widget.sizeHint())
        self.list_widget.addItem(self.add_button_item)
        self.list_widget.setItemWidget(self.add_button_item, self.add_row_widget)

    def add_row(self, text, insert_index=None):
        """Insert a new row widget before the add button row."""
        new_item = QListWidgetItem()
        row_widget = TrialRow(text, self.list_widget)
        new_item.setSizeHint(row_widget.sizeHint())

        # If no explicit index is provided, insert before the last item (the add button)
        if insert_index is None:
            count = self.list_widget.count()
            insert_index = count - 1 if count > 0 else 0

        self.list_widget.insertItem(insert_index, new_item)
        self.list_widget.setItemWidget(new_item, row_widget)

    def add_new_row(self, mode):
        """Callback for the add button to insert a new row."""
        if mode == Mode.MPPT:
            self.add_row("Mppt")
        elif mode == Mode.SCAN:
            self.add_row("Scan")


class TrialRow(QWidget):
    def __init__(self, text, parent_list):
        super().__init__()
        self.parent_list = parent_list

        # Set up a horizontal layout for the row
        layout = QHBoxLayout(self)

        # Row name is non-editable (QLabel)
        self.name_edit = QLabel(text)
        layout.addWidget(self.name_edit)

        # Add additional buttons for the row
        self.edit_button = QPushButton("View / Edit")
        self.delete_button = QPushButton("Delete")
        layout.addWidget(self.edit_button)
        layout.addWidget(self.delete_button)
        self.delete_button.clicked.connect(self.remove_row)

        layout.addStretch()

    def remove_row(self):
        """Removes this row from the list widget."""
        count = self.parent_list.count()
        for index in range(count):
            item = self.parent_list.item(index)
            widget = self.parent_list.itemWidget(item)
            if widget == self:
                self.parent_list.takeItem(index)
                break


class AddTrialRowWidget(QWidget):
    def __init__(self, main_widget):
        super().__init__()
        self.main_widget = main_widget
        layout = QHBoxLayout(self)
        self.add_scan = QPushButton("Add scan")
        self.add_mppt = QPushButton("Add mppt")
        layout.addWidget(self.add_scan)
        layout.addWidget(self.add_mppt)
        layout.addStretch()
        # Use lambda to ensure the handler is called on button click
        self.add_scan.clicked.connect(lambda: self.handle_add(Mode.SCAN))
        self.add_mppt.clicked.connect(lambda: self.handle_add(Mode.MPPT))

    def handle_add(self, mode):
        """When clicked, instruct the main widget to add a new row."""
        self.main_widget.add_new_row(mode)
