import yaml
import os
import sys
from datetime import datetime, timedelta
from os.path import expanduser, join
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QCheckBox, QSpinBox, QLabel, QHBoxLayout, QDialogButtonBox
from database import delete_entry_created_before


CONFIG_PATH = join(expanduser("~"), ".beaclip", "config.yml")

def load_config():
    try:
        with open(CONFIG_PATH, "r") as f:
            config = yaml.safe_load(f)
    except (FileNotFoundError, yaml.YAMLError):
        config = {
            "autostart": False,
            "max_history_days": 30
        }
    autostart_setup(config["autostart"])
    clean_expired_entries(config["max_history_days"])

    return config

def save_config(config):
    try:
        config_dir = join(expanduser("~"), ".beaclip")
        os.makedirs(config_dir, exist_ok=True)
        with open(CONFIG_PATH, "w") as f:
            yaml.safe_dump(config, f)
    except Exception as e:
        print(f"Error saving config: {e}")

def edit_config(parent):
    config = load_config()
    dialog = QDialog(parent)
    dialog.setWindowTitle("Edit Config")

    layout = QVBoxLayout()

    autostart_checkbox = QCheckBox("Start on system boot")
    autostart_checkbox.setChecked(config["autostart"])
    layout.addWidget(autostart_checkbox)

    max_history_days_label = QLabel("Max history days:")
    max_history_days_spin = QSpinBox()
    max_history_days_spin.setRange(1, 365)
    max_history_days_spin.setValue(config["max_history_days"])
    history_layout = QHBoxLayout()
    history_layout.addWidget(max_history_days_label)
    history_layout.addWidget(max_history_days_spin)
    layout.addLayout(history_layout)

    # All changes require a reboot to take effect
    reboot_label = QLabel("\nAll changes require a reboot to take effect!")
    reboot_label.setStyleSheet("color: red")
    layout.addWidget(reboot_label)

    buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
    buttons.accepted.connect(dialog.accept)
    buttons.rejected.connect(dialog.reject)
    layout.addWidget(buttons)

    dialog.setLayout(layout)

    if dialog.exec() == QDialog.DialogCode.Accepted:
        config["autostart"] = autostart_checkbox.isChecked()
        config["max_history_days"] = max_history_days_spin.value()
        save_config(config)

def autostart_setup(enabled):
    app_path = os.path.realpath(sys.argv[0])

    if sys.platform == "win32":
        # Windows
        import winreg

        # register/unregister the app to run on system boot
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
        if enabled:
            winreg.SetValueEx(key, "BeaClip", 0, winreg.REG_SZ, f'"{app_path}"')
        else:
            try:
                winreg.DeleteValue(key, "BeaClip")
            except FileNotFoundError:
                pass
    else:
        # Linux and macOS
        # create/remove a .desktop file in ~/.config/autostart
        autostart_dir = os.path.join(os.path.expanduser("~"), ".config", "autostart")
        autostart_file = os.path.join(autostart_dir, "beaclip.desktop")

        if enabled:
            os.makedirs(autostart_dir, exist_ok=True)
            with open(autostart_file, "w") as f:
                f.write(f"[Desktop Entry]\nType=Application\nExec={app_path}\nHidden=false\nX-GNOME-Autostart-enabled=true\nName=BeaClip")
        else:
            try:
                os.remove(autostart_file)
            except FileNotFoundError:
                pass

def clean_expired_entries(max_history_days):
    threshold_timestamp = (datetime.now() - timedelta(days=max_history_days)).strftime("%Y-%m-%d %H:%M:%S")
    delete_entry_created_before(threshold_timestamp)