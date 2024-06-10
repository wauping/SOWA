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
        self.login_window = None  # Добавляем атрибут для login_window

        self.monitoring_button.clicked.connect(self.open_detection)
        self.return_button.clicked.connect(self.go_back)

    def display_info(self):
        self.show()

    def open_detection(self):
        login_window.sesh['location'] = self.location_input.text()
        if self.detection_window.isVisible():
            print('Detection window is already open.')
        else:
            self.detection_window.create_detection_instance()
            self.detection_window.start_detection()

    def go_back(self):
        login = login_window.sesh.get('login', '')
        password = login_window.sesh.get('password', '')

        print(f"Returning to login window with credentials: {login}, {password}")

        try:
            if self.login_window is None:
                self.login_window = login_window.LoginWindow()
                self.login_window.set_credentials(login, password)
            
            self.login_window.show()
            
            if self.login_window.isVisible():
                print("Login window is visible.")
            else:
                print("Login window is not visible. Trying to show it.")
                self.login_window.show()

            self.close()
            print("Settings window closed.")
        except Exception as e:
            print(f"An error occurred while returning to login window: {e}")

    def closeEvent(self, event):
        if self.detection_window.isVisible():
            self.detection_window.detection.running = False
            self.detection_window.close()
        event.accept()
