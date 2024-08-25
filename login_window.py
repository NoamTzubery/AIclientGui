import re
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from server_connection import BUFFER_SIZE, ServerConnection
from room_window import RoomWindow

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        print("Initializing Login UI...")
        self.initUI()
        self.server_thread = ServerConnection()
        self.server_thread.connected.connect(self.on_connected)
        self.server_thread.connection_failed.connect(self.on_connection_failed)
        self.server_thread.start()

    def initUI(self):
        self.setWindowTitle("Login")
        self.setGeometry(100, 100, 500, 300)  # Adjust window size
        layout = QVBoxLayout()

        self.username_label = QLabel("Username:")
        layout.addWidget(self.username_label)
        self.username_entry = QLineEdit()
        layout.addWidget(self.username_entry)

        self.password_label = QLabel("Password:")
        layout.addWidget(self.password_label)

        # Initialize password_entry before setting EchoMode
        self.password_entry = QLineEdit()
        self.password_entry.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_entry)

        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.on_login)
        layout.addWidget(self.login_button)

        self.signup_button = QPushButton("Sign up")
        self.signup_button.clicked.connect(self.on_signup)
        layout.addWidget(self.signup_button)

        # Apply dark and futuristic style with larger font sizes
        self.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                color: #dcdcdc;
                font-size: 20px;  # Increase font size
                font-family: 'Consolas', monospace;
            }
            QLineEdit {
                background-color: #3c3f41;
                color: #ffffff;
                font-size: 18px;
                padding: 10px;
                border: 1px solid #555555;
                border-radius: 5px;
            }
            QPushButton {
                background-color: #4e91fc;
                color: white;
                font-size: 18px;
                padding: 10px;
                border-radius: 5px;
                border: 1px solid #4e91fc;
            }
            QPushButton:hover {
                background-color: #3c7fd9;
            }
            QLabel {
                font-size: 18px;
            }
        """)

        self.setLayout(layout)
        print("Login UI Initialized")


    def on_connected(self):
        self.add_message("Connected to server")

    def on_connection_failed(self, error_message):
        self.add_message(f"Failed to connect to the server: {error_message}")

    def add_message(self, message):
        print(message)  # Display message in the console for debugging
    
    def validate_credentials(self, username, password):
        if len(username) <= 4:
            self.show_error_message("Error", "Username must be longer than 4 characters.")
            return False
        if len(password) <= 6:
            self.show_error_message("Error", "Password must be longer than 6 characters.")
            return False
        if not re.search(r'[A-Z]', password):
            self.show_error_message("Error", "Password must contain at least one uppercase letter.")
            return False
        if not re.search(r'[0-9]', password):
            self.show_error_message("Error", "Password must contain at least one number.")
            return False
        return True

    def show_error_message(self, title, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.exec_()

    def on_login(self):
        username = self.username_entry.text().strip()
        password = self.password_entry.text().strip()
        if username == "1" and password == "1":
            print("Bypassing server login for username and password '1'")
            self.open_room_window()  # Directly open the room window
        elif username and password:
            self.send_credentials("login", username, password)

    def on_signup(self):
        username = self.username_entry.text().strip()
        password = self.password_entry.text().strip()
        if not self.validate_credentials(username, password):
            return  # If validation fails, the error message will already be shown

        if username and password:
            self.send_credentials("signup", username, password)

    def send_credentials(self, action, username, password):
            try:
                credentials = f"{action}:{username}:{password}"
                self.server_thread.client_socket.sendall(credentials.encode())
                response = self.server_thread.client_socket.recv(1).decode()
                if response == '1':
                    self.open_room_window()
                elif response == '0':
                    self.add_message("Login failed. Please try again.")
                    self.show_error_message("Login ERROR","password or username is not correct")
                elif response == '2':
                    self.add_message("Sign up failed. Please try again.")
                    self.show_error_message("Sign Up ERROR", "this username is already exists")
                else:
                    self.add_message("Unexpected response from the server.")
            except Exception as e:
                self.add_message(f"An error occurred: {e}")

    def open_room_window(self):
        self.hide()
        self.room_window = RoomWindow(self.server_thread.client_socket, self)
        self.room_window.show()
