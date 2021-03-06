from collections import deque
from collections import defaultdict
from tinydb import TinyDB
import googleapiclient.discovery
import random
import os
import logging
import threading
import time
from Error import YoutubeIdMalformedError, NextRequestIgnoredError


class Player:
    def __init__(self, _config, _broadcast_state, _broadcast_message):
        self.queue = deque([])
        self.cb_broadcast_state = _broadcast_state
        self.cb_broadcast_message = _broadcast_message
        self.titles = defaultdict(lambda: "")

        # db
        self.db = TinyDB("db.json")
        self.history = self.db.table("history")

        self.google_api_key = str(_config["googleapi"].get("DeveloperKey", ""))

        # Semaphore for next function
        self.sem_next = threading.Semaphore()
        self.sem_update_timestamp = threading.Semaphore()

        self.current = dict()
        self.current["id"] = ""
        self.current["title"] = ""

        # Timestamp
        self.timestamp_s = 0.0

        # Last skip timestamp
        self.last_skip_timestamp = -1

    def get_current(self) -> str:
        return self.current["id"]

    def get_current_title(self) -> str:
        return self.current["title"]

    def get_timestamp(self) -> float:
        return self.timestamp_s

    def update_timestamp(self, yt_id: str, _timestamp_s: float):
        self.sem_update_timestamp.acquire()

        """ Always take the highest timestamp of all the clients """
        if self.get_current() == yt_id:
            if _timestamp_s > self.timestamp_s:
                self.timestamp_s = _timestamp_s

        self.sem_update_timestamp.release()

    def next(self, current_id: str, is_skip: bool):

        if (self.last_skip_timestamp + 5) > time.time():
            logging.info("next: ignore in window")
            raise NextRequestIgnoredError(
                "Next request ignored, back off window active."
            )

        self.last_skip_timestamp = time.time()

        self.sem_next.acquire()

        # Only allow next when playing the current id.
        if self.current["id"] != current_id:
            logging.info("next: player video id does not match server video id")
            self.sem_next.release()
            raise NextRequestIgnoredError(
                "The currently playing video ID does not match the server video ID, refresh the page to fix."
            )

        # Add to history when not empty
        if self.current["id"] != "" and not (is_skip and self.timestamp_s > 30):
            try:
                self.history.insert(dict(self.current))
            except:
                print(self.current)
                logging.error("Failed to insert {} into db.".format(self.current))

        if len(self.queue) != 0:
            self.current = self.queue.popleft()
        else:
            logging.info("Queue empty")
            if len(self.history.all()) > 0:
                self.current = random.choice(list(self.history.all()))
                self.cb_broadcast_message(
                    "Queue empty, selecting a random video from history."
                )
            else:
                self.current["id"] = ""

        # Reset timestamp
        self.timestamp_s = 0.0

        self.sem_next.release()

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
            logging.error("Failed to get video title")
            return

        self.queue.append({"id": yt_id, "title": title})

        self.cb_broadcast_message("Added: {}".format(title))

        if self.current["id"] == "":
            # When tot playing anything
            self.next("", False)
        else:
            self.cb_broadcast_state()

    def get_queue(self) -> []:
        return list(self.queue)

    def get_history(self) -> []:
        h = list(self.history.all())
        h.reverse()
        return h[0:20]

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
            developerKey=self.google_api_key,
            cache_discovery=False,  # Todo: use the cache google gives you
        )

        request = youtube.videos().list(part="snippet", id=yt_id)
        response = request.execute()
        title = response["items"][0]["snippet"]["title"]

        if len(title) > 0:
            self.titles[yt_id] = title

        return title

    def get_search_results(self, search_string: str) -> []:
        logging.info("get_search_results")

        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

        api_service_name = "youtube"
        api_version = "v3"

        youtube = googleapiclient.discovery.build(
            api_service_name,
            api_version,
            developerKey=self.google_api_key,
            cache_discovery=False,  # Todo: use the cache google gives you
        )

        request = youtube.search().list(
            part="snippet",
            maxResults=10,
            q=search_string,
            type="video",
        )
        response = request.execute()

        results = []
        for item in response["items"]:
            results.append(
                {"id": item["id"]["videoId"], "title": item["snippet"]["title"]}
            )

        return results
