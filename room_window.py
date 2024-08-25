from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from chat_client import ChatClient

class RoomWindow(QWidget):
    def __init__(self, client_socket, login_window):
        super().__init__()
        self.client_socket = client_socket
        self.login_window = login_window
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Enter Room")
        self.setGeometry(100, 100, 500, 300)  # Adjust window size
        layout = QVBoxLayout()

        self.room_label = QLabel("Enter Chat Room Code:")
        layout.addWidget(self.room_label)
        self.room_entry = QLineEdit()
        layout.addWidget(self.room_entry)

        self.create_room_button = QPushButton("Create Room")
        self.create_room_button.clicked.connect(self.on_create_room)
        layout.addWidget(self.create_room_button)

        self.join_room_button = QPushButton("Join Room")
        self.join_room_button.clicked.connect(self.on_join_room)
        layout.addWidget(self.join_room_button)

        self.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                color: #dcdcdc;
                font-size: 20px;
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

    def on_create_room(self):
        room_code = self.room_entry.text().strip()
        if room_code:
            self.send_room_request("create", room_code)

    def on_join_room(self):
        room_code = self.room_entry.text().strip()
        if room_code:
            self.send_room_request("join", room_code)

    def send_room_request(self, action, room_code):
        try:
            request = f"{action}:{room_code}"
            self.client_socket.sendall(request.encode())
            response = self.client_socket.recv(1).decode()
            if response == '1':  # Successfully joined/created room
                self.open_chat_window()
            elif response == '0':  # Room already exists or does not exist
                self.show_error_message("Room Error", "Unable to join/create the room. Please try again.")
            else:
                self.show_error_message("Unexpected Error", "Unexpected response from the server.")
        except Exception as e:
            self.show_error_message("Connection Error", f"An error occurred: {e}")

    def show_error_message(self, title, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.exec_()

    def open_chat_window(self):
        self.hide()
        self.chat_client = ChatClient(self.client_socket, self)
        self.chat_client.show()
