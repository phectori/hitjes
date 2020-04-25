from collections import deque
from collections import defaultdict
import googleapiclient.discovery
import random
import os
import logging
import redis

from Error import YoutubeIdMalformedError


class Player:
    def __init__(self, _config, _broadcast_state, _broadcast_message):
        self.r = redis.Redis(
            host=_config["redis"].get("host", "localhost"),
            port=int(_config["redis"].get("Port", 6379)),
            db=0,
        )

        # Register callbacks
        self.cb_broadcast_state = _broadcast_state
        self.cb_broadcast_message = _broadcast_message

        self.queue = deque([])
        self.history = deque([])

        self.titles = defaultdict(lambda: "")
        self.googleapikey = str(_config["googleapi"].get("DeveloperKey", ""))

        self.r.set('current_video_id', "")
        self.r.set('current_video_title', "")

    def get_current(self) -> str:
        return str(self.r.get('current_video_id'))


    def update_timestamp(self, _timestamp_s, yt_id):
        """ Always take the highest timestamp of all the clients """
        if self.r.get('current_video_id') != yt_id:
            return

        # if self.timestamp_s > _timestamp_s:
        #     self.timestamp_s = _timestamp_s

    def next(self, current_id: str):
        # Only allow next when playing the current id.
        if self.r.get('current_video_id') != current_id:
            logging.info("next: player video id does not match server video id")
            return

        # Add to history when not empty
        if self.r.get('current_video_id') != "":
            self.history.appendleft(self.r.get('current_video_id'))

        if len(self.queue) is not 0:
            self.r.set('current_video_id', self.queue.popleft())
        else:
            logging.info("Queue empty")
            if len(self.history) > 0:
                self.r.set('current_video_id', random.choice(list(self.history)))
                self.cb_broadcast_message(
                    "Queue empty, selecting a random video from history."
                )
            else:
                self.r.set('current_video_id', "")

        self.cb_broadcast_state()

    def append(self, yt_id: str):
        if len(yt_id) != 11:
            raise YoutubeIdMalformedError(yt_id, "Received ID has the wrong length")

        logging.info("append: " + yt_id)
        try:
            self.get_video_title(yt_id)
        except:
            logging.error("Failed to get video title")

        self.queue.append({"id": yt_id, "title": self.titles[yt_id]})

        if self.r.get('current_video_id') == "":
            # When tot playing anything
            self.next("")
        else:
            self.cb_broadcast_state()

    def get_queue(self) -> []:
        logging.info("get_queue")
        return list(self.queue)

    def get_history(self) -> []:
        logging.info("get_history")
        return list(self.history)

    def get_video_title(self, yt_id: str):
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

        request = youtube.videos().list(part="snippet", id=yt_id)
        response = request.execute()
        self.titles[yt_id] = response["items"][0]["snippet"]["title"]
