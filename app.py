#!/usr/bin/env python
import eventlet
eventlet.monkey_patch()

import multiprocessing
import os
import shutil
import threading

from eventlet import tpool

from flask import Flask, render_template
from flask_socketio import SocketIO, emit, disconnect

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)


def copy_large_file():
    source = "/home/christophe/Desktop/largefile"
    destination = "/home/christophe/Desktop/largefile2"
    try:
        os.remove(destination)
    except:
        pass
    print("Before copy")
    socketio.emit('my_response',
                  {'data': 'Thread says: before'}, namespace='/test')
    shutil.copy(source, destination)
    print("After copy")
    socketio.emit('my_response',
                  {'data': 'Thread says: after'}, namespace='/test')


@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('copy_file', namespace='/test')
def copy_file():
    """ Select one of the below options """
    option = "multiprocessing"  # native, threading, multiprocessing

    if option == "native":
        socketio.start_background_task(target=copy_large_file)

    if option == "multiprocessing":
        thread = multiprocessing.Process(target=copy_large_file)
        thread.start()

    if option == "threading":
        thread = threading.Thread(target=copy_large_file)
        thread.start()

    if option == "eventlet":
        tpool.execute(copy_large_file)

    emit('my_response', {'data': 'Copy request received'})


@socketio.on('ping', namespace='/test')
def ping():
    print("Ping received")
    emit('my_response', {'data': 'Pong'})


@socketio.on('disconnect_request', namespace='/test')
def disconnect_request():
    emit('my_response', {'data': 'Disconnected!'})
    disconnect()


@socketio.on('connect', namespace='/test')
def connect():
    emit('my_response', {'data': 'Connected'})


@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected')


if __name__ == '__main__':
    socketio.run(app, debug=True)
