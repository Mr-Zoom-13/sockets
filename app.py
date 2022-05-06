from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, emit, Namespace, join_room, rooms
from threading import Lock

async_mode = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()


@app.route('/')
def index():
    return render_template('index.html', async_mode=socketio.async_mode)


def background_thread():
    """Example of how to send server generated events to clients."""
    count = 0
    while True:
        socketio.sleep(10)
        count += 1
        socketio.emit('my_response',
                      {'data': 'Server generated event', 'count': count},
                      namespace='/test')


class MyNamespace(Namespace):
    def on_my_event(self, message):
        session['receive_count'] = session.get('receive_count', 0) + 1
        emit('my_response',
             {'data': message['data'], 'count': session['receive_count']}, room='1')

    def on_connect(self):
        global thread
        print('mymymy')
        join_room('1')
        print(', '.join(rooms()))
        with thread_lock:
            if thread is None:
                thread = socketio.start_background_task(background_thread)
        emit('my_response', {'data': 'Connected', 'count': 0})

    def on_disconnect(self):
        print('mimimi')
        print('Client disconnected', request.sid)


socketio.on_namespace(MyNamespace('/'))
if __name__ == '__main__':
    socketio.run(app, debug=True)
