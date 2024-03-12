from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QTextEdit, QScrollArea, QLabel, QListWidget, QListWidgetItem
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
import sys
import os

APP_NAME = "BeaClip"
TEXT_FONT_SIZE = 16
GLOBAL_FONT_SIZE = 12
VERSION = "V1.0.0"

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def init_ui(self):
    self.setWindowTitle(f'BeaClip {VERSION}')
    # set the color of the title bar
    self.setStyleSheet(f'''
        QWidget {{
            background-color: #f0f0f0;
            font-size: {GLOBAL_FONT_SIZE}px;
        }}''')

    # set icon
    self.setWindowIcon(QIcon(resource_path("icons/logo.svg")))
    self.resize(600, 400)

    main_layout = QVBoxLayout()

    # Top bar layout
    top_bar_layout = QHBoxLayout()

    # Clear button
    clear_button = QPushButton()
    clear_button.setIcon(QIcon(resource_path("icons/clear.svg")))
    clear_button.setToolTip("Clear All")
    clear_button.setFixedWidth(40)
    clear_button.setFixedHeight(40)
    clear_button.clicked.connect(self.clear_entries)
    top_bar_layout.addWidget(clear_button)

    # config button
    config_button = QPushButton()
    config_button.setIcon(QIcon(resource_path("icons/config.svg")))
    config_button.setToolTip("config")
    config_button.setFixedWidth(40)
    config_button.setFixedHeight(40)
    config_button.clicked.connect(self.editConfig)
    top_bar_layout.addWidget(config_button)

    # About button
    about_button = QPushButton()
    about_button.setIcon(QIcon(resource_path("icons/about.svg")))
    about_button.setToolTip("About")
    about_button.setFixedWidth(40)
    about_button.setFixedHeight(40)
    about_button.clicked.connect(self.about)
    top_bar_layout.addWidget(about_button)

    # Search bar
    self.search_bar = QLineEdit()
    self.search_bar.setClearButtonEnabled(True)
    self.search_bar.setPlaceholderText("Search...")
    self.search_bar.setFixedHeight(40)
    self.search_bar.textChanged.connect(self.filterEntries)
    top_bar_layout.addWidget(self.search_bar)

    # Add a stretch to fill the top bar
    top_bar_layout.addStretch()

    main_layout.addLayout(top_bar_layout)

    under_layout = QHBoxLayout()

    # Scroll area for clipboard entries
    self.scroll_area = QScrollArea()
    self.scroll_area.setWidgetResizable(True)
    scroll_widget = QWidget()
    self.entry_list = QListWidget()
    self.entry_list.itemSelectionChanged.connect(self.selectionChanged)
    self.entry_list.itemDoubleClicked.connect(self.showDetails)
    scroll_widget.setLayout(QVBoxLayout(scroll_widget))
    scroll_widget.layout().addWidget(self.entry_list)
    self.scroll_area.setWidget(scroll_widget)
    under_layout.addWidget(self.scroll_area)

    # Right button layout
    right_button_layout = QVBoxLayout()
    right_button_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

    copy_button = QPushButton()
    copy_button.setIcon(QIcon(resource_path("icons/copy.svg")))
    copy_button.setToolTip("Copy")
    copy_button.setFixedWidth(40)
    copy_button.setFixedHeight(40)
    copy_button.clicked.connect(self.copySelectedEntries)
    right_button_layout.addWidget(copy_button)

    delete_button = QPushButton()
    delete_button.setIcon(QIcon(resource_path("icons/delete.svg")))
    delete_button.setToolTip("Delete")
    delete_button.setFixedWidth(40)
    delete_button.setFixedHeight(40)
    delete_button.clicked.connect(self.deleteSelectedEntries)
    right_button_layout.addWidget(delete_button)

    tag_button = QPushButton()
    tag_button.setIcon(QIcon(resource_path("icons/tag.svg")))
    tag_button.setToolTip("Tag")
    tag_button.setFixedWidth(40)
    tag_button.setFixedHeight(40)
    tag_button.clicked.connect(self.tagSelectedEntries)
    right_button_layout.addWidget(tag_button)

    show_details_button = QPushButton()
    show_details_button.setIcon(QIcon(resource_path("icons/details.svg")))
    show_details_button.setToolTip("Show Details")
    show_details_button.setFixedWidth(40)
    show_details_button.setFixedHeight(40)
    show_details_button.clicked.connect(self.showDetails)
    right_button_layout.addWidget(show_details_button)

    # Add a stretch to fill the right layout
    right_button_layout.addStretch()

    under_layout.addLayout(right_button_layout)
    main_layout.addLayout(under_layout)

    self.setLayout(main_layout)

    # set font size
    self.setStyleSheet(f"QTextEdit {{ font-size: {TEXT_FONT_SIZE}px; }}")