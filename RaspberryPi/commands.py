'''Contains most commands that the user
can execute'''
from enum import Enum
from optparse import Values
from re import S
from socket import TIPC_MEDIUM_IMPORTANCE

#from pygtkcompat import enable_webkit
import message as msg
import os
from time import sleep
import RPi.GPIO as GPIO
import yaml
import json
import random

import sensors

__author__ = "Aidan Cantu, Joshua Vondracek"

LAST_COMMAND = []

# Setting up the output pins for the valves/ valve control

GPIO.setmode(GPIO.BOARD)

TWO_WAY_PIN = 36
TEN_FUEL_PIN = 37
PRESS_FUEL_PIN = 31
MAIN_FUEL_PIN = 33
VENT_FUEL_PIN = 29

GPIO.setup(TWO_WAY_PIN, GPIO.OUT)
GPIO.setup(TEN_FUEL_PIN, GPIO.OUT)
GPIO.setup(PRESS_FUEL_PIN, GPIO.OUT)
GPIO.setup(MAIN_FUEL_PIN, GPIO.OUT)
GPIO.setup(VENT_FUEL_PIN, GPIO.OUT)

OPEN = GPIO.HIGH
CLOSE = GPIO.LOW


STATES = {
    'SYSTEM': {
        "Safety": "On",
        "System Hold": "Off",

        "Data Logging": "Off", # Do we want to have a state for raw data reading - see if it's connected? 
        "PT Simulation": "Off" 
    },

    'VALVES': {
        "Two-Way Solenoid": "Closed",

        "Fuel 10 Percent Pressurant Valve": "Closed",
        "Fuel Pressurant Valve": "Closed",
        "Fuel Main Valve": "Closed",
        "Fuel Vent Valve": "Closed"
        
    },

    "Ignitor": "Off"
}


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
    
    ten_percent_open: Opens the 10 PERCENT FLOW valve
    ten_percent_close: Closes the 10 PERCENT FLOW valve
    full_flow_open: Opens the FULL FLOW valve
    full_flow_close: Closes the FULL FLOW valve

    
    ventlox_open: Opens the LOX vent valve
    ventlox_close: Closes the LOX vent valve
    ventfuel_open: Opens the FUEL vent valve
    ventfuel_close: Closes the FUEL vent valve
    
    mainlox_open: Opens the LOX main valve
    mainlox_close: Closes the LOX main valve
    mainfuel_open: Opens the FUEL main valve
    mainfuel_close: Closes the FUEL main valve

    "ignition": [ignition, 1],
    "a": [a, 1],
    "SYS": [SYS, 1]
    '''
    msg.tell(s)


''' 
======================================================================
SINGLE FUNCTIONS AND COMMANDS (NOT INTERDEPENDENT ON OTHER COMMANDS) |
======================================================================
'''

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

def pt_simulation(currently_generating):
    if currently_generating == "on":    
        msg.tell("SIMULATION OPTIONS:\n1.) Linear\n2.) Exponential\n3.) Random\n(Put random character to quit)")
        sim_type = msg.input("Enter the simulation type's number:")
        msg.tell("You entered {}".format(type(sim_type)))
        
        if not(sim_type == "1" or sim_type == "2" or sim_type == "3"):
            msg.tell("Quitting the simulator")
            return
         
        time_increment = msg.input("Input PT update speed (in ms): ")
        '''while True:
            try:
                time_increment = msg.demand("Input PT update speed (in ms): ")
                if time_increment <= 50:
                    msg.tell("Please input integer above 50 only...") 
                    continue 
                break
            except ValueError:
                msg.tell("Please input integer above 50 only...")  
                continue'''

        pt_sim_type = {

            "Type": "",
            "Y Intercept": 0,
            "Slope": 0,
            "Exponent": 0,
            "Upper Bound": 0,
            "Lower Bound": 0,
            "Update Speed": time_increment

        }

        if sim_type == 1:
            msg.tell("Selected linear. Please enter characteristics:")
            pt_sim_type["Type"] = "Linear"
            while True:
                try:
                    pt_sim_type["Y Intercept"] = msg.demand("Input y intercept: ")
                    pt_sim_type["Slope"] = msg.demand("Input slope: ")
                    pt_sim_type["Lower Bound"] = msg.demand("Input a lower bound for the simulation: ")
                    pt_sim_type["Upper Bound"] = msg.demand("Input an upper bound for the simulation: ")
                    
                    # Might need to add something to check that equation will run within the decided bounds
                    '''
                    if time_increment <= 50:
                        msg.tell("Please input integer above 50 only...") 
                        continue 
                    '''
                    break
                except ValueError:
                    msg.tell("Please input integers only...")  
                    continue
            msg.logging_dummy(True, pt_sim_type)
            msg.tell("Trying to start logging dummy data")
            #return pt_sim_type

        elif sim_type == "2":
            msg.tell("Selected exponential. Please enter characteristics.")
            while True:
                try:
                    pt_sim_type["Y Intercept"] = int(msg.demand("Input y intercept: "))
                    pt_sim_type["Exponent"] = int(msg.demand("Input slope: "))
                    pt_sim_type["Lower Bound"] = int(msg.demand("Input a lower bound for the simulation: "))
                    pt_sim_type["Upper Bound"] = int(msg.demand("Input an upper bound for the simulation: "))
                            
                            # Might need to add something to check that equation will run within the decided bounds
                    
                    break
                except ValueError:
                    msg.tell("Please input integers only...")  
                    continue
            return pt_sim_type
               
        elif sim_type == "3":
            msg.tell("Selected random. Please enter characteristics.")

        else:
            msg.tell("Quitting Pressure Transducer Simulator")
    elif currently_generating == "off":
        msg.logging_dummy(False)


def led_test():
    GPIO.output(TWO_WAY_PIN, OPEN)
    GPIO.output(TEN_FUEL_PIN, OPEN)
    GPIO.output(PRESS_FUEL_PIN, OPEN)
    GPIO.output(MAIN_FUEL_PIN, OPEN)
    GPIO.output(VENT_FUEL_PIN, OPEN)
    sleep(1)
    GPIO.output(TWO_WAY_PIN, CLOSE)
    GPIO.output(TEN_FUEL_PIN, CLOSE)
    GPIO.output(PRESS_FUEL_PIN, CLOSE)
    GPIO.output(MAIN_FUEL_PIN, CLOSE)
    GPIO.output(VENT_FUEL_PIN, CLOSE)
    sleep(0.5)
    GPIO.output(TWO_WAY_PIN, OPEN)
    sleep(0.5)
    GPIO.output(TWO_WAY_PIN, CLOSE)
    GPIO.output(TEN_FUEL_PIN, OPEN)
    sleep(0.5)
    GPIO.output(TEN_FUEL_PIN, CLOSE)
    GPIO.output(PRESS_FUEL_PIN, OPEN)
    sleep(0.5)
    GPIO.output(PRESS_FUEL_PIN, CLOSE)
    GPIO.output(VENT_FUEL_PIN, OPEN)
    sleep(0.5)
    GPIO.output(VENT_FUEL_PIN, CLOSE)
    GPIO.output(MAIN_FUEL_PIN, OPEN)
    sleep(0.5)
    GPIO.output(MAIN_FUEL_PIN, CLOSE)
    

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

def clean_up():
    GPIO.cleanup()

def enable_2way():
    global STATES
    print("Opening 2-way solenoid")
    GPIO.output(TWO_WAY_PIN, OPEN)
    STATES["VALVES"]["Two-Way Solenoid"] = "Open"
    msg.tell("2-way solenoid has been opened")

def disable_2way():
    global STATES
    print("Closing 2-way solenoid")
    GPIO.output(TWO_WAY_PIN, CLOSE)
    STATES["VALVES"]["Two-Way Solenoid"] = "Closed"
    msg.tell("2-way solenoid has been closed")

def fuel_ten_open():
    global STATES
    print("Opening the 10 percent valve")
    GPIO.output(TEN_FUEL_PIN, OPEN)
    STATES["VALVES"]["Fuel 10 Percent Pressurant Valve"] = "Open"
    msg.tell("10 percent valve opened")

def fuel_ten_close():
    global STATES
    print("Closing the 10 percent valve")
    GPIO.output(TEN_FUEL_PIN, CLOSE)
    STATES["VALVES"]["Fuel 10 Percent Pressurant Valve"] = "Closed"
    msg.tell("Fuel 10 percent valve closed")

def fuel_press_open():
    global STATES
    print("Opening the fuel pressurant valve")
    GPIO.output(PRESS_FUEL_PIN, OPEN)
    STATES["VALVES"]["Fuel Pressurant Valve"] = "Open"
    msg.tell("Fuel pressurant valve opened")

def fuel_press_close():
    global STATES
    print("Closing the fuel pressurant valve")
    GPIO.output(PRESS_FUEL_PIN, CLOSE)
    STATES["VALVES"]["Fuel Pressurant Valve"] = "Closed"
    msg.tell("Fuel pressurant valve closed")

def fuel_main_open():
    global STATES
    print("Opening the main fuel valve")
    GPIO.output(MAIN_FUEL_PIN, OPEN)
    STATES["VALVES"]["Fuel Main Valve"] = "Open"
    msg.tell("Main fuel valve opened")

def fuel_main_close():
    global STATES
    print("Closing the main fuel valve")
    GPIO.output(MAIN_FUEL_PIN, CLOSE)
    STATES["VALVES"]["Fuel Main Valve"] = "Closed"
    msg.tell("Main fuel valve closed")

def fuel_vent_open():
    global STATES
    print("Opening the fuel vent valve")
    GPIO.output(VENT_FUEL_PIN, OPEN)
    STATES["VALVES"]["Fuel Vent Valve"] = "Open"
    msg.tell("Fuel vent valve opened")

def fuel_vent_close():
    global STATES
    print("Closing the fuel vent valve")
    GPIO.output(VENT_FUEL_PIN, CLOSE)
    STATES["VALVES"]["Fuel Vent Valve"] = "Closed"
    msg.tell("Fuel vent valve closed")


# def ignitor_on():
#     global STATES
#     print("Turning the ignitor pin on")
#     GPIO.output(IGNITION_PIN, GPIO.HIGH)  # Make sure this pin is actually set to "HIGH" for on
#     STATES["Ignitor"] = "On"
#     msg.tell("Turned the ignitor pin on")

# def ignitor_off():
#     global STATES
#     print("Turning the ignitor pin on")
#     GPIO.output(IGNITION_PIN, GPIO.LOW)
#     STATES["Ignitor"] = "Off"
#     msg.tell("Turned the ignitor pin on")

def a():
    print("USER ABORT")
    msg.tell("SYSTEM ABORTED VIA USER INPUT")

# def pt_check():
#     print("Checking PT readings")

def sys():
    global STATES
    states_string = json.dumps(STATES)
    print("Printed System States")
    msg.tell(states_string.replace(",", "\n"))


# def hold():
#     print("ENTERING A HOLD STATE")

# ''' 
# ==========================================================================================
# COMPOUND FUNCTIONS AND COMMANDS (INTERDEPENDENT ON THE ABOVE SINGLE FUNCTIONS/ COMMANDS) |
# ==========================================================================================
# '''

