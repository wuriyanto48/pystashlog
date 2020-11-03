class StashError(Exception):
    pass

class ConnectionError(StashError):
    pass

class TimeoutError(StashError):
    pass

class ResponseError(StashError):
    pass