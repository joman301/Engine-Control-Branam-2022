'''Contains most commands that the user
can execute'''
from enum import Enum
from optparse import Values
from re import S
from socket import TIPC_MEDIUM_IMPORTANCE

#from pygtkcompat import enable_webkit
import message as msg
import time
import os
from time import sleep
import RPi.GPIO as GPIO
import yaml
import json

import sensors

__author__ = "Aidan Cantu, Joshua Vondracek"

LAST_COMMAND = []

# Setting up the output pins for the valves/ valve control

with open('setup.yml', 'r') as file:
    prime_service = yaml.safe_load(file)



# MAINPRESS_PIN

# TENPERCENT_PIN = "P9_11"
# FULLFLOW_PIN = "P9_11"
# FUELPRESS
# VENTLOX_PIN = "P9_23"
# MAINLOX_PIN = "P9_21"
# VENTFUEL_PIN = "P9_26"
# MAINFUEL_PIN = "P9_13"  
# IGNITION_PIN = "P9_41"
# TENPERCENT_PIN_2WAY = "P9_41"
# FULLFLOW_PIN_2WAY = "P9_21"  
# VENTLOX_PIN_2WAY = "P9_23"
# MAINLOX_PIN_2WAY = "P9_24"
# VENTFUEL_PIN_2WAY = "P9_26"
# MAINFUEL_PIN_2WAY = "P9_23" 

# GPIO.setup(TENPERCENT_PIN, GPIO.OUT)
# GPIO.setup(FULLFLOW_PIN, GPIO.OUT)
# GPIO.setup(VENTLOX_PIN, GPIO.OUT)
# GPIO.setup(MAINLOX_PIN, GPIO.OUT)
# GPIO.setup(VENTFUEL_PIN, GPIO.OUT)
# GPIO.setup(MAINFUEL_PIN, GPIO.OUT)
# GPIO.setup(IGNITION_PIN, GPIO.OUT)
# GPIO.setup(TENPERCENT_PIN_2WAY, GPIO.OUT)
# GPIO.setup(FULLFLOW_PIN_2WAY, GPIO.OUT)
# GPIO.setup(VENTLOX_PIN_2WAY, GPIO.OUT)
# GPIO.setup(MAINLOX_PIN_2WAY, GPIO.OUT)
# GPIO.setup(VENTFUEL_PIN_2WAY, GPIO.OUT)
# GPIO.setup(MAINFUEL_PIN_2WAY, GPIO.OUT)


# GPIO.output(TENPERCENT_PIN, GPIO.HIGH)
# GPIO.output(FULLFLOW_PIN, GPIO.HIGH)
# GPIO.output(VENTLOX_PIN, GPIO.HIGH)
# GPIO.output(MAINLOX_PIN, GPIO.HIGH)
# GPIO.output(VENTFUEL_PIN, GPIO.HIGH)
# GPIO.output(MAINFUEL_PIN, GPIO.HIGH)
# GPIO.output(IGNITION_PIN, GPIO.HIGH)
# GPIO.output(TENPERCENT_PIN_2WAY, GPIO.HIGH)
# GPIO.output(FULLFLOW_PIN_2WAY, GPIO.HIGH)
# GPIO.output(VENTLOX_PIN_2WAY, GPIO.HIGH)
# GPIO.output(MAINLOX_PIN_2WAY, GPIO.HIGH)
# GPIO.output(VENTFUEL_PIN_2WAY, GPIO.HIGH)
# GPIO.output(MAINFUEL_PIN_2WAY, GPIO.HIGH)

