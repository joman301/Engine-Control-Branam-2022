'''Contains most commands that the user
can execute'''
from enum import Enum

from pygtkcompat import enable_webkit
import message as msg
import time
import os
from time import sleep

#import board
#from adafruit_motor import stepper
#from adafruit_motorkit import MotorKit

import sensors

__author__ = "Aidan Cantu"

LAST_COMMAND = []
LOX_MOTOR_POS_DEG = 0
KER_MOTOR_POS_DEG = 0

# stepper1 --> M1, M2 terminals
# stepper2 --> M3, M4 terminals

# 200 steps --> 360 deg; 1.8 deg per step
# Gear ratio of 100:1

# stepper.FORWARD = clockwise, increase presssure
# stepper.BACKWARD = counterclockwise, decrease pressure

#motors = MotorKit(i2c=board.I2C())
GEAR_RATIO = 100

class Dev(Enum):
    LOX_MOTOR = 1
    KER_MOTOR = 2


def help():
    s = '''
    log [T/F]: Turns on/ off sensor csv data logging 
    calibrate: Sets the y intercept of sensors to 0

    ping: Returns pong if connected to server
    help: Pulls up this help menu
    reboot: Restarts the server
    rr: Repeats the last command

    led_on: Turns on an LED
    led_off: Turns off the LED

    enable_2way: Enables the 2-way solenoids, valves can actuate
    disable_2way: Disables the 2-way solenoids, valves can't actuate
    
    press: Opens the main pressurant valve
    depress: Closes the main pressurant valve
    
    ventlox_open: Opens the LOX vent valve
    ventlox_close: Closes the LOX vent valve
    ventfuel_open: Opens the fuel vent valve
    ventfuel_close: Closes the fuel vent valve
    
    mainlox_open: Opens the LOX main valve
    mainlox_close: Closes the LOX main valve
    mainfuel_open: Opens the FUEL main valve
    mainfuel_close: Closes the FUEL main valve

    "ignition": [ignition, 1],
    "a": [a, 1],
    "SYS": [SYS, 1]
    '''
    msg.tell(s)

# Starts or stops logging data from sensors
def log(currently_logging):
    if currently_logging.lower() == "true":
        msg.logging(True)
        msg.tell("Started Logging Data")
    elif currently_logging.lower() == "false":
        msg.logging(False)
        msg.tell("Stopped Logging Data")
    else:
        msg.tell("Error: Invalid Option (Enter \"True\" or \"False\")")

def calibrate():
    '''calibrates all sensors by setting the y-intercept
    of voltage-value conversion to 0'''
    sensors.calibrate_all()

# Repeats the previous command
def rr():
    if len(LAST_COMMAND) > 0:
        exe(LAST_COMMAND)
    else:
        return 1

def ping():
    msg.tell("pong")

def reboot():
    if msg.demand("Are you sure you want to reboot [yes/no]") == 'yes':
        msg.tell("Rebooting system (will automatically reconnect shortly)")
        os.system('sudo reboot now')
    else:
        msg.tell("aborting")

def led_on():
    print('I am turning on the LED')
    msg.tell("LED turned on")

def led_off():
    print('I am turning off the LED')
    msg.tell("LED turned off")

def enable_2way():
    print("2-ways are enabled")
    msg.tell("2-way solenoids have been enabled")

def disable_2way():
    print("2-way solenoids are disabled")
    msg.tell("2-way solenoids have been disabled")

def press():
    print("Opening the pressurant valve")
    msg.tell("Pressurant valve opened")

def depress():
    print("Closing the pressurant valve")
    msg.tell("Pressurant valve closed")

def ventlox_open():
    print("Opening the LOX vent valve")
    msg.tell("LOX vent valve opened")

def ventlox_close():
    print("Closing the LOX vent valve")
    msg.tell("LOX vent valve closed")

def ventfuel_open():
    print("Opening the fuel vent valve")
    msg.tell("FUEL vent valve opened")

def ventfuel_close():
    print("Closing the fuel vent valve")
    msg.tell("FUEL vent valve closed")

def mainlox_open():
    print("Opening the main LOX valve")
    msg.tell("Main LOX valve opened")

def mainlox_close():
    print("Closing the main LOX valve")
    msg.tell("Main LOX valve closed")

def mainfuel_open():
    print("Opening the main FUEL valve")
    msg.tell("Main FUEL valve opened")

def mainfuel_close():
    print("Closing the main FUEL valve")
    msg.tell("Main FUEL valve closed")

def ignition():
    if msg.demand("Are you sure you want to start ignition? [yes/no]") == 'yes':
        msg.tell("Ignition beginning: Countdown from 10.")
        for sec in range(10):
            msg.tell("{}".format(sec))
            sleep(1)
        msg.tell("BOOM")
    else:
        msg.tell("Aborted the ignition procedure")

def a():
    print("ABORT")
    msg.tell("SYSTEM ABORTED")

def SYS():
    print("Work in progress")
    msg.tell("Work in progress")


#dictionary of all commands, and number of args
commands = {
    
    "log": [log, 2],
    "calibrate": [calibrate, 1],

    "ping": [ping, 1],
    "help": [help, 1],
    "reboot": [reboot, 1],
    "rr": [rr, 1],

    "led_on": [led_on, 1],
    "led_off": [led_off, 1],

    "enable_2way": [enable_2way, 1],
    "disable_2way": [disable_2way, 1],
    
    "press": [press, 1],
    "depress": [depress, 1],
    
    "ventlox_open": [ventlox_open, 1],
    "ventlox_close": [ventlox_close, 1],
    "ventfuel_open": [ventfuel_open, 1],
    "ventfuel_close": [ventfuel_close, 1],
    
    "mainlox_open": [mainlox_open, 1],
    "mainlox_close": [mainlox_close, 1],
    "mainfuel_open": [mainfuel_open, 1],
    "mainfuel_close": [mainfuel_close, 1],

    "ignition": [ignition, 1],
    "a": [a, 1],
    "SYS": [SYS, 1]

}

# Takes an array including command and arguments, and executes it
def exe(user_command):
    global LAST_COMMAND 

    user_method = user_command[0]
    user_args = user_command[1:]

    if user_method != 'rr':
        LAST_COMMAND = user_command


    if (user_method in commands.keys()) == False:
        msg.tell(("Error: command \"%s\" not found") % user_command )
        msg.cmd_ready()
        return 2
    
    method = commands.get(user_method)[0]
    num_args = commands.get(user_method)[1]

    if len(user_command) != num_args:
        msg.tell(("Error: %s arguments were given when %s were expected") % (len(user_command), num_args))
        msg.cmd_ready()
        return 3

    try:
        a = method(*user_args)
        msg.cmd_ready()
        return a
    except:
        msg.tell("An error has occured")
        msg.cmd_ready()
        return 1

# Converts a string to an array of arguments
def parse(user_input):
    user_input = str.lower(user_input)
    user_command = user_input.split()

    for i, item in enumerate(user_command):
        if item.isnumeric():
            user_command[i] = int(item)

    return user_command