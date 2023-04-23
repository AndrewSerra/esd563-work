import socketio
import zmq

connected_clients = []

@socketio.event
def connect(sid):
    print(f"New connection {sid}")
    connected_clients.append(sid)
    return

@socketio.event
def disconnect(sid):
    print(f"Disconnection {sid}")
    target_id = connected_clients.index(sid)
    connected_clients.pop(target_id)
    return

if __name__ == "__main__":
    sio = socketio.Server()
    app = socketio.WSGIApp(sio)

    zmq_context = zmq.Context()
    socket = zmq_context.socket(zmq.SUB)
    socket.bind("tcp://*:5555")

    while True:
        message = socket.recv()
        print("Received request: %s" % message)
        socket.send(message)
