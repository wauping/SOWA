from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
import sys
import login_window

def main():
    app = QApplication(sys.argv)
    app_icon = QIcon("UI/ICON_32.png")

    mainwindow = login_window.LoginWindow()
    mainwindow.setWindowIcon(app_icon)

    try:
        sys.exit(app.exec_())
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        login_window.smtpObj.quit()
        print("Exiting...")

if __name__ == "__main__":
    main()
