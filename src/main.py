from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,  QInputDialog, QMessageBox, QSystemTrayIcon, QMenu, QLabel, QListWidgetItem, QDialog
from PyQt6.QtCore import Qt, QObject, pyqtSignal, QDateTime
from PyQt6.QtGui import QIcon, QAction
from database import init_database, load_entries, save_entry, update_entry, delete_entry, clear_entries
from ui import init_ui, resource_path
from config import edit_config, load_config
from utils import shorten_text
import ctypes
import sys 

APP_NAME = "BeaClip"
TEXT_FONT_SIZE = 16
GLOBAL_FONT_SIZE = 12
VERSION = "V1.0.0"
if sys.platform == "win32":
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_NAME)

# wrapper class for clipboard monitoring
class ClipboardMonitor(QObject):
    clipboardChanged = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.clipboard = QApplication.clipboard()
        self.clipboard.dataChanged.connect(self.onClipboardDataChanged)

    # only emit the signal when the clipboard has text
    def onClipboardDataChanged(self):
        mimeData = self.clipboard.mimeData()
        if mimeData.hasText():
            self.clipboardChanged.emit()

class ClipboardManager(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.monitor = ClipboardMonitor()
        self.monitor.clipboardChanged.connect(self.addClipboardEntry)
        # initialize the database and load the config first
        # to make sure the database and config file are ready
        init_database()
        load_config()
        self.createTrayIcon()
        self.loadEntries()


    def initUI(self):
        init_ui(self)

    def addEntry(self, text, timestamp, tag=None):
        entry = QListWidgetItem()
        entry.setData(Qt.ItemDataRole.UserRole, (text, timestamp, tag))
        header_widget = QWidget()
        entry_layout = QVBoxLayout()
        header_layout = QHBoxLayout()
        timestamp_label = QLabel(timestamp)
        timestamp_label.setStyleSheet(f"font-size: {GLOBAL_FONT_SIZE}px; color: #666;")
        header_layout.addWidget(timestamp_label)
        header_layout.addStretch()
        tag_label = QLabel(tag)
        tag_label.setStyleSheet(f"font-size: {GLOBAL_FONT_SIZE + 2}px; color: #666;")
        header_layout.addWidget(tag_label)
        entry_layout.addLayout(header_layout)
        text_copy = text
        shortened_text = shorten_text(text_copy)
        text_label = QLabel(shortened_text)     
        text_label.setToolTip("Double click to see the full text")
        entry_layout.addWidget(text_label)
        header_widget.setLayout(entry_layout)
        entry.setSizeHint(header_widget.sizeHint())
        self.entry_list.insertItem(0, entry)
        self.entry_list.setItemWidget(entry, header_widget)

        save_entry(text, timestamp, tag)

    def selectionChanged(self):
        pass

    def copySelectedEntries(self):
        clipboard = QApplication.clipboard()
        texts = [item.data(Qt.ItemDataRole.UserRole)[0] for item in self.entry_list.selectedItems()]
        clipboard.setText("\n".join(texts))

    def deleteSelectedEntries(self):
        selected_items = self.entry_list.selectedItems()
        if selected_items:
            for item in selected_items:
                data = item.data(Qt.ItemDataRole.UserRole)
                delete_entry(data[0], data[1], data[2])
                self.entry_list.takeItem(self.entry_list.row(item))

    def tagSelectedEntries(self):
        selected_items = self.entry_list.selectedItems()
        if selected_items:
            item = selected_items[0]
            data = item.data(Qt.ItemDataRole.UserRole)
            get_tag_dialog = QInputDialog()
            get_tag_dialog.setWindowIcon(QIcon(resource_path("icons/logo.svg")))
            tag, ok = get_tag_dialog.getText(self, "Tag Entry", "Enter a tag for the selected entry:", text=data[2])
            if ok:
                tag = tag[:10]
                update_entry(data[0], data[1], tag)
                data = (data[0], data[1], tag)
                header_widget = QWidget()
                entry_layout = QVBoxLayout()
                header_layout = QHBoxLayout()
                timestamp_label = QLabel(data[1])
                timestamp_label.setStyleSheet(f"font-size: {GLOBAL_FONT_SIZE}px; color: #666;")
                header_layout.addWidget(timestamp_label)
                header_layout.addStretch()
                tag_label = QLabel(data[2])
                tag_label.setStyleSheet(f"font-size: {GLOBAL_FONT_SIZE + 2}px; color: #666;")
                header_layout.addWidget(tag_label)
                entry_layout.addLayout(header_layout)
                # at most 50 characters and at most 4 lines
                text_copy = data[0]
                shortened_text = shorten_text(text_copy)
                text_label = QLabel(shortened_text)   
                text_label.setToolTip("Double click to see the full text")
                entry_layout.addWidget(text_label)
                header_widget.setLayout(entry_layout)
                item.setSizeHint(header_widget.sizeHint())
                self.entry_list.setItemWidget(item, header_widget)
    
    def filterEntries(self, text):
        for i in range(self.entry_list.count()):
            item = self.entry_list.item(i)
            data = item.data(Qt.ItemDataRole.UserRole) if item else None
            # lowercase comparison
            if data and text.lower() in data[0].lower():
                item.setHidden(False)
            elif item:
                item.setHidden(True)


    def addClipboardEntry(self):
        tray_menu = self.tray_icon.contextMenu()
        clipboard = QApplication.clipboard()
        mimeData = clipboard.mimeData()
        if mimeData.hasText():
            text = mimeData.text()
            timestamp = QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss")
            self.addEntry(text, timestamp)
            # also update on an entry of tray icon
            tray_text = text[:20] + "..." if len(text) > 20 else text
            tray_text = "Copied: " + tray_text
            # update the first entry
            tray_menu.actions()[0].setText(tray_text)

    def createTrayIcon(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon(resource_path("icons/logo.svg")))
        self.tray_icon.setVisible(True)

        menu = QMenu()
        copied_text_action = QAction('Clipboard is empty', self)
        show_action = QAction("Show", self)
        quit_action = QAction("Quit", self)
        hide_action = QAction("Hide", self)
        show_action.triggered.connect(self.show)
        hide_action.triggered.connect(self.hide)
        quit_action.triggered.connect(QApplication.quit)
        menu.addAction(copied_text_action)
        # set copied_text_action to unclickable
        copied_text_action.setDisabled(True)
        # add a separator
        menu.addSeparator()
        menu.addAction(show_action)
        menu.addAction(hide_action)
        menu.addAction(quit_action)
        self.tray_icon.setContextMenu(menu)
        self.tray_icon.setToolTip("BeaClip")

    def closeEvent(self, event):
        event.ignore()
        self.hide()

    def loadEntries(self):
        # Clear existing entries before loading from the database
        self.entry_list.clear()
        entries = load_entries()
        for entry in entries:
            self.addEntry(entry[0], entry[1], entry[2])

    def clear_entries(self):
        confirm = QMessageBox.question(self, "Clear Entries", "Are you sure you want to clear all entries?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.Yes:
            clear_entries()
            self.entry_list.clear()

    def editConfig(self):
        edit_config(self)

    def about(self):
        QMessageBox.about(self, f"About {APP_NAME}",
                          f"<b>{APP_NAME} {VERSION}</b><br><br>"
                          "A simple clipboard manager built with PyQt6.<br><br>"
                          "Developed by <a href='https://beacox.space/ '>BeaCox</a>"
                          "Open source on <a href='https://github.com/BeaCox/BeaClip'>GitHub</a>"
                          )

    def showDetails(self):
        selected_items = self.entry_list.selectedItems()
        if selected_items:
            item = selected_items[0]
            data = item.data(Qt.ItemDataRole.UserRole)
            detail_dialog = QDialog(self)
            detail_dialog.setWindowIcon(QIcon(resource_path("icons/logo.svg")))
            detail_dialog.resize(300, 300)
            detail_dialog.setWindowTitle("Entry Details")
            detail_layout = QVBoxLayout()
            detail_text = QTextEdit()
            detail_text.setReadOnly(True)
            detail_text.setText(data[0])
            detail_layout.addWidget(detail_text)
            detail_dialog.setLayout(detail_layout)
            detail_dialog.exec()

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    clipboard_manager = ClipboardManager()

    clipboard_manager.show()
    sys.exit(app.exec())