def shutdown():
    print("Cleaning the pins of the RPi")
    print("Closing this program")
    if msg.demand("Are you sure you want to shutdown? [y/n]") == 'y':
        clean_up()
        msg.tell("Shutting down raspberry pi!")
        os.system('exit')

# def ignition():
#     if msg.demand("Are you sure you want to start ignition? [yes/no]") == 'yes':
        
#         msg.tell("Ignition beginning: Countdown from 10.")
#         for sec in range(10):
#             msg.tell("{}".format(10-sec))
#             sleep(1)
# def a():
#     print("USER ABORT")
#     msg.tell("SYSTEM ABORTED VIA USER INPUT")
#         ten_percent_open()
#         mainfuel_open()
#         mainlox_open()
#         ignitor_on()
#         sleep(2)
#         full_flow_open()
#         msg.tell("BOOM")
#     else:
#         msg.tell("Aborted the ignition procedure")


# def reset():
#     if msg.demand("Are you sure you want to reset the system? [yes/no]") == 'yes':
#         print("RESETTING THE SYSTEM: CLOSING ALL VALVES - TURNING OFF IGNITOR")
#         msg.tell("RESETTING THE SYSTEM: CLOSING ALL VALVES - TURNING OFF IGNITOR")
#         ten_percent_close()
#         full_flow_close()
#         mainfuel_close()
#         mainlox_close()
#         ventfuel_close()
#         ventlox_close()
#         ignitor_off()
#     else:
#         msg.tell("Cancelled the reset of the system")

