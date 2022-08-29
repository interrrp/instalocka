#! /usr/bin/python3

import os
import sys
import time

from PyQt6.QtCore import QObject, QRunnable, QThreadPool, pyqtSlot, pyqtSignal
from PyQt6.QtGui import QCloseEvent
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QComboBox, QCheckBox

import instalocka


class InstalockSignals(QObject):
    locked = pyqtSignal()


class InstalockWorker(QRunnable):
    """The worker for the instalocking thread."""

    def __init__(self, agent: str) -> None:
        super().__init__()

        self.agent = agent
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

        self.setup_ui()
        self.setup_instalock_pool_and_worker()

    def setup_ui(self) -> None:
        """Set up our UI."""

        # Set up the agent select combo box based on the available avatars
        self.agent_select_combo_box = QComboBox()
        self.agent_select_combo_box.currentTextChanged.connect(self.on_agent_select_combo_box_changed)
        for file in os.listdir("assets/avatars"):
            if file.endswith(".png"):
                self.agent_select_combo_box.addItem(file.replace(".png", "").title())

        # This toggle checkbox toggles the instalock or something
        self.toggle_checkbox = QCheckBox("Instalocking")
        self.toggle_checkbox.stateChanged.connect(self.on_toggle_checkbox_toggle)

        # Setup our VBoxLayout, we will add our widgets here
        layout = QVBoxLayout()
        layout.addWidget(self.agent_select_combo_box)
        layout.addWidget(self.toggle_checkbox)

        # Create a plain widget with our layout
        widget = QWidget()
        widget.setLayout(layout)

        self.setCentralWidget(widget)

    def setup_instalock_pool_and_worker(self) -> None:
        """Set up the instalock thread pool and worker."""

        self.thread_pool = QThreadPool()
        self.instalock_worker = InstalockWorker(self.agent_select_combo_box.currentText())
        self.instalock_worker.signals.locked.connect(self.on_lock)
        self.thread_pool.start(self.instalock_worker)

    def on_toggle_checkbox_toggle(self) -> None:
        """Called when the toggle check box is... toggled."""
        self.instalock_worker.enabled = self.toggle_checkbox.isChecked()

    def on_agent_select_combo_box_changed(self) -> None:
        """Called when the agent select combo box changed."""

        if not hasattr(self, "instalock_worker"):
            return

        self.instalock_worker.agent = self.agent_select_combo_box.currentText()

    def on_lock(self) -> None:
        """Called when we lock in!"""
        self.toggle_checkbox.setChecked(False)

    def closeEvent(self, event: QCloseEvent) -> None:
        """Called when we're about to exit."""

        self.instalock_worker.stop()
        super().closeEvent(event)


app = QApplication(sys.argv[1:])

window = MainWindow()
window.show()

app.exec()
