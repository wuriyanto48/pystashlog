import socket
import os

# check ssl support
try:
    import ssl
    ssl_available = True
except ImportError:
    ssl_available = False

print('ssl available ', ssl_available)

from pystashlog.exceptions import (
    StashError, 
    ConnectionError, 
    TimeoutError,
)

# protocol
M_CRLF = b'\r\n'
M_EMPTY = b''

SERVER_TIMEOUT_ERROR = 'error: timeout connecting to server'
SERVER_CLOSED_CONNECTION_ERROR = 'error: server closed its connection'
INVALID_MESSAGE_TYPE_ERROR = 'error: invalid message'
TIMOUT_WRITING_TO_SOCKET_ERROR = 'error: timeout while writing to socket'
TIMOUT_READING_FROM_SOCKET_ERROR = 'error: timeout while reading from socket'
SSL_NOT_AVAILABLE_ERROR = 'error: ssl not available'

class Connection:
    def __init__(self, host='localhost', port=5000, socket_type=0,
        socket_timeout=None, socket_connect_timeout=None,
        socket_keepalive_options=None, retry_on_timeout=False,
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

        # function signature : def my_func(self, connection)
        self._connect_callbacks = []
        self._sock = None

    def info(self):
        infos = [
            ('host', self.host),
            ('port', self.port)
        ]

        return infos

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

        for callback in self._connect_callbacks:
            # self parameter, refer to Connection
            callback(self)

    def _error(self, exception):
        if len(exception.args) == 1:
            return 'error connecting to {0}:{1}. {2}.'.format(self.host, self.port, exception.args[0])
        else:
            return 'error {0} connecting to {1}:{2}. {3}.'.format(exception.args[0], self.host, self.port, exception.args[1])
    
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
        raise OSError('socket.getaddrinfo returned an empty list')
    
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

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass
    
    def write_str(self, message):
        if not self._sock:
            self.connect()
        if not isinstance(message, str):
            raise StashError(INVALID_MESSAGE_TYPE_ERROR)
        msg_byte = M_EMPTY.join((message.encode('utf-8'), M_CRLF))
        try:
            self.write_bytes(msg_byte)
        except TimeoutError as e:
            self.close()
            raise e
        except ConnectionError as e:
            self.close()
            raise e

    def write_bytes(self, message):
        if not self._sock:
            self.connect()
        if not isinstance(message, bytes):
            raise StashError(INVALID_MESSAGE_TYPE_ERROR)

        msg_byte = message
        if not msg_byte.endswith(M_CRLF):
            msg_byte = M_EMPTY.join((message, M_CRLF))
        try:
            self._sock.sendall(msg_byte)
        except socket.timeout:
            self.close()
            raise TimeoutError(TIMOUT_WRITING_TO_SOCKET_ERROR)
        except socket.error as e:
            self.close()
            raise ConnectionError('error while writing to socket %s'%(e))

    def read(self):
        try:
            response = self._sock.recv(self.socket_read_size)
        except socket.timeout:
            self.close()
            raise TimeoutError(TIMOUT_READING_FROM_SOCKET_ERROR)
        except socket.error as e:
            self.close()
            raise ConnectionError('error while reading from socket %s'%(e))
        return response

class SecureConnection(Connection):

    def __init__(self, ssl_keyfile=None, ssl_certfile=None,
                 ssl_cert_reqs='required', ssl_ca_certs=None,
                 ssl_check_hostname=False, **kwargs):
        if not ssl_available:
            raise StashError(SSL_NOT_AVAILABLE_ERROR)

        # call parent connection constructor
        super().__init__(**kwargs)

        self.keyfile = ssl_keyfile
        self.certfile = ssl_certfile
        if ssl_cert_reqs is None:
            ssl_cert_reqs = ssl.CERT_NONE
        elif isinstance(ssl_cert_reqs, str):
            CERT_REQS = {
                'none': ssl.CERT_NONE,
                'optional': ssl.CERT_OPTIONAL,
                'required': ssl.CERT_REQUIRED
            }
            if ssl_cert_reqs not in CERT_REQS:
                raise StashError(
                    "Invalid SSL Certificate Requirements Flag: %s" %
                    ssl_cert_reqs)
            ssl_cert_reqs = CERT_REQS[ssl_cert_reqs]
        self.cert_reqs = ssl_cert_reqs
        self.ca_certs = ssl_ca_certs
        self.check_hostname = ssl_check_hostname
    
    def _connect(self):
        "Wrap the socket with SSL support"
        sock = super()._connect()
        context = ssl.create_default_context()
        context.check_hostname = self.check_hostname
        context.verify_mode = self.cert_reqs
        if self.certfile and self.keyfile:
            context.load_cert_chain(certfile=self.certfile,
                                    keyfile=self.keyfile)
        if self.ca_certs:
            context.load_verify_locations(self.ca_certs)
        return context.wrap_socket(sock, server_hostname=self.host)