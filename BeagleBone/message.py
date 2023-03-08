from email import message
import queue
import threading
from enum import IntEnum
import time

import zmq

import sensors

__author__ = "Aidan Cantu, Joshua Vondracek"

# ZMQ setup
context = zmq.Context()
send_socket = context.socket(zmq.PUSH)
send_socket.bind("tcp://192.168.7.2:5555")
receive_socket = context.socket(zmq.PULL)
receive_socket.bind("tcp://192.168.7.2:5556")

# Queue of all data that will later be sent to the host
SEND_INFO = queue.Queue()

# Queue of all responses to demands from the server
DEMAND_REPLIES = queue.Queue(1)

# Queue of all inputs called from input function
INPUT_REPLIES = queue.Queue(1)

# Queue of all commands from the host
RECEIVED_COMMANDS = queue.Queue(1)

class Status(IntEnum):
    WAITING = 1
    CMD_READY = 2
    DMR_READY = 3

# Current status of server (used by host to test 
# connection and determine when to send messages)
SERVER_STATUS = Status.WAITING

# Global entity which determines whether
# to send .csv logging data
LOGGING = threading.Event()
LOGGING.clear()

DUMMY_DATA = threading.Event()
DUMMY_DATA.clear()

PT_SIM_TYPE = {}

# Global entity which determines whether
# requests can be made by the server
USER_IO_AVAILABLE = threading.Event()
USER_IO_AVAILABLE.set()

# Global variable which will stop all running commands
STOPPED = False

def sender():
    '''Immediately sends any info in the
    SEND_INFO queue over the socket'''
    global SEND_INFO
    while(True):
        send_socket.send_string(SEND_INFO.get())

def receiver():
    '''Puts any received info from the socket
    in its respective queue'''
    global RECEIVED_COMMANDS, DEMAND_REPLIES
    while(True):
        message = receive_socket.recv()
        message = str(message, 'UTF-8')
        a = message.find('%')
        if message[:a] == "cmd":
            RECEIVED_COMMANDS.put(message[a+1:], block=False)
        elif message[:a] == "dmr":
            DEMAND_REPLIES.put(message[a+1:], block=False)
        elif message[:a] == "sta":
            set_status(SERVER_STATUS)

def tell(message = ""):
    '''Sends a string message to the host'''
    global SEND_INFO
    message = "msg%" + message
    USER_IO_AVAILABLE.wait()
    SEND_INFO.put(message)

def send_logs():
    '''thread that reads sensor data and sends it to the
    host over the socket'''
    global SEND_INFO
    global LOGGING
    while(True):
        LOGGING.wait()
        threading.Timer(0.1, send_logs).start()
        message = 'log%' + sensors.read_all()
        time.sleep(0.05)
        SEND_INFO.put(message)

def send_dummy_data():
    '''thread that sends dummy data over'''
    global SEND_INFO
    global DUMMY_DATA
    global PT_SIM_TYPE
    while(True):
        DUMMY_DATA.wait()
        threading.Timer(0.1, send_dummy_data).start()
        message = 'dummy%' + sensors.dummy_data(PT_SIM_TYPE)
        time.sleep(0.05)
        SEND_INFO.put(message)

def get_cmd():
    '''waits until user input is allowed, then sets server status
    to enable commands, then returns received command'''
    global RECEIVED_COMMANDS, USER_IO_AVAILABLE, SERVER_STATUS

    USER_IO_AVAILABLE.wait()
    set_status(Status.CMD_READY)

    a = RECEIVED_COMMANDS.get()
    set_status(Status.WAITING)

    return a
        
def demand(message):
    '''Waits until user input is allowed, then sets server status
    to enable demand replies, then returns received demand reply'''
    global USER_IO_AVAILABLE
    global SERVER_STATUS

    USER_IO_AVAILABLE.wait()

    tell(message)

    while DEMAND_REPLIES.empty() == False:
        DEMAND_REPLIES.get()

    USER_IO_AVAILABLE.clear()

    set_status(Status.DMR_READY)
    a = DEMAND_REPLIES.get()
    set_status(Status.WAITING)
    USER_IO_AVAILABLE.set()
    #tell("I made it to the return command")
    return a

def input(message):
    '''Waits until user input is allowed, then reads and returns
    the value'''
    global USER_IO_AVAILABLE
    global SERVER_STATUS
    global INPUT_REPLIES

    USER_IO_AVAILABLE.wait()

    tell(message)
    while INPUT_REPLIES.empty() == False:
        INPUT_REPLIES.get()

    USER_IO_AVAILABLE.clear()
    set_status(Status.DMR_READY)
    a = INPUT_REPLIES.get()
    set_status(Status.WAITING)
    USER_IO_AVAILABLE.set()

    #tell("I made it to the end of the command")
    return a
    


def logging(currently_logging = True):
    '''determines whether send_logs should send
    log data'''
    global LOGGING
    if currently_logging:
        LOGGING.set()
    else:
        LOGGING.clear()

def logging_dummy(currently_logging_dummy = True, dict = {}):
    '''determines whether send_dummy_data should send
    the data'''
    global DUMMY_DATA, PT_SIM_TYPE
    if currently_logging_dummy:
        DUMMY_DATA.set()
        PT_SIM_TYPE = dict
    else:
        DUMMY_DATA.clear()

def set_status(status):
    global SEND_INFO, SERVER_STATUS
    SERVER_STATUS = status
    message = "sta%" + str(int(status))
    SEND_INFO.put(message)

def cmd_ready():
    set_status(Status.CMD_READY)
    USER_IO_AVAILABLE.set()

def stop():
    global STOPPED
    STOPPED = True

def is_stopped():
    global STOPPED
    return STOPPED

def resume():
    global STOPPED
    STOPPED = False