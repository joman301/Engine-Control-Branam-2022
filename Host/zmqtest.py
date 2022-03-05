import zmq
import queue

context = zmq.Context()

#  Socket to talk to server
print("Connecting to hello world server…")
context = zmq.Context()
receive_socket = context.socket(zmq.PULL)
receive_socket.connect("tcp://192.168.7.2:5555")
send_socket = context.socket(zmq.PUSH)
send_socket.connect("tcp://192.168.7.2:5556")

# Queue of all data that will later be sent to the server
SEND_INFO = queue.Queue()

# Queue of all demands from the server
RECEIVED_LOGS = queue.Queue()
RECEIVED_MESSAGES = queue.Queue()


#  Do 10 requests, waiting each time for a response
for request in range(10):
    print("Sending request %s …" % request)
    socket.send(b"Hello")

    #  Get the reply.
    message = socket.recv()
    print("Received reply %s [ %s ]" % (request, message))