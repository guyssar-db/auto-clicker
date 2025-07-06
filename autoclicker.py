import sys
import json
import threading
import time
import pyautogui
import keyboard
from pynput import mouse  # สำหรับ Pick Location
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QRadioButton, QComboBox, QSpinBox,
    QInputDialog, QGroupBox,
)
from PyQt5.QtCore import QLocale

PROFILES_FILE = "profiles.json"

class AutoClicker(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Advanced Auto Clicker by guyssar")
        self.hotkey = 'F6'
        self.is_running = False

        self.layout = QVBoxLayout()
        self.layout.setSpacing(10)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.setWindowIcon(QIcon("./icon.ico"))
        self.locale = QLocale(QLocale.English)  # บังคับเลขอารบิก

        # === Click Interval ===
        interval_group = QGroupBox("Click Interval")
        interval_layout = QHBoxLayout()
        self.interval_hours = QSpinBox(); self.interval_hours.setRange(0, 24); self.interval_hours.setLocale(self.locale)
        self.interval_mins = QSpinBox(); self.interval_mins.setRange(0, 60); self.interval_mins.setLocale(self.locale)
        self.interval_secs = QSpinBox(); self.interval_secs.setRange(0, 60); self.interval_secs.setLocale(self.locale)
        self.interval_ms = QSpinBox(); self.interval_ms.setRange(0, 999); self.interval_ms.setLocale(self.locale)
        for widget in [self.interval_hours, self.interval_mins, self.interval_secs, self.interval_ms]:
            widget.setFixedHeight(35)
        interval_layout.addWidget(self.interval_hours); interval_layout.addWidget(QLabel("hours"))
        interval_layout.addWidget(self.interval_mins); interval_layout.addWidget(QLabel("mins"))
        interval_layout.addWidget(self.interval_secs); interval_layout.addWidget(QLabel("secs"))
        interval_layout.addWidget(self.interval_ms); interval_layout.addWidget(QLabel("ms"))
        interval_group.setLayout(interval_layout)
        self.layout.addWidget(interval_group)

        # === Click Options ===
        options_group = QGroupBox("Click Options")
        options_layout = QVBoxLayout()
        self.mouse_button = QComboBox(); self.mouse_button.addItems(["Left", "Right", "Middle"])
        self.click_type = QComboBox(); self.click_type.addItems(["Single", "Double"])

        # ComboBox style
        combo_style = """
        QComboBox {
            padding: 5px;
            font-size: 14px;
        }
        """
        for combo in [self.mouse_button, self.click_type]:
            combo.setFixedHeight(40)
            combo.setStyleSheet(combo_style)

        options_layout.addWidget(QLabel("Mouse Button:")); options_layout.addWidget(self.mouse_button)
        options_layout.addWidget(QLabel("Click Type:")); options_layout.addWidget(self.click_type)
        options_group.setLayout(options_layout)

        # === Click Repeat ===
        repeat_group = QGroupBox("Click Repeat")
        repeat_layout = QVBoxLayout()
        self.repeat_times_radio = QRadioButton("Repeat N times")
        self.repeat_until_radio = QRadioButton("Repeat until stopped")
        self.repeat_until_radio.setChecked(True)
        self.repeat_times = QSpinBox(); self.repeat_times.setRange(1, 1000000); self.repeat_times.setLocale(self.locale)
        self.repeat_times.setFixedHeight(35)
        repeat_layout.addWidget(self.repeat_times_radio)
        repeat_times_row = QHBoxLayout()
        repeat_times_row.addWidget(QLabel("Times:"))
        repeat_times_row.addWidget(self.repeat_times)
        repeat_layout.addLayout(repeat_times_row)
        repeat_layout.addWidget(self.repeat_until_radio)
        repeat_group.setLayout(repeat_layout)

        row1 = QHBoxLayout()
        row1.addWidget(options_group)
        row1.addWidget(repeat_group)
        self.layout.addLayout(row1)

        # === Cursor Position ===
        cursor_group = QGroupBox("Cursor Position")
        cursor_layout = QHBoxLayout()
        self.current_location_radio = QRadioButton("Current Location")
        self.pick_location_radio = QRadioButton("Pick Location")
        self.current_location_radio.setChecked(True)
        self.pick_location_radio.toggled.connect(self.pick_location)  # <<<<<< ฟังก์ชัน Pick Location
        self.x_input = QLineEdit("0")
        self.y_input = QLineEdit("0")
        self.x_input.setFixedHeight(35)
        self.y_input.setFixedHeight(35)
        cursor_layout.addWidget(self.current_location_radio)
        cursor_layout.addWidget(self.pick_location_radio)
        cursor_layout.addWidget(QLabel("X:")); cursor_layout.addWidget(self.x_input)
        cursor_layout.addWidget(QLabel("Y:")); cursor_layout.addWidget(self.y_input)
        cursor_group.setLayout(cursor_layout)
        self.layout.addWidget(cursor_group)

        # === Profile (with GroupBox) ===
        profile_group = QGroupBox("Profile")
        profile_layout = QVBoxLayout()
        self.profile_combo = QComboBox(); self.profile_combo.addItems(["Profile 1", "Profile 2", "Profile 3"])
        self.profile_combo.setFixedHeight(40)
        self.profile_combo.setStyleSheet(combo_style)
        profile_layout.addWidget(self.profile_combo)
        self.save_profile_btn = QPushButton("Save Profile"); self.save_profile_btn.clicked.connect(self.save_profile)
        self.load_profile_btn = QPushButton("Load Profile"); self.load_profile_btn.clicked.connect(self.load_profile)
        self.save_profile_btn.setFixedHeight(40)
        self.load_profile_btn.setFixedHeight(40)
        profile_btns = QHBoxLayout()
        profile_btns.addWidget(self.save_profile_btn)
        profile_btns.addWidget(self.load_profile_btn)
        profile_layout.addLayout(profile_btns)
        profile_group.setLayout(profile_layout)
        self.layout.addWidget(profile_group)

        # === Action Buttons ===
        self.start_btn = QPushButton(f"Start ({self.hotkey})"); self.start_btn.clicked.connect(self.start_clicking)
        self.stop_btn = QPushButton(f"Stop ({self.hotkey})"); self.stop_btn.clicked.connect(self.stop_clicking)
        self.start_btn.setFixedHeight(40)
        self.stop_btn.setFixedHeight(40)
        action_btns = QHBoxLayout()
        action_btns.addWidget(self.start_btn); action_btns.addWidget(self.stop_btn)
        self.layout.addLayout(action_btns)

        # === Hotkey + Reset ===
        self.hotkey_btn = QPushButton("Hotkey Setting"); self.hotkey_btn.clicked.connect(self.set_hotkey)
        self.reset_btn = QPushButton("Reset"); self.reset_btn.clicked.connect(self.reset_settings)
        self.hotkey_btn.setFixedHeight(40)
        self.reset_btn.setFixedHeight(40)
        hotkey_btns = QHBoxLayout()
        hotkey_btns.addWidget(self.hotkey_btn); hotkey_btns.addWidget(self.reset_btn)
        self.layout.addLayout(hotkey_btns)

        self.setLayout(self.layout)

        # Register Hotkey
        keyboard.add_hotkey(self.hotkey, self.toggle_clicking)

    def pick_location(self):
        if self.pick_location_radio.isChecked():
            self.hide()
            print("Please click anywhere on screen to pick location...")

            def on_click(x, y, button, pressed):
                if pressed:
                    self.x_input.setText(str(x))
                    self.y_input.setText(str(y))
                    print(f"Picked position: X={x}, Y={y}")
                    self.show()
                    listener.stop()

            listener = mouse.Listener(on_click=on_click)
            listener.start()

    def get_interval(self):
        return (
            self.interval_hours.value() * 3600 +
            self.interval_mins.value() * 60 +
            self.interval_secs.value() +
            self.interval_ms.value() / 1000.0
        )

    def start_clicking(self):
        if self.is_running: return
        self.is_running = True

        interval = self.get_interval()
        mouse_button = self.mouse_button.currentText().lower()
        click_type = self.click_type.currentText().lower()
        repeat_times = self.repeat_times.value() if self.repeat_times_radio.isChecked() else None

        if self.pick_location_radio.isChecked():
            x, y = int(self.x_input.text()), int(self.y_input.text())
        else:
            x = y = None

        def click_loop():
            count = 0
            while self.is_running:
                if x is not None and y is not None:
                    pyautogui.moveTo(x, y)
                if click_type == "double":
                    pyautogui.doubleClick(button=mouse_button)
                else:
                    pyautogui.click(button=mouse_button)

                count += 1
                if repeat_times and count >= repeat_times:
                    break
                time.sleep(interval)
            print("Clicking stopped.")

        threading.Thread(target=click_loop).start()

    def stop_clicking(self):
        self.is_running = False

    def toggle_clicking(self):
        if self.is_running: self.stop_clicking()
        else: self.start_clicking()

    def set_hotkey(self):
        new_hotkey, ok = QInputDialog.getText(self, "Set Hotkey", "Enter new hotkey (ex: F6):")
        if ok:
            keyboard.remove_hotkey(self.hotkey)
            self.hotkey = new_hotkey
            keyboard.add_hotkey(self.hotkey, self.toggle_clicking)
            self.start_btn.setText(f"Start ({self.hotkey})")
            self.stop_btn.setText(f"Stop ({self.hotkey})")

    def save_profile(self):
        profile_index = self.profile_combo.currentIndex()
        data = {
            "interval": {
                "hours": self.interval_hours.value(),
                "minutes": self.interval_mins.value(),
                "seconds": self.interval_secs.value(),
                "milliseconds": self.interval_ms.value()
            },
            "mouse_button": self.mouse_button.currentText(),
            "click_type": self.click_type.currentText(),
            "repeat_mode": "times" if self.repeat_times_radio.isChecked() else "until_stopped",
            "repeat_times": self.repeat_times.value(),
            "cursor_mode": "pick" if self.pick_location_radio.isChecked() else "current",
            "position": {"x": int(self.x_input.text()), "y": int(self.y_input.text())},
            "hotkey": self.hotkey
        }
        profiles = self.load_profiles()
        profiles[f"profile_{profile_index}"] = data
        with open(PROFILES_FILE, "w") as f:
            json.dump(profiles, f)
        print(f"Profile {profile_index+1} saved.")

    def load_profile(self):
        profile_index = self.profile_combo.currentIndex()
        profiles = self.load_profiles()
        key = f"profile_{profile_index}"
        if key in profiles:
            p = profiles[key]
            self.interval_hours.setValue(p["interval"]["hours"])
            self.interval_mins.setValue(p["interval"]["minutes"])
            self.interval_secs.setValue(p["interval"]["seconds"])
            self.interval_ms.setValue(p["interval"]["milliseconds"])
            self.mouse_button.setCurrentText(p["mouse_button"])
            self.click_type.setCurrentText(p["click_type"])
            if p["repeat_mode"] == "times":
                self.repeat_times_radio.setChecked(True)
            else:
                self.repeat_until_radio.setChecked(True)
            self.repeat_times.setValue(p["repeat_times"])
            if p["cursor_mode"] == "pick":
                self.pick_location_radio.setChecked(True)
            else:
                self.current_location_radio.setChecked(True)
            self.x_input.setText(str(p["position"]["x"]))
            self.y_input.setText(str(p["position"]["y"]))
            self.set_hotkey_value(p["hotkey"])
            print(f"Profile {profile_index+1} loaded.")

    def load_profiles(self):
        try:
            with open(PROFILES_FILE, "r") as f:
                return json.load(f)
        except:
            return {}

    def set_hotkey_value(self, new_hotkey):
        keyboard.remove_hotkey(self.hotkey)
        self.hotkey = new_hotkey
        keyboard.add_hotkey(self.hotkey, self.toggle_clicking)
        self.start_btn.setText(f"Start ({self.hotkey})")
        self.stop_btn.setText(f"Stop ({self.hotkey})")

    def reset_settings(self):
        self.interval_hours.setValue(0)
        self.interval_mins.setValue(0)
        self.interval_secs.setValue(0)
        self.interval_ms.setValue(0)
        self.mouse_button.setCurrentIndex(0)
        self.click_type.setCurrentIndex(0)
        self.repeat_times.setValue(1)
        self.repeat_until_radio.setChecked(True)
        self.current_location_radio.setChecked(True)
        self.x_input.setText("0")
        self.y_input.setText("0")
        print("Settings reset.")

    def closeEvent(self, event):
        self.is_running = False
        keyboard.unhook_all_hotkeys()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AutoClicker()
    window.show()
    sys.exit(app.exec_())
