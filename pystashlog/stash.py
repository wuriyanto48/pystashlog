from pystashlog.connection import (
    Connection,
    SecureConnection,
    INVALID_MESSAGE_TYPE_ERROR,
)

from pystashlog.exceptions import (
    StashError, 
    ConnectionError, 
    TimeoutError,
)

class Stash(object):
    def __init__(self, host='localhost', port=5000, socket_type=0,
        socket_timeout=None, socket_connect_timeout=None,
        socket_keepalive_options=None, retry_on_timeout=False,
        socket_keepalive=False, ssl=False, ssl_keyfile=None, 
        ssl_certfile=None, ssl_cert_reqs='required', ssl_ca_certs=None,
        ssl_check_hostname=False,
        health_check_interval=0):

        self.ssl = ssl

        self.kwargs = {
            'host': host,
            'port': port,
            'socket_connect_timeout': socket_connect_timeout,
            'socket_keepalive': socket_keepalive,
            'socket_keepalive_options': socket_keepalive_options,
            'socket_timeout': socket_timeout,
            'retry_on_timeout': retry_on_timeout,
            'health_check_interval': health_check_interval
        }

        if ssl:
            self.kwargs.update({
                'ssl_keyfile': ssl_keyfile,
                'ssl_certfile': ssl_certfile,
                'ssl_cert_reqs': ssl_cert_reqs,
                'ssl_ca_certs': ssl_ca_certs,
                'ssl_check_hostname': ssl_check_hostname,
            })
        self.connection = None
        self._create_connection()
    
    def _create_connection(self):
        if self.ssl:
            self.connection = SecureConnection(**self.kwargs)
        else:
            self.connection = Connection(**self.kwargs)
        self.connection.connect()
    
    def write(self, message):
        if isinstance(message, str):
            self.connection.write_str(message)
        elif isinstance(message, bytes):
            self.connection.write_bytes(message)
        else:
            raise StashError(INVALID_MESSAGE_TYPE_ERROR)
    
    def release(self):
        if self.connection is None:
            return
        try:
            self.connection.close()
        except OSError as e:
            pass
        self.connection = None