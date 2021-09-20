import argparse

import socket

import threading


HOST = '127.0.0.1'
ENCODING = 'utf-8'
CHAT_BEGIN = 'CHAT_BEGIN'
CHAT_END = 'QUIT'
SHUTDOWN_SERVER = 'SHUTDOWN'

DEBUG = True

def debug(msg):
    if DEBUG:
        print(f'<{threading.currentThread().getName()}> -- {msg}')


class Peer:
    def __init__(self, backlog: int = 5):
        self.shutdown: bool = False
        self.continue_chat: bool = True
        
        self.backlog: int = backlog


    def listen_for_connections(self, port: int):
        self.setup_server_socket(port, self.backlog)

        self.server_thread = threading.Thread(target=self._listen_for_connections)
        self.server_thread.start()


    def _listen_for_connections(self):
        while not self.shutdown:
            try:
                debug('[SERVER]: Waiting for connections...')

                conn, client_addr = self.server_sock.accept()

                debug(f'[SERVER]: Got connection from: {client_addr}')

                self.handle_connection(conn)

            except KeyboardInterrupt:
                self.shutdown = True

        self.server_sock.close()


    def setup_server_socket(self, port: int, backlog: int = 5):
        self.server_sock = socket.socket(socket.AF_INET, type=socket.SOCK_STREAM)
        self.server_sock.bind((HOST, port))
        self.server_sock.listen(backlog)

        debug(f'[SERVER]: Listening at port: {port}...')


    # Function to act as a client to another peer
    def connect_and_chat(self, port: int):
        address = (HOST, str(port))

        debug(f'[CLIENT]: Trying to connect to: {address}...')

        s = socket.create_connection(address)

        debug(f'[CLIENT]: Successfully connected to: {address}')

        s.sendall(CHAT_BEGIN.encode('utf-8'))

        self.begin_chat(s)

        debug(f'[CLIENT]: Exited chat')


    def handle_connection(self, conn: socket):
        msg = conn.recv(1024).decode('utf-8')

        if msg == CHAT_BEGIN:
            self.begin_chat(conn)
        elif msg == SHUTDOWN_SERVER:
            self.shutdown = True


    def begin_chat(self, conn: socket):
        debug(f'Beginning chat with {conn.getpeername()}')

        chat_thread = threading.Thread(target=self.recvmsg, args=[conn])
        chat_thread.start()

        while self.continue_chat:
            try:
                msg = input('::: ').encode(ENCODING)
                conn.sendall(msg)

            except KeyboardInterrupt:
                self.end_chat(conn)
                break
            # Trying to send a message to a dead node
            except ConnectionResetError:
                break

        # Enabling new chat requests
        self.continue_chat = True

        chat_thread.join()
        conn.close()


    def recvmsg(self, conn: socket):
        while self.continue_chat:
            msg = conn.recv(1024).decode(ENCODING)

            print(f'{conn.getpeername()} says: {msg}')

            if msg == CHAT_END or '' or None:
                self.end_chat(conn)


    def end_chat(self, conn: socket):
        debug(f'Ending chat with: {conn.getpeername()}')

        self.continue_chat = False

        conn.sendall(CHAT_END.encode(ENCODING))


    def end(self):
        self.shutdown = True
        try:
            self.server_thread.join()
        except:
            ...


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--listen', help='Listen for conexions from other peers', type=int)
    parser.add_argument('--connect-to', help='The port of the peer to chat with', type=int)
    args = parser.parse_args()

    peer = Peer()

    if args.listen:
        peer.listen_for_connections(args.listen)

    if args.connect_to:
        peer.connect_and_chat(args.connect_to)

    if not args.listen:
        peer.end()
