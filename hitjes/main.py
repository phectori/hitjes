from flask import Flask, render_template, request, send_from_directory
from flask_socketio import SocketIO, send, emit

from Player import Player

app = Flask(__name__, static_url_path='')
app.config['SECRET_KEY'] = 'keepitsave'
socketIO = SocketIO(app, cors_allowed_origins='*')


def broadcast_state():
    print("Broadcasting state")
    state = get_state()
    emit('state', state, broadcast=True, json=True)


def broadcast_message(msg: str):
    print("Broadcasting message" + msg)
    emit('message', msg, broadcast=True)


player = Player(broadcast_state,
                broadcast_message)


@app.route('/')
def send_index():
    print("Index requested")
    return send_from_directory('static', 'index.html')


@app.route('/<path:path>')
def send_static(path):
    print(path + " requested")
    return send_from_directory('static', path)


@socketIO.on('message')
def handle_message(message):
    print("Message: " + message)


@socketIO.on('addUrl')
def handle_add_url(yt_id):
    player.append(yt_id)


@socketIO.on('requestQueue')
def handle_request_queue(_):
    json = dict()
    json["queue"] = player.get_queue()
    send(json, json=True)


@socketIO.on('requestHistory')
def handle_request_history(_):
    json = dict()
    json["history"] = player.get_history()
    send(json, json=True)


@socketIO.on('requestCurrent')
def handle_request_current(_):
    json = dict()
    json["current"] = player.get_current()
    send(json, json=True)


@socketIO.on('requestState')
def handle_request_state():
    print("State requested")
    json = get_state()
    emit("state", json, json=True)


@socketIO.on('requestNext')
def handle_request_next(current_yt_id):
    print("Next requested with current id: " + str(current_yt_id))
    player.next(str(current_yt_id))


def get_state():
    state = dict()
    state["current"] = player.get_current()
    state["timestamp"] = player.get_timestamp()
    state["queue"] = player.get_queue()
    state["history"] = player.get_history()
    return state


if __name__ == '__main__':
    socketIO.run(app, host='0.0.0.0')
