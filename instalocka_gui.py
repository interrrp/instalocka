#! /usr/bin/python3

import os
import sys
import time

from PyQt6.QtCore import QObject, QRunnable, QThreadPool, pyqtSlot, pyqtSignal
from PyQt6.QtGui import QCloseEvent, QIcon
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QComboBox,
    QCheckBox,
    QMessageBox,
)
import qt_material

import utils
import instalocka


class InstalockSignals(QObject):
    locked = pyqtSignal()


class InstalockWorker(QRunnable):
    """The worker for the instalocking thread."""

    def __init__(self) -> None:
        super().__init__()

        self.agent = ""
        self.enabled = False
        self.signals = InstalockSignals()

        self._stopped = False

    @pyqtSlot()
    def run(self) -> None:
        while True:
            # Delay so our CPU doesn't cry uwu
            time.sleep(0.01)

            if self._stopped:
                return

            if not self.enabled:
                continue

            try:
                instalocka.click_agent(self.agent.lower())
                instalocka.lock_in()
            except instalocka.ImageNotFoundException:
                pass
            else:
                self.signals.locked.emit()

    def stop(self) -> None:
        self._stopped = True


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Instalocka GUI")

        self.setup_instalock_pool_and_worker()
        self.setup_ui()

    def setup_ui(self) -> None:
        """Set up our UI."""

        # Set up the agent select combo box based on the available avatars
        self.agent_select_combo_box = QComboBox()
        self.agent_select_combo_box.currentTextChanged.connect(self.on_agent_select_combo_box_changed)
        for file in os.listdir(f"assets/avatars/{utils.get_screen_size_str()}"):
            if file.endswith(".png"):
                self.agent_select_combo_box.addItem(
                    QIcon(f"assets/avatars/{utils.get_screen_size_str()}/{file}"), file.replace(".png", "").title()
                )

        # This toggle checkbox toggles the instalock or something
        self.toggle_checkbox = QCheckBox("Instalocking")
        self.toggle_checkbox.setChecked(True)
        self.toggle_checkbox.stateChanged.connect(self.on_toggle_checkbox_toggle)
        self.instalock_worker.enabled = self.toggle_checkbox.isChecked()

        # Toggle whether to turn off instalocking when we lock
        self.turn_off_when_locked_checkbox = QCheckBox("Turn off when locked")

        # The options are in an HBoxLayout, just looks neat
        options_layout = QHBoxLayout()
        options_layout.addWidget(self.toggle_checkbox)
        options_layout.addWidget(self.turn_off_when_locked_checkbox)
        options_widget = QWidget()
        options_widget.setLayout(options_layout)

        # Setup our main VBoxLayout, we will add all our widgets here
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.agent_select_combo_box)
        main_layout.addWidget(options_widget)
        main_widget = QWidget()
        main_widget.setLayout(main_layout)

        self.setCentralWidget(main_widget)

    def setup_instalock_pool_and_worker(self) -> None:
        """Set up the instalock thread pool and worker."""

        self.thread_pool = QThreadPool()
        self.instalock_worker = InstalockWorker()
        self.instalock_worker.signals.locked.connect(self.on_lock)
        self.thread_pool.start(self.instalock_worker)

    def on_toggle_checkbox_toggle(self) -> None:
        """Called when the toggle check box is... toggled."""
        self.instalock_worker.enabled = self.toggle_checkbox.isChecked()

    def on_agent_select_combo_box_changed(self) -> None:
        """Called when the agent select combo box changed."""
        self.instalock_worker.agent = self.agent_select_combo_box.currentText()

    def on_lock(self) -> None:
        """Called when we lock in!"""

        if self.turn_off_when_locked_checkbox.isChecked():
            self.toggle_checkbox.setChecked(False)

    def closeEvent(self, event: QCloseEvent) -> None:
        """Called when we're about to exit."""

        self.instalock_worker.stop()
        super().closeEvent(event)


app = QApplication(sys.argv[1:])
qt_material.apply_stylesheet(app, theme="dark_teal.xml")

if not os.path.exists(f"assets/avatars/{utils.get_screen_size_str()}"):
    error_box = QMessageBox()
    error_box.setIcon(QMessageBox.Icon.Critical)
    error_box.setWindowTitle("Resolution not supported")
    error_box.setText(f"Your monitor resolution ({utils.get_screen_size_str()}) is currently not supported.")
    error_box.exec()
    sys.exit(1)

window = MainWindow()
window.show()

app.exec()
