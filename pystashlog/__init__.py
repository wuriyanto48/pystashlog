from pystashlog.exceptions import (
    StashError, 
    ConnectionError, 
    TimeoutError,
)

from pystashlog.stash import (
    Stash,
)

__version__ = '1.0.0'
VERSION = tuple(map(lambda v: int(v), __version__.split('.')))