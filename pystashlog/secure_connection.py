
from pystashlog.exceptions import (
    StashError, 
    ConnectionError, 
    TimeoutError,
)

from pystashlog.connection import Connection
from pystashlog.logger import logger as log

# check ssl support
try:
    import ssl
    ssl_available = True
except ImportError:
    ssl_available = False

STATUS_CONNECTING_TO_SERVER_SECURE = 'connecting stash client to the logstash server with secure connection'

'''
SecureConnection class represent a secure socket client
'''
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
        log.info(STATUS_CONNECTING_TO_SERVER_SECURE)

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