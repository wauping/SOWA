from PyQt5.QtWidgets import QMainWindow, QMessageBox
from PyQt5.uic import loadUi
from settings_window import SettingsWindow


class LoginWindow(QMainWindow):
    def __init__(self):
        super(LoginWindow, self).__init__()
        loadUi('UI/login_window.ui', self)

        self.register_button.clicked.connect(self.direct_to_register_page)
        self.login_button.clicked.connect(self.open_settings_window)

        self.show()
    
    def direct_to_register_page(self):
        print('Direct to register page')

    def open_settings_window(self):
        self.settings_window = SettingsWindow()
        self.settings_window.display_info()
        self.close()

