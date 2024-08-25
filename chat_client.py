import re
import socket
import threading
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel, QScrollArea, QListWidget, QListWidgetItem, QSpacerItem, QSizePolicy
from PyQt5.QtCore import Qt


def clean_message(response):
    response = re.sub(r'^\[\{"generated_text":\s*"', '', response)
    response = re.sub(r'"\}\]$', '', response)
    response = response.replace('\\n', '\n')
    return response

class ChatClient(QWidget):
    def __init__(self, client_socket, login_window):
        super().__init__()
        print("Initializing UI...")
        self.client_socket = client_socket
        self.login_window = login_window
        self.initUI()
        self.start_receiving()  # Start the thread to receive messages

    def initUI(self):
        self.setWindowTitle("Chat Client")
        self.setGeometry(100, 100, 1000, 600)  # Increased width for the side menu

        # Main layout
        main_layout = QHBoxLayout(self)

        # Side menu
        self.side_menu = QListWidget()
        self.side_menu.setFixedWidth(200)  # Set width of the side menu
        self.side_menu.addItem(QListWidgetItem("Return to Login"))
        self.side_menu.addItem(QListWidgetItem("New Group Chat"))
        self.side_menu.itemClicked.connect(self.on_menu_item_clicked)
        main_layout.addWidget(self.side_menu)

        # Chat area
        chat_area = QVBoxLayout()

        # Scroll area to hold the chat history
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("background-color: #f5f5f5; border: none;")

        # Chat container inside the scroll area
        self.chat_container = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.setAlignment(Qt.AlignTop)
        self.scroll_area.setWidget(self.chat_container)

        chat_area.addWidget(self.scroll_area)

        # Input layout
        input_layout = QHBoxLayout()
        self.prompt_entry = QLineEdit()
        self.prompt_entry.setPlaceholderText("Type a message...")
        self.prompt_entry.setStyleSheet("""
            background-color: #ffffff; 
            color: #000000; 
            font-size: 18px; 
            padding: 10px; 
            border-radius: 20px; 
            border: 1px solid #cccccc;
        """)
        input_layout.addWidget(self.prompt_entry)

        self.send_button = QPushButton("Send")
        self.send_button.setStyleSheet("""
            background-color: #007bff; 
            color: white; 
            font-size: 18px; 
            padding: 10px 20px; 
            border-radius: 20px;
        """)
        input_layout.addWidget(self.send_button)

        chat_area.addLayout(input_layout)

        main_layout.addLayout(chat_area)

        self.setLayout(main_layout)
        self.send_button.clicked.connect(self.on_send)
        self.prompt_entry.returnPressed.connect(self.on_send)
        print("UI Initialized")

    def add_message(self, text, sender):
        # Create a container for the message
        message_container = QWidget()
        message_layout = QHBoxLayout()

        text_label = QLabel(text)
        text_label.setWordWrap(True)  # Enable word wrap

        if sender == "user":
            # User's message: right-aligned with blue background
            text_label.setStyleSheet("""
                background-color: #007bff; 
                color: white; 
                padding: 15px; 
                border-radius: 15px; 
                margin: 5px;
                font-size: 20px;
            """)
            message_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
            message_layout.addWidget(text_label)
        else:
            # ChatGPT's message: left-aligned with white background
            text_label.setStyleSheet("""
                background-color: #e0e0e0; 
                color: black; 
                padding: 15px; 
                border-radius: 15px; 
                margin: 5px;
                font-size: 20px;
            """)
            message_layout.addWidget(text_label)
            message_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        message_container.setLayout(message_layout)
        self.chat_layout.addWidget(message_container)
        self.chat_layout.addStretch()

        # Auto-scroll to the bottom of the chat
        self.scroll_area.verticalScrollBar().setValue(self.scroll_area.verticalScrollBar().maximum())

    def send_prompt(self, prompt):
        try:
            self.client_socket.sendall(prompt.encode())
        except Exception as e:
            self.add_message(f"An error occurred: {e}", "system")

    def receive_messages(self):
        while True:
            try:
                response = self.client_socket.recv(9999).decode()
                if response:
                    response = clean_message(response)
                    self.add_message(response, "bot")
                else:
                    break  # Connection closed
            except Exception as e:
                self.add_message(f"An error occurred: {e}", "system")
                break

    def start_receiving(self):
        self.receive_thread = threading.Thread(target=self.receive_messages, daemon=True)
        self.receive_thread.start()

    def on_send(self):
        prompt = self.prompt_entry.text().replace('\\n', '\n')
        if prompt.strip():
            self.add_message(prompt, "user")
            if prompt.lower() == "exit":
                self.client_socket.close()
                self.close()
                return
            self.send_prompt(prompt)
            self.prompt_entry.clear()

    def on_menu_item_clicked(self, item):
        if item.text() == "Return to Login":
            message = "$home$"
            self.client_socket.sendall(message.encode())
            self.login_window.show()  
            self.close()  
