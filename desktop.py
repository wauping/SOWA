from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
import sys
import login_window


app = QApplication(sys.argv)
app_icon = QIcon("UI/ICON_32.png")


mainwindow = login_window.LoginWindow()
mainwindow.setWindowIcon(app_icon)


try:
    sys.exit(app.exec_())
except:
    login_window.smtpObj.quit()
    print("Exiting...")
