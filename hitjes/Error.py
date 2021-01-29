class Error(Exception):
    """Base class for exceptions in this module."""

    pass


class YoutubeIdMalformedError(Error):
    """Exception raised for errors in the input.

    Attributes:
        yt_id -- the malformed id
        message -- explanation of the error
    """

    def __init__(self, yt_id: str, message: str):
        self.yt_id = yt_id
        self.message = message


class NextRequestIgnoredError(Error):
    """"""

    def __init__(self, message: str):
        self.message = message