STATES = {
    'SYSTEM': {
        "Safety": "On",
        "System Hold": "Off",

        "Data Logging": "Off", # Do we want to have a state for raw data reading - see if it's connected? 
        "PT Simulation": "Off" 
    },

    'VALVES': {
        "Two-Way Solenoids": "Closed",

        "10 percent Flow Valve": "Closed",
        "Full Flow Valve": "Closed",

        "LOX Main Valve": "Closed",
        "LOX Vent Valve": "Closed",

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
    GPIO.output(led_test, GPIO.LOW)
    msg.tell("LED turned on")

def led_off():
    print('I am turning off the LED')
    GPIO.output(led_test, GPIO.HIGH)
    msg.tell("LED turned off")

def enable_2way():
    global STATES
    print("2-ways are enabled")
    GPIO.output(TENPERCENT_PIN_2WAY, GPIO.LOW)
    GPIO.output(FULLFLOW_PIN_2WAY, GPIO.LOW)
    GPIO.output(VENTLOX_PIN_2WAY, GPIO.LOW)
    GPIO.output(MAINLOX_PIN_2WAY, GPIO.LOW)
    GPIO.output(VENTFUEL_PIN_2WAY, GPIO.LOW)
    GPIO.output(MAINFUEL_PIN_2WAY, GPIO.LOW)
    STATES["Two-Way Solenoids"] = "Open"
    msg.tell("2-way solenoids have been opened")

def disable_2way():
    global STATES
    print("2-way solenoids are disabled")
    GPIO.output(TENPERCENT_PIN_2WAY, GPIO.HIGH)
    GPIO.output(FULLFLOW_PIN_2WAY, GPIO.HIGH)
    GPIO.output(VENTLOX_PIN_2WAY, GPIO.HIGH)
    GPIO.output(MAINLOX_PIN_2WAY, GPIO.HIGH)
    GPIO.output(VENTFUEL_PIN_2WAY, GPIO.HIGH)
    GPIO.output(MAINFUEL_PIN_2WAY, GPIO.HIGH)
    STATES["Two-Way Solenoids"] = "Closed"
    msg.tell("2-way solenoids have been closed")

def ten_percent_open():
    global STATES
    print("Opening the 10 percent valve")
    GPIO.output(TENPERCENT_PIN, GPIO.LOW)
    STATES["10 Percent Flow Valve"] = "Open"
    msg.tell("10 percent valve opened")

def ten_percent_close():
    global STATES
    print("Closing the pressurant valve")
    GPIO.output(TENPERCENT_PIN, GPIO.HIGH)
    STATES["10 Percent Flow Valve"] = "Closed"
    msg.tell("10 percent valve closed")

def full_flow_open():
    global STATES
    print("Opening the full-flow valve")
    GPIO.output(FULLFLOW_PIN, GPIO.LOW)
    STATES["Full Flow Valve"] = "Open"
    msg.tell("Full-flow valve opened")

def full_flow_close():
    global STATES
    print("Closing the full-flow valve")
    GPIO.output(FULLFLOW_PIN, GPIO.HIGH)
    STATES["Full Flow Valve"] = "Closed"
    msg.tell("Full-flow valve closed")

def ventlox_open():
    global STATES
    print("Opening the LOX vent valve")
    GPIO.output(VENTLOX_PIN, GPIO.LOW)
    STATES["LOX Vent Valve"] = "Open"
    msg.tell("LOX vent valve opened")

def ventlox_close():
    global STATES
    print("Closing the LOX vent valve")
    GPIO.output(VENTLOX_PIN, GPIO.HIGH)
    STATES["LOX Vent Valve"] = "Closed"
    msg.tell("LOX vent valve closed")

def ventfuel_open():
    global STATES
    print("Opening the fuel vent valve")
    GPIO.output(VENTFUEL_PIN, GPIO.LOW)
    STATES["Fuel Vent Valve"] = "Open"
    msg.tell("FUEL vent valve opened")

def ventfuel_close():
    global STATES
    print("Closing the fuel vent valve")
    GPIO.output(VENTFUEL_PIN, GPIO.HIGH)
    STATES["Fuel Vent Valve"] = "Closed"
    msg.tell("FUEL vent valve closed")

def mainlox_open():
    global STATES
    print("Opening the main LOX valve")
    GPIO.output(MAINLOX_PIN, GPIO.LOW)
    STATES["LOX Main Valve"] = "Open"
    msg.tell("Main LOX valve opened")

def mainlox_close():
    global STATES
    print("Closing the main LOX valve")
    GPIO.output(MAINLOX_PIN, GPIO.HIGH)
    STATES["LOX Main Valve"] = "Closed"
    msg.tell("Main LOX valve closed")

def mainfuel_open():
    global STATES
    print("Opening the main FUEL valve")
    GPIO.output(MAINFUEL_PIN, GPIO.LOW)
    STATES["Fuel Main Valve"] = "Open"
    msg.tell("Main FUEL valve opened")

def mainfuel_close():
    global STATES
    print("Closing the main FUEL valve")
    GPIO.output(MAINFUEL_PIN, GPIO.HIGH)
    STATES["Fuel Main Valve"] = "Closed"
    msg.tell("Main FUEL valve closed")

def ignitor_on():
    global STATES
    print("Turning the ignitor pin on")
    GPIO.output(IGNITION_PIN, GPIO.HIGH)  # Make sure this pin is actually set to "HIGH" for on
    STATES["Ignitor"] = "On"
    msg.tell("Turned the ignitor pin on")

def ignitor_off():
    global STATES
    print("Turning the ignitor pin on")
    GPIO.output(IGNITION_PIN, GPIO.LOW)
    STATES["Ignitor"] = "Off"
    msg.tell("Turned the ignitor pin on")

def a():
    print("USER ABORT")
    msg.tell("SYSTEM ABORTED VIA USER INPUT")

def pt_check():
    print("Checking PT readings")

def sys():
    global STATES
    states_string = json.dumps(STATES)
    print("Printed System States")
    msg.tell(states_string.replace(",", "\n"))

def quit():
    print("Cleaning the pins of the BBB")
    print("Closing this program")
    GPIO.cleanup()
    os.system('exit')
    msg.tell("Cleaning all the pins, closing the program on the BBB")

def hold():
    print("ENTERING A HOLD STATE")

''' 
==========================================================================================
COMPOUND FUNCTIONS AND COMMANDS (INTERDEPENDENT ON THE ABOVE SINGLE FUNCTIONS/ COMMANDS) |
==========================================================================================
'''

def ignition():
    if msg.demand("Are you sure you want to start ignition? [yes/no]") == 'yes':
        
        msg.tell("Ignition beginning: Countdown from 10.")
        for sec in range(10):
            msg.tell("{}".format(10-sec))
            sleep(1)
        ten_percent_open()
        mainfuel_open()
        mainlox_open()
        ignitor_on()
        sleep(2)
        full_flow_open()
        msg.tell("BOOM")
    else:
        msg.tell("Aborted the ignition procedure")


def reset():
    if msg.demand("Are you sure you want to reset the system? [yes/no]") == 'yes':
        print("RESETTING THE SYSTEM: CLOSING ALL VALVES - TURNING OFF IGNITOR")
        msg.tell("RESETTING THE SYSTEM: CLOSING ALL VALVES - TURNING OFF IGNITOR")
        ten_percent_close()
        full_flow_close()
        mainfuel_close()
        mainlox_close()
        ventfuel_close()
        ventlox_close()
        ignitor_off()
    else:
        msg.tell("Cancelled the reset of the system")

def engine_abort():
    print("ABORTING THE ENGINE SYSTEM")
    ten_percent_close()
    full_flow_close()
    mainfuel_close()
    mainlox_close()
    sleep(0.5)
    ventfuel_open()
    ventlox_open()
    msg.tell("ABORTING THE ENGINE SYSTEM - PRESSURE VALVES CLOSED - MAIN VALVES CLOSED - VENT VALVES OPENED" )

def full_abort():
    print("FULLY ABORTING THE SYSTEM")
    ten_percent_close()
    full_flow_close()
    mainfuel_open()
    mainlox_open()
    ventfuel_open()
    ventlox_open()
    msg.tell("FULLY ABORTING THE SYSTEM - PRESSURE VALVES CLOSED - ALL MAIN AND VENT VALVES OPENED ")

def hold_check():
    hold()

def energy_efficient():
    global STATES
    print("Turning on Energy Efficient mode")
    for key, value in STATES["VALVES"]:
        if value == "Closed":
            yield key
    msg.tell("Turning on Energy Efficient Mode - Turning off unused 2-way solenoids")


#def pt_simulation():





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
    
    "ten_percent_open": [ten_percent_open, 1],
    "ten_percent_close": [ten_percent_close, 1],
    "full_flow_open": [full_flow_open, 1],
    "full_flow_close": [full_flow_close, 1],
    
    "ventlox_open": [ventlox_open, 1],
    "ventlox_close": [ventlox_close, 1],
    "ventfuel_open": [ventfuel_open, 1],
    "ventfuel_close": [ventfuel_close, 1],
    
    "mainlox_open": [mainlox_open, 1],
    "mainlox_close": [mainlox_close, 1],
    "mainfuel_open": [mainfuel_open, 1],
    "mainfuel_close": [mainfuel_close, 1],

    "ignition": [ignition, 1],
    "ignitor_on": [ignitor_on, 1],
    "ignitor_off": [ignitor_off, 1],

    "full_abort": [full_abort, 1],
    "engine_abort": [engine_abort, 1],

    "pt_simulation": [pt_simulation, 2],
    "energy_efficient": [energy_efficient, 2],

    "a": [a, 1],
    "sys": [sys, 1],
    "reset": [reset, 1],
    "quit": [quit, 1]

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