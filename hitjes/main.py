from flask import Flask, render_template, request, send_from_directory
from flask_socketio import SocketIO, send, emit, Namespace, join_room, leave_room
import logging
import configparser
import git

from Room import Room

app = Flask(__name__, static_url_path="")
app.config["SECRET_KEY"] = "keepitsave"

# disable browser caching for now
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
socketIO = SocketIO(app, cors_allowed_origins="*")

logging.basicConfig(format="%(asctime)s %(levelname)s: %(message)s", level=logging.INFO)


config = configparser.ConfigParser()
config.read("settings/settings.ini")

repo = git.Repo(search_parent_directories=True)
version = repo.git.describe("--always")

if "googleapi" not in config:
    logging.info("No googleapi section in settings.ini")


@app.route("/")
def send_index():
    logging.info("send_index")
    return send_from_directory("static", "index.html")


@app.route("/<path:path>")
def send_static(path):
    logging.info(path + " requested")
    return send_from_directory("static", path)


socketIO.on_namespace(Room("/", config, version))


if __name__ == "__main__":
    logging.info("Starting socketIO...")
    socketIO.run(app, host="0.0.0.0")
