import argparse

import socket

import threading

import protocol

from chat import Chat

from debug import client_debug, server_debug, debug


# This, obviously, will be parameterized later on
HOST = '127.0.0.1'


# Handles connections from outside peers/server
class RequestHandler:
    def __init__(self):
        self.handlers = {
            protocol.PING:       self.ping,
            protocol.CHAT_BEGIN: self.begin_chat,
            protocol.CHAT_END:   self.end_chat,
        }


    def handle_connection(self, conn: socket):
        operation = conn.recv(1024).decode(protocol.ENCODING)

        if operation not in self.handlers:
            debug('[ERROR] Operation not found')
            return

        self.handlers[operation](conn)


    def ping(self, conn: socket):
        server_debug('Got PING request')


    def begin_chat(self, conn: socket):
        chat = Chat()

        chat.begin_chat(conn)


    def end_chat(self, conn: socket):
        ...


class PeerConnection:
    def __init__(self, conn: socket):
        self.conn = conn

        self.handler = RequestHandler()


    # handle incomming requests (acts as a server)
    def handle_connection(self):
        self.handler.handle_connection(self.conn)


    # send information (act as a client)
    def chat(self):
        self.conn.send(protocol.CHAT_BEGIN.encode(protocol.ENCODING))

        chat = Chat()
        chat.begin_chat(self.conn)

        client_debug(f'Exited chat')


    def send(self, data: bytes):
        self.conn.sendall(data)


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
                server_debug('Waiting for connections...')

                conn, client_addr = self.server_sock.accept()

                server_debug(f'Got connection from: {client_addr}')

                peer_conn = PeerConnection(conn)

                peer_conn.handle_connection()

            except KeyboardInterrupt:
                self.shutdown = True

        self.server_sock.close()


    def setup_server_socket(self, port: int, backlog: int = 5):
        self.server_sock = socket.socket(socket.AF_INET, type=socket.SOCK_STREAM)
        self.server_sock.bind((HOST, port))
        self.server_sock.listen(backlog)

        server_debug(f'Listening at port: {port}...')


    def connect(self, port: int) -> PeerConnection:
        address = (HOST, port)

        client_debug(f'Trying to connect to: {address}...')

        try:
            conn = socket.create_connection(address)
        except ConnectionRefusedError:
            print('Deu ruim menó')

        client_debug(f'Successfully connected to: {address}')

        return PeerConnection(conn)


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
       peer_connection = peer.connect(args.connect_to)
       peer_connection.chat()

    if not args.listen:
        peer.end()
