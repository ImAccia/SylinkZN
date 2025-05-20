import curses
import threading
import time
import sys
import os
import signal
import select

class ChatHandler:
    def __init__(self, conn):
        self.conn = conn
        self.chat_thread = None
        self.running = True
        self.conn.setblocking(0)  # Imposta la connessione in modalità non bloccante
        self.chat_thread = threading.Thread(target=self.chat_session)
        self.chat_thread.start()
        self.chat_thread.join()
        self.conn.close()
        self.running = False

    def chat_session(self):
        conn = self.conn
        def signal_handler(sig, frame):
            curses.endwin()
            sys.exit(0)
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        def chat(stdscr):
            curses.curs_set(1)
            stdscr.clear()
            stdscr.addstr(0, 0, "Chat avviata. Premi 'q' per uscire.")
            stdscr.refresh()

            while True:
                stdscr.addstr(2, 0, "Tu: ")
                curses.echo()
                msg = stdscr.getstr(2, 4, 100).decode()
                curses.noecho()

                if msg == 'q':
                    break

                conn.sendall(msg.encode())
                stdscr.addstr(3, 0, f"Tu: {msg}")
                stdscr.refresh()
                time.sleep(0.1)
                # Ricezione del messaggio dal client
                ready = select.select([conn], [], [], 1)
                if ready[0]:
                    data = conn.recv(1024)
                    if not data:
                        break
                    stdscr.addstr(4, 0, f"Client: {data.decode()}")
                    stdscr.refresh()
                    time.sleep(0.1)
                stdscr.addstr(5, 0, "Premi 'q' per uscire.")
                stdscr.refresh()
                key = stdscr.getch()
                if key == ord('q'):
                    break
                stdscr.clear()

        # Avvia la chat in un thread separato
        chat_thread = threading.Thread(target=chat, args=(curses.initscr(),))
        chat_thread.start()
        chat_thread.join()
        conn.close()
        curses.endwin()
        print("Chat chiusa.")