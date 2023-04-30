from flask import Flask
import zmq

app = Flask(__name__)

context = zmq.Context()
subscriber = context.socket(zmq.SUB)
subscriber.connect("tcp://localhost:5555")
subscriber.setsockopt(zmq.SUBSCRIBE, b"")

@app.route('/position', methods=["GET"])
def position():
    message = subscriber.recv_string()
    print("Received message: ", message)
    return str(message)

if __name__ == '__main__':
    app.run(host='0.0.0.0') 
