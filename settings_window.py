from PyQt5.QtWidgets import QMainWindow
from PyQt5.uic import loadUi
from detection_window import DetectionWindow
import login_window, detection

class SettingsWindow(QMainWindow):
    def __init__(self):
        super(SettingsWindow, self).__init__()
        loadUi('UI/settings_window.ui', self)
        detection.clear_frames_directory()
        self.detection_window = DetectionWindow()

        self.monitoring_button.clicked.connect(self.open_detection)

    def display_info(self):
        self.show()

    def open_detection(self):
        login_window.sesh['location'] = self.location_input.text()
        if self.detection_window.isVisible():
            print('Detection window is already open.')
        else:
            self.detection_window.create_detection_instance()
            self.detection_window.start_detection()

    def closeEvent(self, event):
        if self.detection_window.isVisible():
            self.detection_window.detection.running = False
            self.detection_window.close()
            event.accept()
