from flask import Flask, render_template, request, send_from_directory
from flask_socketio import SocketIO, send, emit

app = Flask(__name__, static_url_path='')
app.config['SECRET_KEY'] = 'keepitsave'
socketIO = SocketIO(app, cors_allowed_origins='*')


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
    print(message)
    send(message)


@socketIO.on('json')
def handle_json(json):
    print(json)
    send(json, json=True)


@socketIO.on('my event')
def handle_my_custom_event(json):
    print(json)
    emit('my response', json)


if __name__ == '__main__':
    socketIO.run(app, host='0.0.0.0')
