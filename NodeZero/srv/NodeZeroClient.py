import socket
import math
from NodeZero.srv.ChatHandler import ChatHandler

class NodeZeroClient:
    def __init__(self, port=19840):
        import requests
        public_ip = requests.get('https://api.ipify.org').text
        self.ip = public_ip
        self.port = port
        self.nodes = []
        self.executor = None
        self.running = False

    def scan_ips(self):
        import concurrent.futures

        ip_parts = list(map(int, self.ip.split('.')))
        ip_list = []

        # Esempio di scansione limitata (evita 256*256, usa solo 10 IP per esempio)
        for i in range(1000):
            ip = f"{ip_parts[0]}.{ip_parts[1]}.{(ip_parts[2] + (math.floor(i / 256) % 256 ) % 256)}.{(ip_parts[3] + i) % 256}"
            if ip != self.ip:
                ip_list.append(ip)

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            self.executor = executor
            futures = [executor.submit(self.scan_ip, ip) for ip in ip_list]
            for future in concurrent.futures.as_completed(futures):
                if not self.running:
                    break
                future.result()

    def scan_ip(self, ip):
        if not self.running:
            return
        try:
            with socket.create_connection((ip, self.port), timeout=1) as sock:
                sock.sendall(b'NZ-HANDSHAKE-REQ')
                response = sock.recv(1024)
                if response == b'NZ-HANDSHAKE-OK':
                    self.nodes.append(ip)
        except:
            pass

    def stop(self):
        self.running = False
        if self.executor:
            self.executor.shutdown(wait=False)
            print('[NodeZeroClient] Scansione interrotta.')

    def direct_message(self, ip):
        with socket.create_connection((ip, self.port), timeout=1) as sock:
            sock.sendall(b'NZ-DIRECT-MESSAGE')
            response = sock.recv(1024)
            if response == b'NZ-DIRECT-MESSAGE-OK':
                ch = ChatHandler(sock)
                ch.chat_session()
            else:
                print(f'[NodeZeroClient] Errore durante l\'invio del messaggio a {ip}')