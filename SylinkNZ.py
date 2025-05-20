from threading import Thread
from NodeZero.srv.NodeZeroServer import NodeZeroServer
from NodeZero.srv.NodeZeroClient import NodeZeroClient

class SylinkNZ:
    def __init__(self):
        # Avvio server in un thread separato
        self.server = NodeZeroServer()
        server_thread = Thread(target=self.server.start, daemon=True)
        server_thread.start()

        import time
        time.sleep(1)

        # Avvio il client in un thread separato
        self.client = NodeZeroClient()
        client_thread = Thread(target=self.client.scan_ips, daemon=True)
        client_thread.start()

    def mainPage(self):
        # Mostro un menù, percorribile con tastiera (freccia su/giù, invio)
        # Mostro gli ip trovati, quando premo invio posso inviare un messaggio a quel ip
        import curses
        
        def main(stdscr):
            curses.curs_set(0)
            stdscr.nodelay(False)
            stdscr.clear()
            
            while True:
                stdscr.clear()
                stdscr.addstr(0, 0, "SylinkNZ - NodeZero Client")
                stdscr.addstr(1, 0, "IP trovati:")
                
                for i, ip in enumerate(self.client.nodes):
                    if i == self.selected:
                        stdscr.addstr(i + 2, 0, ip, curses.A_REVERSE)
                    else:
                        stdscr.addstr(i + 2, 0, ip)

                stdscr.addstr(len(self.client.nodes) + 3, 0, "Premi ↑↓ per muoverti, Invio per inviare, 'q' per uscire")
                stdscr.refresh()

                key = stdscr.getch()

                if key == ord('q'):
                    break
                elif key == curses.KEY_UP and self.selected > 0:
                    self.selected -= 1
                elif key == curses.KEY_DOWN and self.selected < len(self.client.nodes) - 1:
                    self.selected += 1
                elif key == ord('\n') or key == 10:
                    selected_ip = self.client.nodes[self.selected]
                    self.client.stop()
                    stdscr.addstr(len(self.client.nodes) + 5, 0, f"Scansione interrotta. Puoi inviare un messaggio a {selected_ip}")
                    stdscr.refresh()
                    curses.napms(1000)


        self.selected = 0
        curses.wrapper(main)




if __name__ == "__main__":
    SNZ = SylinkNZ()
    SNZ.mainPage()
