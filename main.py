import sys
from PyQt5.QtWidgets import QApplication
from login_window import LoginWindow

if __name__ == '__main__':
    print("Running application...")
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())
