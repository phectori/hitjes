from collections import deque
from collections import defaultdict
import googleapiclient.discovery
import random
import os
import logging
import threading
from Error import YoutubeIdMalformedError


class Player:
    def __init__(self, _broadcast_state, _broadcast_message):
        self.queue = deque([])
        self.history = deque([])
        self.cb_broadcast_state = _broadcast_state
        self.cb_broadcast_message = _broadcast_message
        self.titles = defaultdict(lambda: '')

        # Semaphore for next function
        self.sem = threading.Semaphore()

        self.current = dict()
        self.current["id"] = ""
        self.current["title"] = ""
        self.timestamp_s = 0

    def get_current(self) -> str:
        return self.current["id"]

    def get_current_title(self) -> str:
        return self.current["title"]

    def get_timestamp(self):
        return self.timestamp_s

    def update_timestamp(self, _timestamp_s, yt_id):
        """ Always take the highest timestamp of all the clients """
        if self.current["id"] != yt_id:
            return

        if self.timestamp_s > _timestamp_s:
            self.timestamp_s = _timestamp_s

    def next(self, current_id: str):
        self.sem.acquire()

        # Only allow next when playing the current id.
        if self.current["id"] != current_id:
            logging.info("next: player video id does not match server video id")
            return

        # Add to history when not empty
        if self.current["id"] != "":
            self.history.appendleft(self.current)

        if len(self.queue) is not 0:
            self.current = self.queue.popleft()
        else:
            logging.info("Queue empty")
            if len(self.history) > 0:
                self.current = random.choice(list(self.history))
                self.cb_broadcast_message(
                    "Queue empty, selecting a random video from history."
                )
            else:
                self.current["id"] = ""

        self.sem.release()

        self.cb_broadcast_state()

    def append(self, yt_id: str):
        if len(yt_id) != 11:
            raise YoutubeIdMalformedError(yt_id, "Received ID has the wrong length")

        logging.info("append: " + yt_id)
        title = ""
        try:
            title = self.get_video_title(yt_id)
            logging.info("Got title: '{}'".format(title))
        except:
            logging.error('Failed to get video title')

        self.queue.append({"id": yt_id, "title": title})

        self.cb_broadcast_message("Added: {}".format(title))

        if self.current["id"] == "":
            # When tot playing anything
            self.next("")
        else:
            self.cb_broadcast_state()

    def get_queue(self) -> []:
        return list(self.queue)

    def get_history(self) -> []:
        return list(self.history)

    def get_video_title(self, yt_id: str) -> str:
        logging.info("get_video_title")
        if yt_id in self.titles:
            return self.titles[yt_id]

        if len(yt_id) != 11:
            raise YoutubeIdMalformedError(yt_id, "Received ID has the wrong length")

        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

        api_service_name = "youtube"
        api_version = "v3"

        youtube = googleapiclient.discovery.build(
            api_service_name,
            api_version,
            developerKey=self.googleapikey,
            cache_discovery=False,
        )

        request = youtube.videos().list(
            part="snippet", id=yt_id
        )
        response = request.execute()
        title = response["items"][0]["snippet"]["title"]

        if len(title) > 0:
            self.titles[yt_id] = title

        return title
