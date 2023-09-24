class HTTPError501(Exception):
    """
    Custom exception for HTTP status code 501 (Not Implemented).
    This exception is raised when the requested functionality is
    not implemented or recognized on the server.
    """

    def __init__(self):
        super().__init__("Not Implemented")


class HTTPError502(Exception):
    """
    Custom exception for HTTP status code 502 (Bad Gateway).
    This exception is raised when a gateway server received
    an invalid response from the upstream server.
    """

    def __init__(self):
        super().__init__("Bad Gateway")


class HTTPError503(Exception):
    """
    Custom exception for HTTP status code 503 (Service Unavailable).
    This exception is raised when the Server is currently unable to
    handle the request.
    """

    def __init__(self):
        super().__init__("Service Unavailable")


class HTTPError418(Exception):
    """
    Custom exception for HTTP status code 418 (I'm a teapot).
    This exception is raised when the Server is currently unable to
    brew coffee.
    """

    def __init__(self):
        super().__init__("I'm a teapot")
