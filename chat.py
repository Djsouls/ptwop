import socket

import threading

from protocol import ENCODING, CHAT_END

from debug import debug


class Chat:
    def __init__(self):
        self.continue_chat: bool = True


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
            # Put this text in a specific place instead of just printing
            print(f'{conn.getpeername()} says: {msg}')

            if msg == CHAT_END or '' or None:
                self.end_chat(conn)


    def end_chat(self, conn: socket):
        debug(f'Ending chat with: {conn.getpeername()}')

        self.continue_chat = False

        conn.sendall(CHAT_END.encode(ENCODING))

