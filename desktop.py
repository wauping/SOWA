from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
import sys
from login_window import LoginWindow


app = QApplication(sys.argv)
app_icon = QIcon("UI/ICON_32.png")


mainwindow = LoginWindow()
mainwindow.setWindowIcon(app_icon)


try:
    sys.exit(app.exec_())
except:
    print("Exiting...")
