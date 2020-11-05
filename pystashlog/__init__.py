from pystashlog.exceptions import (
    StashError, 
    ConnectionError, 
    TimeoutError,
)

from pystashlog.stash import (
    Stash,
)

__version__ = '1.0.0'
VERSION = tuple([int(v) for v in __version__.split('.')])