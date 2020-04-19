from collections import deque


class Player:

    def __init__(self, _broadcast_state):
        self.queue = deque([])
        self.history = []
        self.cb_broadcast_state = _broadcast_state

        self.queue.append('C0DPdy98e4c')
        self.queue.append('C0DPdy98e4c')
        self.queue.append('C0DPdy98e4c')
        self.queue.append('GLQ0biK-ZgA')
        self.queue.append('t0bPrt69rag')
        self.current = 'C0DPdy98e4c'
        self.timestamp_s = 0

    def get_current(self) -> str:
        return self.current

    def get_timestamp(self):
        return self.timestamp_s

    def update_timestamp(self, _timestamp_s):
        """ Always take the highest timestamp of all the clients """
        if self.timestamp_s > _timestamp_s:
            self.timestamp_s = _timestamp_s

    def next(self, current_id: str):
        if len(current_id) != 11:
            raise YoutubeIdMalformed(current_id, "Received ID has the wrong length")

        if self.current != current_id:
            print("next: player video id does not match server video id")
            return

        self.history.append(self.current)
        if len(self.queue) is not 0:
            self.current = self.queue.popleft()
        else:
            print("Queue empty")
            self.current = ""

        self.cb_broadcast_state()

    def append(self, yt_id: str):
        if len(yt_id) != 11:
            raise YoutubeIdMalformed(yt_id, "Received ID has the wrong length")

        print("append: " + yt_id)
        self.queue.append(yt_id)
        self.cb_broadcast_state()

    def get_queue(self) -> []:
        return list(self.queue)

    def get_history(self) -> []:
        return self.history


class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class YoutubeIdMalformed(Error):
    """Exception raised for errors in the input.

    Attributes:
        yt_id -- the malformed id
        message -- explanation of the error
    """

    def __init__(self, yt_id: str, message: str):
        self.yt_id = yt_id
        self.message = message
