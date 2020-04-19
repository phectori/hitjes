from collections import deque
import googleapiclient.discovery
import random
import os
import logging
from Error import YoutubeIdMalformedError


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
            logging.info("next: player video id does not match server video id")
            return

        # Add to history when not empty
        if self.current['id'] != '':
            self.history.append(self.current)

        if len(self.queue) is not 0:
            self.current = self.queue.popleft()
        else:
            logging.info("Queue empty")
            if len(self.history) > 0:
                self.current = random.choice(self.history)
                self.cb_broadcast_message("Queue empty, selecting a random video from history.")
            else:
                self.current['id'] = ''

        self.cb_broadcast_state()

    def append(self, yt_id: str):
        if len(yt_id) != 11:
            raise YoutubeIdMalformedError(yt_id, "Received ID has the wrong length")

        logging.info("append: " + yt_id)
        self.get_video_title(yt_id)

        self.queue.append({"id": yt_id, "title": self.titles[yt_id]})

        if self.current['id'] == '':
            # When tot playing anything
            self.next('')
        else:
            self.cb_broadcast_state()

    def get_queue(self) -> []:
        logging.info("get_queue")
        return list(self.queue)

    def get_history(self) -> []:
        logging.info("get_history")
        return self.history

    def get_video_title(self, yt_id: str):
        logging.info("get_video_title")
        if yt_id in self.titles:
            return self.titles[yt_id]

        if len(yt_id) != 11:
            raise YoutubeIdMalformedError(yt_id, "Received ID has the wrong length")

        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

        api_service_name = "youtube"
        api_version = "v3"
        DEVELOPER_KEY = "AIzaSyCxmSPZ8Bp8v0FeEKES7PP62MSLig2YsLs"

        youtube = googleapiclient.discovery.build(
            api_service_name, api_version, developerKey=DEVELOPER_KEY, cache_discovery=False)

        request = youtube.videos().list(
            part="snippet,contentDetails,statistics",
            id=yt_id
        )
        response = request.execute()
        self.titles[yt_id] = response['items'][0]["snippet"]["title"]
