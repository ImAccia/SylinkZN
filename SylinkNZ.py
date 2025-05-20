from threading import Thread
from NodeZero.srv.NodeZeroServer import NodeZeroServer
from NodeZero.srv.NodeZeroClient import NodeZeroClient
import curses

class SylinkNZ:
    def __init__(self):
        self.server = NodeZeroServer()
        server_thread = Thread(target=self.server.start, daemon=True)
        server_thread.start()

        import time
        time.sleep(1)

        self.client = NodeZeroClient()
        self.selected = 0
        self.scanning_thread = None

    def start_scan(self):
        if not self.scanning_thread or not self.scanning_thread.is_alive():
            self.client.running = True
            self.client.nodes = []  # reset list
            self.scanning_thread = Thread(target=self.client.scan_ips, daemon=True)
            self.scanning_thread.start()

    def scan_menu(self, stdscr):
        self.start_scan()
        while True:
            stdscr.clear()
            stdscr.addstr(0, 0, "Scanning... (Premi ↑↓ per muoverti, Invio per inviare, 'b' per tornare)")
            for i, ip in enumerate(self.client.nodes):
                # se i+2 è maggiore delle dimensioni della consolle, fermiamo il client
                if i + 2 > curses.LINES - 1:
                    if self.client.running:
                        self.client.stop()
                    break

                if i == self.selected:
                    stdscr.addstr(i + 2, 0, ip, curses.A_REVERSE)
                else:
                    stdscr.addstr(i + 2, 0, ip)
            stdscr.refresh()

            key = stdscr.getch()
            if key == ord('b'):
                self.client.stop()
                break
            elif key == curses.KEY_UP and self.selected > 0:
                self.selected -= 1
            elif key == curses.KEY_DOWN and self.selected < len(self.client.nodes) - 1:
                self.selected += 1
            elif key == ord('\n') or key == 10:
                selected_ip = self.client.nodes[self.selected]
                self.client.stop()
                stdscr.refresh()
                self.client.direct_message(selected_ip)
                break

    def direct_message(self, stdscr):
        curses.echo()
        stdscr.clear()
        stdscr.addstr(0, 0, "Inserisci IP destinatario: ")
        stdscr.refresh()
        ip = stdscr.getstr(1, 0, 20).decode()
        curses.noecho()
        selected_ip = ip
        stdscr.refresh()
        self.client.direct_message(selected_ip)

    def mainPage(self):
        def main(stdscr):
            curses.curs_set(0)
            options = ["Start scan", "Direct message"]
            selected_option = 0

            while True:
                stdscr.clear()
                stdscr.addstr(0, 0, "SylinkNZ - NodeZero Client")
                stdscr.addstr(1, 0, "Your IP: " + self.client.ip)
                for idx, option in enumerate(options):
                    if idx == selected_option:
                        stdscr.addstr(3 + idx, 0, option, curses.A_REVERSE)
                    else:
                        stdscr.addstr(3 + idx, 0, option)

                stdscr.addstr(6, 0, "Premi ↑↓ per muoverti, Invio per selezionare, 'q' per uscire")
                stdscr.refresh()

                key = stdscr.getch()
                if key == ord('q'):
                    self.client.stop()
                    break
                elif key == curses.KEY_UP and selected_option > 0:
                    selected_option -= 1
                elif key == curses.KEY_DOWN and selected_option < len(options) - 1:
                    selected_option += 1
                elif key == ord('\n') or key == 10:
                    if selected_option == 0:
                        self.scan_menu(stdscr)
                    elif selected_option == 1:
                        self.direct_message(stdscr)

        curses.wrapper(main)

if __name__ == "__main__":
    SNZ = SylinkNZ()
    SNZ.mainPage()
