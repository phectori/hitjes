from flask import Flask, render_template, request, send_from_directory
from flask_socketio import SocketIO, send, emit
import logging

from Player import Player

app = Flask(__name__, static_url_path='')
app.config['SECRET_KEY'] = 'keepitsave'

# disable browser caching for now
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
socketIO = SocketIO(app, cors_allowed_origins='*')

logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=logging.DEBUG)

def broadcast_state():
    logging.info("broadcast_state")
    state = get_state()
    emit('state', state, broadcast=True, json=True)


def broadcast_message(msg: str):
    logging.info("broadcast_message " + msg)
    emit('message', msg, broadcast=True)


player = Player(broadcast_state,
                broadcast_message)


@app.route('/')
def send_index():
    logging.info("send_index")
    return send_from_directory('static', 'index.html')


@app.route('/<path:path>')
def send_static(path):
    logging.info(path + " requested")
    return send_from_directory('static', path)


@socketIO.on('message')
def handle_message(message):
    logging.info("Received client message: " + message)


@socketIO.on('addUrl')
def handle_add_url(yt_id):
    logging.info("handle_add_url")
    player.append(yt_id)


@socketIO.on('requestState')
def handle_request_state():
    logging.info("handle_request_state")
    json = get_state()
    emit("state", json, json=True)


@socketIO.on('requestNext')
def handle_request_next(current_yt_id):
    logging.info("Next requested while currently playing: " + str(current_yt_id))
    player.next(str(current_yt_id))


def get_state():
    state = dict()
    state["current"] = player.get_current()
    state["timestamp"] = player.get_timestamp()
    state["queue"] = player.get_queue()
    state["history"] = player.get_history()
    return state


if __name__ == '__main__':
    logging.info("Starting socketIO...")
    socketIO.run(app, host='0.0.0.0')
