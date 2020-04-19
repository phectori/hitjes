from collections import deque
import googleapiclient.discovery
import random
import os
import json


class Player:

    def __init__(self, _broadcast_state, _broadcast_message):
        self.queue = deque([])
        self.history = []
        self.cb_broadcast_state = _broadcast_state
        self.cb_broadcast_message = _broadcast_message
        self.titles = dict()

        self.current = dict()
        self.current['id'] = ''
        self.timestamp_s = 0

    def get_current(self) -> str:
        return self.current['id']

    def get_timestamp(self):
        return self.timestamp_s

    def update_timestamp(self, _timestamp_s, yt_id):
        """ Always take the highest timestamp of all the clients """
        if self.current['id'] != yt_id:
            return

        if self.timestamp_s > _timestamp_s:
            self.timestamp_s = _timestamp_s

    def next(self, current_id: str):
        # Only allow next when playing the current id.
        if self.current['id'] != current_id:
            print("next: player video id does not match server video id")
            return

        # Add to history when not empty
        if self.current['id'] != '':
            self.history.append(self.current)

        if len(self.queue) is not 0:
            self.current = self.queue.popleft()
        else:
            print("Queue empty")
            if len(self.history) > 0:
                self.current = random.choice(self.history)
            self.cb_broadcast_message("Queue empty, selecting randomly from history.")

        self.cb_broadcast_state()

    def append(self, yt_id: str):
        if len(yt_id) != 11:
            raise YoutubeIdMalformed(yt_id, "Received ID has the wrong length")

        print("append: " + yt_id)
        self.get_video_title(yt_id)

        self.queue.append({"id": yt_id, "title": self.titles[yt_id]})

        if self.current['id'] == '':
            # When tot playing anything
            self.next('')
        else:
            self.cb_broadcast_state()

    def get_queue(self) -> []:
        return list(self.queue)

    def get_history(self) -> []:
        return self.history

    def get_video_title(self, yt_id: str):
        if yt_id in self.titles:
            return self.titles[yt_id]

        if len(yt_id) != 11:
            raise YoutubeIdMalformed(yt_id, "Received ID has the wrong length")

        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

        api_service_name = "youtube"
        api_version = "v3"
        DEVELOPER_KEY = "AIzaSyCxmSPZ8Bp8v0FeEKES7PP62MSLig2YsLs"

        youtube = googleapiclient.discovery.build(
            api_service_name, api_version, developerKey=DEVELOPER_KEY)

        request = youtube.videos().list(
            part="snippet,contentDetails,statistics",
            id=yt_id
        )
        response = request.execute()

        print(response)
        self.titles[yt_id] = response['items'][0]["snippet"]["title"]


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
