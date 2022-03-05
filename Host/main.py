from datetime import datetime
import queue
import threading
from enum import IntEnum

import zmq
import pandas as pd

__author__ = "Aidan Cantu"

# ZMQ setup
context = zmq.Context()
receive_socket = context.socket(zmq.PULL)
receive_socket.connect("tcp://192.168.7.2:5555")
send_socket = context.socket(zmq.PUSH)
send_socket.connect("tcp://192.168.7.2:5556")

current_date = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
FILE_NAME = "data/Sensor_Data" + current_date + ".csv"

df = pd.DataFrame(columns = ["LOX psi", "KER psi", "PRES psi"])
#df.to_csv(FILE_NAME, mode = 'w')

# Queue of all data that will later be sent to the server
SEND_INFO = queue.Queue()

# Queue of all demands from the server
RECEIVED_LOGS = queue.Queue()
RECEIVED_MESSAGES = queue.Queue()

# Enums for status of server
class Status(IntEnum):
    WAITING = 1
    CMD_READY = 2
    DMR_READY = 3

# Current status of the server (used by host to test
# connection and determine when to send messages)
SERVER_STATUS = 0

# Set if the server status changed recently
STATUS_CHANGE = threading.Event()
STATUS_CHANGE.clear()

'''Message types:
    Sent:
        cmd - Command with arguments, which can be executed on server
        dmr - Replies to demands from the server
        sta - Requests the server status
    Received:
        log - CSV data from the server
        sta - The current server status'''

def sender():
    '''Thread which immediately sends any info in the
    SEND_INFO queue to the server over the socket'''
    global SEND_INFO
    while(True):
        send_socket.send_string(SEND_INFO.get())

def receiver():
    '''Thread which processes all information received 
    from the server'''
    global RECEIVED_LOGS, RECEIVED_MESSAGES, SERVER_STATUS
    while(True):
        message = receive_socket.recv()
        message = str(message, 'UTF-8')
        a = message.find('%')
        if message[:a] == "log":
            RECEIVED_LOGS.put(message[a+1:])
        elif message[:a] == "msg":
            '''RECEIVED_MESSAGES.put(message[a+1:])'''
            print('\n' + message[a+1:])
        elif message[:a] == "sta":
            a = int(message[a+1:])
            if SERVER_STATUS != a:
                SERVER_STATUS = a
                STATUS_CHANGE.set()

def logger():
    '''Thread which stores all data in the RECEIVED_LOGS
    queue as a csv file'''
    global FILE_NAME
    while(True):
        data = RECEIVED_LOGS.get()
        with open(FILE_NAME, 'a') as file:
            file.write(data)
            file.close()

def user_io():
    '''Thread which controls user io, by getting input
    and printing output'''
    global SEND_INFO, STATUS_CHANGE, SERVER_STATUS
    while(True):
        STATUS_CHANGE.wait()
        STATUS_CHANGE.clear()

        if SERVER_STATUS == Status.WAITING:
            print(". . .")
        elif SERVER_STATUS == Status.CMD_READY:
            cmd = input("\n> > > ")
            cmd = "cmd%" + cmd
            SEND_INFO.put(cmd)
        elif SERVER_STATUS == Status.DMR_READY:
            dmr = input("\n---> ")
            dmr = "dmr%" + dmr
            SEND_INFO.put(dmr)

def req_status():
    '''Manually update the current status of the server'''
    global SEND_INFO
    message = "sta%"
    SEND_INFO.put(message)

def get_file_name():
    global FILE_NAME
    '''Gives the name of the file all data is
    currently being saved to'''
    return FILE_NAME

send = threading.Thread(name='sender', target=sender)
send.start()

receive = threading.Thread(name='receiver', target=receiver)
receive.start()

log = threading.Thread(name='logger', target=logger)
log.start()

req_status()

STATUS_CHANGE.wait()
print("Sucessfully Connected")

user_inout = threading.Thread(name='userio', target=user_io)
user_inout.start()
