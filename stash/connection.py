import socket
import os

from stash.exceptions import (
    StashError, ConnectionError, TimeoutError
)

M_CRLF = b'\r\n'
M_EMPTY = b''

SERVER_TIMEOUT_ERROR = 'timeout connecting to server'
INVALID_MESSAGE_TYPE_ERROR = 'invalid message'

class Connection:
    def __init__(self, host='localhost', port=5000, socket_type=0,
        socket_timeout=None, socket_connect_timeout=None,
        socket_keepalive_options=None,
        socket_keepalive=False, socket_read_size=65536, 
        health_check_interval=0):

        self.pid = os.getpid()

        self.host = host
        self.port = int(port)
        self.socket_type = socket_type
        self.socket_timeout = socket_timeout
        self.socket_connect_timeout = socket_connect_timeout or socket_timeout
        self.socket_keepalive_options = socket_keepalive_options or {}
        self.socket_keepalive = socket_keepalive
        self.socket_read_size = socket_read_size
        self.health_check_interval = health_check_interval
        self._connect_callbacks = []
        self._sock = None

    def register_connect_callback(self, callback):
        self._connect_callbacks.append(callback)

    def clear_connect_callbacks(self):
        self._connect_callbacks = []
    
    def connect(self):
        if self._sock:
            return
        try:
            sock = self._connect()
        except socket.timeout:
            raise TimeoutError(SERVER_TIMEOUT_ERROR)
        except socket.error as e:
            raise ConnectionError(self._error(e))

        self._sock = sock
    def _error(self, exception):
        if len(exception.args) == 1:
            return "Error connecting to {0}:{1}. {2}.".format(self.host, self.port, exception.args[0])
        else:
            return "Error {0} connecting to {1}:{2}. {3}.".format(exception.args[0], self.host, self.port, exception.args[1])
    
    def _connect(self):
        err = None
        for addr_info in socket.getaddrinfo(self.host, self.port, self.socket_type, socket.SOCK_STREAM):
            family, socktype, proto, canonname, socket_address = addr_info
            sock = None
            try:
                sock = socket.socket(family, socktype, proto)
                # TCP_NODELAY
                sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

                # TCP_KEEPALIVE
                if self.socket_keepalive:
                    sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
                    for k, v in self.socket_keepalive_options.items():
                        sock.setsockopt(socket.IPPROTO_TCP, k, v)
                
                # set the socket_connect_timeout before we connect
                sock.settimeout(self.socket_connect_timeout)

                # connect
                sock.connect(socket_address)

                # set the socket_timeout now that we're connected
                sock.settimeout(self.socket_timeout)
                return sock

            except OSError as _:
                err = _
                if sock is not None:
                    sock.close()
        if err is not None:
            raise err
        raise OSError("socket.getaddrinfo returned an empty list")
    
    def close(self):
        if self._sock is None:
            return
        try:
            if os.getpid() == self.pid:
                self._sock.shutdown(socket.SHUT_RDWR)
            self._sock.close()
        except OSError:
            pass
        self._sock = None

        for callback in self._connect_callbacks:
            callback(self)

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass

    def send(self, message):
        if not self._sock:
            self.connect()
        if not isinstance(message, str):
            raise StashError(INVALID_MESSAGE_TYPE_ERROR)
        msg_byte = M_EMPTY.join((message.encode('utf-8'), M_CRLF))
        try:
            self._sock.sendall(msg_byte)
        except socket.timeout:
            self.close()
            raise TimeoutError(SERVER_TIMEOUT_ERROR)
        except socket.error as e:
            self.close()
            raise ConnectionError(self._error(e))

    def read(self):
        pass
