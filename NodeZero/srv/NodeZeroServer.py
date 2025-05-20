import socket

class NodeZeroServer:
    def __init__(self, port=19840):
        self.port = port

    def start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('0.0.0.0', self.port))
            s.listen()

            while True:
                conn, addr = s.accept()
                with conn:
                    data = conn.recv(1024)
                    if data:
                        conn.sendall(b'NZ-HANDSHAKE-OK')
