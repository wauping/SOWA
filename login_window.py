from PyQt5.QtWidgets import QMainWindow, QMessageBox
from PyQt5.QtCore import QUrl
from PyQt5.uic import loadUi
from PyQt5.QtGui import QDesktopServices
from settings_window import SettingsWindow
import requests,os
import smtplib
from dotenv import load_dotenv


sesh = {}


load_dotenv('.env.prod')


smtpObj = smtplib.SMTP('smtp.gmail.com', 587)
smtpObj.ehlo()
smtpObj.starttls()
smtpObj.ehlo()
smtpObj.login('sowa.notifi@gmail.com', os.getenv('EMAIL_PASSWORD'))


class LoginWindow(QMainWindow):
    def __init__(self):
        super(LoginWindow, self).__init__()
        loadUi('UI/login_window.ui', self)

        self.register_button.clicked.connect(self.direct_to_register_page)
        self.login_button.clicked.connect(self.check_user)

        self.show()
    
    def direct_to_register_page(self):
        registration_url = QUrl('http://localhost:1337/register')
        QDesktopServices.openUrl(registration_url)

    def check_user(self):
        username = self.username_input.text()
        password = self.password_input.text()
        print(username, password)
        
        try:
            url = 'http://localhost:1337/users'
            response = requests.get(url)
            if response.ok:
                users = response.json()
                for user in users:
                    if user['username'] == username and user['password'] == password:
                        sesh['username'] = username
                        sesh['user_id'] = user['id']
                        sesh['user_email'] = user['email']
                        print(username, password)
                        self.settings_window = SettingsWindow()
                        self.settings_window.display_info()
                        self.close()
                        return
                QMessageBox.warning(self, 'Ошибка', 'Неверное имя пользователя или пароль')
                return False
            else:
                QMessageBox.warning(self, 'Ошибка', 'Не удалось получить данные с сервера')
                return False
        except Exception as e:
            print(e)
            QMessageBox.warning(self, 'Ошибка', 'Не удалось обратиться к серверу')
            return False

