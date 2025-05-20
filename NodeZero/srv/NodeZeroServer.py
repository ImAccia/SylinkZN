import socket
from NodeZero.srv.ChatHandler import ChatHandler
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
                    if data == b'NZ-HANDSHAKE-REQ':
                        conn.sendall(b'NZ-HANDSHAKE-OK')
                    elif data == b'NZ-DIRECT-MESSAGE':
                        conn.sendall(b'NZ-DIRECT-MESSAGE-OK')
                        msg = conn.recv(1024)
                        print(f"Received msg request from {addr}: {msg.decode()}")

                        # avvio la sessione di chat
                        ch = ChatHandler(conn)
                        ch.chat_session()