# def engine_abort():
#     print("ABORTING THE ENGINE SYSTEM")
#     ten_percent_close()
#     full_flow_close()
#     mainfuel_close()
#     mainlox_close()
#     sleep(0.5)
#     ventfuel_open()
#     ventlox_open()
#     msg.tell("ABORTING THE ENGINE SYSTEM - PRESSURE VALVES CLOSED - MAIN VALVES CLOSED - VENT VALVES OPENED" )

# def full_abort():
#     print("FULLY ABORTING THE SYSTEM")
#     ten_percent_close()
#     full_flow_close()
#     mainfuel_open()
#     mainlox_open()
#     ventfuel_open()
#     ventlox_open()
#     msg.tell("FULLY ABORTING THE SYSTEM - PRESSURE VALVES CLOSED - ALL MAIN AND VENT VALVES OPENED ")

# def hold_check():
#     hold()

# def energy_efficient():
#     global STATES
#     print("Turning on Energy Efficient mode")
#     for key, value in STATES["VALVES"]:
#         if value == "Closed":
#             yield key
#     msg.tell("Turning on Energy Efficient Mode - Turning off unused 2-way solenoids")


#def pt_simulation():





#dictionary of all commands, and number of args
commands = {
    
    "log": [log, 2],
    "calibrate": [calibrate, 1],

    "ping": [ping, 1],
    "help": [help, 1],
    "reboot": [reboot, 1],
    "rr": [rr, 1],

    "led_test": [led_test, 1],
    "shutdown": [shutdown, 1],
    "clean_up": [clean_up, 1],

    # "led_on": [led_on, 1],
    # "led_off": [led_off, 1],

    "enable_2way": [enable_2way, 1],
    "disable_2way": [disable_2way, 1],
    
    "fuel_ten_open": [fuel_ten_open, 1],
    "fuel_ten_close": [fuel_ten_close, 1],
    "fuel_press_open": [fuel_press_open, 1],
    "fuel_press_close": [fuel_press_close, 1],
    
    "fuel_vent_open": [fuel_vent_open, 1],
    "fuel_vent_close": [fuel_vent_close, 1],
    "fuel_main_open": [fuel_main_open, 1],
    "fuel_main_close": [fuel_main_close, 1],
    
    # "mainlox_open": [mainlox_open, 1],
    # "mainlox_close": [mainlox_close, 1],
    # "mainfuel_open": [mainfuel_open, 1],
    # "mainfuel_close": [mainfuel_close, 1],

    # "ignition": [ignition, 1],
    # "ignitor_on": [ignitor_on, 1],
    # "ignitor_off": [ignitor_off, 1],

    # "full_abort": [full_abort, 1],
    # "engine_abort": [engine_abort, 1],

    # "pt_simulation": [pt_simulation, 2],
    # "energy_efficient": [energy_efficient, 2],

    # "a": [a, 1],
    # "sys": [sys, 1],
    # "reset": [reset, 1],
    # "quit": [quit, 1]

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