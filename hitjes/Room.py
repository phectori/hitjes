from flask import Flask, render_template, request, send_from_directory
from flask_socketio import SocketIO, send, emit, Namespace, join_room, leave_room
from Error import NextRequestIgnoredError
from Player import Player

import logging


class Room(Namespace):
    def __init__(self, name, config, version):
        super().__init__(name)
        self.player = Player(config, self.broadcast_state, self.broadcast_message)
        self.clients = set()
        self.version = version

    def broadcast_state(self):
        logging.info("broadcast_state")
        state = self.get_state()
        emit("state", state, broadcast=True, json=True)

    def broadcast_message(self, msg: str):
        logging.info("broadcast_message: '{}'".format(msg))
        emit("message", msg, broadcast=True)

    def on_connect(self):
        logging.info("on_connect({})".format(request.sid[-4:]))
        self.clients.add(request.sid)
        self.broadcast_state()

    def on_disconnect(self):
        logging.info("on_disconnect({})".format(request.sid[-4:]))
        self.clients.remove(request.sid)
        self.broadcast_state()

    def on_message(self, message):
        logging.info("on_message({}): {}".format(request.sid[-4:], message))

    def on_add_url(self, yt_id):
        logging.info("on_add_url({})".format(request.sid[-4:]))
        self.player.append(yt_id)

    def on_search(self, yt_id):
        logging.info("on_search({})".format(request.sid[-4:]))
        results = self.player.get_search_results(yt_id)
        emit("search_results", results, json=True)

    def on_request_state(self):
        logging.info("on_request_state({})".format(request.sid[-4:]))
        json = self.get_state()
        emit("state", json, json=True)

    def on_request_next(self, current_yt_id):
        try:
            logging.info(
                "on_request_next({}): {}".format(request.sid[-4:], current_yt_id)
            )
            self.player.next(str(current_yt_id), False)
        except NextRequestIgnoredError as err:
            pass

    def on_request_skip(self, current_yt_id):
        try:
            logging.info(
                "on_request_skip({}): {}".format(request.sid[-4:], current_yt_id)
            )
            self.player.next(str(current_yt_id), True)
        except NextRequestIgnoredError as err:
            self.broadcast_message(err.message)

    def on_request_update_timestamp(self, data):
        logging.debug("on_request_update_timestamp({})".format(request.sid[-4:]))
        if "timestamp" in data and "id" in data:
            self.player.update_timestamp(data["id"], float(data["timestamp"]))

    def get_state(self):
        state = dict()
        state["version"] = self.version
        state["currentId"] = self.player.get_current()
        state["currentTitle"] = self.player.get_current_title()
        state["timestamp"] = self.player.get_timestamp()
        state["queue"] = self.player.get_queue()
        state["history"] = self.player.get_history()
        state["clients"] = list(self.clients)
        return state
