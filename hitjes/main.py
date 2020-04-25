from flask import Flask, render_template, request, send_from_directory
from flask_socketio import SocketIO, send, emit
import logging
import configparser

from Player import Player

app = Flask(__name__, static_url_path="")
app.config["SECRET_KEY"] = "keepitsave"

# disable browser caching for now
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
socketIO = SocketIO(app, cors_allowed_origins="*")

logging.basicConfig(
    format="%(asctime)s %(levelname)s: %(message)s", level=logging.INFO
)


def broadcast_state():
    logging.info("broadcast_state")
    state = get_state()
    emit("state", state, broadcast=True, json=True)


def broadcast_message(msg: str):
    logging.info("broadcast_message: '{}'".format(msg))
    emit("message", msg, broadcast=True)


config = configparser.ConfigParser()
config.read("settings/settings.ini")

if "googleapi" not in config:
    logging.info("No googleapi section in settings.ini")

clients = set()
player = Player(config, broadcast_state, broadcast_message)


@app.route("/")
def send_index():
    logging.info("send_index")
    return send_from_directory("static", "index.html")


@app.route("/<path:path>")
def send_static(path):
    logging.info(path + " requested")
    return send_from_directory("static", path)

@socketIO.on("message")
def handle_message(message):
    logging.info("handle_message({}): {}".format(request.sid[-4:], message))


@socketIO.on("connect")
def handle_connect():
    logging.info("handle_connect({})".format(request.sid[-4:]))
    clients.add(request.sid)
    broadcast_state()


@socketIO.on("disconnect")
def handle_disconnect():
    logging.info("handle_disconnect({})".format(request.sid[-4:]))
    clients.remove(request.sid)
    broadcast_state()


@socketIO.on("addUrl")
def handle_add_url(yt_id):
    logging.info("handle_add_url({})".format(request.sid[-4:]))
    player.append(yt_id)


@socketIO.on("requestState")
def handle_request_state():
    logging.info("handle_request_state({})".format(request.sid[-4:]))
    json = get_state()
    emit("state", json, json=True)


@socketIO.on("requestNext")
def handle_request_next(current_yt_id):
    logging.info("handle_request_next({}): {}".format(request.sid[-4:], current_yt_id))
    player.next(str(current_yt_id))


@socketIO.on("requestSkip")
def handle_request_skip(current_yt_id):
    logging.info("handle_request_skip({}): {}".format(request.sid[-4:], current_yt_id))
    player.next(str(current_yt_id))


@socketIO.on("requestUpdateTimestamp")
def handle_request_update_timestamp(data):
    logging.debug("handle_request_update_timestamp({})".format(request.sid[-4:]))
    player.update_timestamp(data["id"], float(data["timestamp"]))


def get_state():
    state = dict()
    state["currentId"] = player.get_current()
    state["currentTitle"] = player.get_current_title()
    state["timestamp"] = player.get_timestamp()
    state["queue"] = player.get_queue()
    state["history"] = player.get_history()
    state["clients"] = list(clients)
    return state


if __name__ == "__main__":
    logging.info("Starting socketIO...")
    socketIO.run(app, host="0.0.0.0")
