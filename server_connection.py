import socket
from PyQt5.QtCore import QThread, pyqtSignal

SERVER_IP = '172.20.10.2'
SERVER_PORT = 8000
BUFFER_SIZE = 9999

class ServerConnection(QThread):
    connected = pyqtSignal()
    connection_failed = pyqtSignal(str)

    def __init__(self, parent=None):
        super(ServerConnection, self).__init__(parent)
        self.client_socket = None

    def run(self):
        try:
            print("Connecting to server...")
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((SERVER_IP, SERVER_PORT))
            print("Connected to server")
            self.connected.emit()
        except Exception as e:
            print(f"Failed to connect to the server: {e}")
            self.connection_failed.emit(str(e))
