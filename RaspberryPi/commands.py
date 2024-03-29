'''Contains most commands that the user
can execute'''
from enum import Enum
from optparse import Values
from re import S
from socket import TIPC_MEDIUM_IMPORTANCE
from tabnanny import check
from datetime import datetime

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
VENT_FUEL_PIN = 29
MAIN_FUEL_PIN = 33

IGNITOR_PIN = 32

# TEN_LOX_PIN = ##
# PRESS_LOX_PIN = ##
# MAIN_LOX_PIN = ##
# VENT_LOX_PIN = ##

GPIO.setup(TWO_WAY_PIN, GPIO.OUT)
GPIO.setup(TEN_FUEL_PIN, GPIO.OUT)
GPIO.setup(PRESS_FUEL_PIN, GPIO.OUT)
GPIO.setup(MAIN_FUEL_PIN, GPIO.OUT)
GPIO.setup(VENT_FUEL_PIN, GPIO.OUT)

GPIO.setup(IGNITOR_PIN, GPIO.OUT)

# GPIO.setup(TEN_LOX_PIN, GPIO.OUT)
# GPIO.setup(PRESS_LOX_PIN, GPIO.OUT)
# GPIO.setup(MAIN_LOX_PIN, GPIO.OUT)
# GPIO.setup(VENT_LOX_PIN, GPIO.OUT)

OPEN = GPIO.LOW
CLOSE = GPIO.HIGH


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
        "Fuel Vent Valve": "Closed",

        # "LOX 10 Percent Pressurant Valve": "Closed",
        # "LOX Pressurant Valve": "Closed",
        # "LOX Main Valve": "Closed",
        # "LOX Vent Valve": "Closed"
        
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

    enable_2way: Enables the 2-way solenoid, valves can actuate
    disable_2way: Disables the 2-way solenoid, valves can't actuate
    
    fuel_press_open: Opens the FUEL PRESSURANT valve
    fuel_press_close: Closes the FUEL PRESSURANT valve
    fuel_vent_open: Opens the FUEL VENT valve
    fuel_vent_close: Closes the FUEL VENT valve

    fuel_ten_open: Opens the FUEL 10 PERCENT FLOW valve
    fuel_ten_close: Closes the FUEL 10 PERCENT FLOW valve
    fuel_main_open: Opens the FUEL FULL FLOW valve
    fuel_main_close: Closes the FUEL FULL FLOW valve

    fuel_fill: Prepares system to fill tanks with fuel
    ignition: Begins the ignition procedure
    a: Emergency abort - type this quickly and hit enter
    sys: Updates the user on system states: what's open/closed, etc

    engine_abort: Aborts through vent valves, avoids flowing through engine
    full_abort: Opens all engine and vent valves
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
    GPIO.output(IGNITOR_PIN, GPIO.HIGH)
    GPIO.output(MAIN_FUEL_PIN, OPEN)
    GPIO.output(TEN_FUEL_PIN, OPEN)
    GPIO.output(VENT_FUEL_PIN, OPEN)
    GPIO.output(PRESS_FUEL_PIN, OPEN)
    sleep(1)
    GPIO.output(TWO_WAY_PIN, CLOSE)
    GPIO.output(IGNITOR_PIN, GPIO.LOW)
    GPIO.output(MAIN_FUEL_PIN, CLOSE)
    GPIO.output(TEN_FUEL_PIN, CLOSE)
    GPIO.output(PRESS_FUEL_PIN, CLOSE)
    sleep(0.5)
    GPIO.output(TWO_WAY_PIN, OPEN)
    sleep(0.5)
    GPIO.output(TWO_WAY_PIN, CLOSE)
    GPIO.output(IGNITOR_PIN, GPIO.HIGH)
    sleep(0.5)
    GPIO.output(IGNITOR_PIN, GPIO.LOW)
    GPIO.output(MAIN_FUEL_PIN, OPEN)    
    sleep(0.5)
    GPIO.output(MAIN_FUEL_PIN, CLOSE)
    GPIO.output(TEN_FUEL_PIN, OPEN)
    sleep(0.5)
    GPIO.output(TEN_FUEL_PIN, CLOSE)
    GPIO.output(VENT_FUEL_PIN, OPEN)
    sleep(0.5)
    GPIO.output(VENT_FUEL_PIN, CLOSE)
    GPIO.output(PRESS_FUEL_PIN, OPEN)
    sleep(0.5)
    GPIO.output(PRESS_FUEL_PIN, CLOSE)
    
    

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
    '''Returns "pong" to host if RPi is correctly connected/ receiving 
    commands'''
    msg.tell("pong")

def reboot():
    if msg.demand("Are you sure you want to reboot [yes/no]") == 'yes':
        msg.tell("Rebooting system (will automatically reconnect shortly)")
        os.system('sudo reboot now')
    else:
        msg.tell("aborting")

def clean_up():
    '''Manually clean-up the GPIO pins on the RPi'''
    GPIO.cleanup()

def enable_2way():
    '''Opens the two-way solenoid, pressurizing the five-way solenoids'''
    global STATES
    print("Opening 2-way solenoid")
    GPIO.output(TWO_WAY_PIN, OPEN)
    STATES["VALVES"]["Two-Way Solenoid"] = "Open"
    msg.tell("2-way solenoid has been opened")

def disable_2way():
    '''Closes the two-way solenoids, preventing five-way solenoids from actuating'''
    global STATES
    print("Closing 2-way solenoid")
    GPIO.output(TWO_WAY_PIN, CLOSE)
    STATES["VALVES"]["Two-Way Solenoid"] = "Closed"
    msg.tell("2-way solenoid has been closed")

def check_2way_open():
    '''Ensures that two-way solenoid is open before attempting to actuate a valve'''
    global STATES

    if STATES["VALVES"]["Two-Way Solenoid"] == "Closed":
        command = msg.demand("The two-way solenoid is currently closed. Would you like to open it? [yes/no/cancel]")
        if command.upper() == "YES":
            enable_2way()
            return True
        elif command.upper() == "NO":
            msg.tell("Command preceded without turning on the two-way solenoid")
            return True
        else:
            msg.tell("Cancelled the command")
            return False
    else:
        return True

def fuel_ten_open():
    '''Opens the ten-percent pressure fuel valve'''
    global STATES
    if check_2way_open():
        print("Opening the 10 percent valve")
        GPIO.output(TEN_FUEL_PIN, OPEN)
        STATES["VALVES"]["Fuel 10 Percent Pressurant Valve"] = "Open"
        msg.tell("10 percent valve opened")


def fuel_ten_close():
    '''Closes the ten-percent pressure fuel valve'''
    global STATES
    if check_2way_open():
        print("Closing the 10 percent valve")
        GPIO.output(TEN_FUEL_PIN, CLOSE)
        STATES["VALVES"]["Fuel 10 Percent Pressurant Valve"] = "Closed"
        msg.tell("Fuel 10 percent valve closed")

def fuel_press_open():
    '''Opens the pressurant valve for the fuel lines'''
    global STATES
    if check_2way_open():
        print("Opening the fuel pressurant valve")
        GPIO.output(PRESS_FUEL_PIN, OPEN)
        STATES["VALVES"]["Fuel Pressurant Valve"] = "Open"
        msg.tell("Fuel pressurant valve opened")

def fuel_press_close():
    '''Closes the pressurant valve for the fuel lines'''
    global STATES
    if check_2way_open():
        print("Closing the fuel pressurant valve")
        GPIO.output(PRESS_FUEL_PIN, CLOSE)
        STATES["VALVES"]["Fuel Pressurant Valve"] = "Closed"
        msg.tell("Fuel pressurant valve closed")

def fuel_main_open():
    '''Opens the main fuel release valve - full-flow'''
    global STATES
    if check_2way_open():
        print("Opening the main fuel valve")
        GPIO.output(MAIN_FUEL_PIN, OPEN)
        STATES["VALVES"]["Fuel Main Valve"] = "Open"
        msg.tell("Main fuel valve opened")

def fuel_main_close():
    '''Closes the main fuel release valve'''
    global STATES
    if check_2way_open():
        print("Closing the main fuel valve")
        GPIO.output(MAIN_FUEL_PIN, CLOSE)
        STATES["VALVES"]["Fuel Main Valve"] = "Closed"
        msg.tell("Main fuel valve closed")

def fuel_vent_open():
    '''Opens the fuel vent valve'''
    global STATES
    if check_2way_open():
        print("Opening the fuel vent valve")
        GPIO.output(VENT_FUEL_PIN, OPEN)
        STATES["VALVES"]["Fuel Vent Valve"] = "Open"
        msg.tell("Fuel vent valve opened")

def fuel_vent_close():
    '''Closes the fuel vent valve'''
    global STATES
    if check_2way_open():
        print("Closing the fuel vent valve")
        GPIO.output(VENT_FUEL_PIN, CLOSE)
        STATES["VALVES"]["Fuel Vent Valve"] = "Closed"
        msg.tell("Fuel vent valve closed")


# UNCOMMENT IF ADDING LOX STUFF

# def lox_ten_open():
#     global STATES
#     if check_2way_open:
#         print("Opening the LOX 10 percent valve")
#         GPIO.output(TEN_LOX_PIN, OPEN)
#         STATES["VALVES"]["LOX 10 Percent Pressurant Valve"] = "Open"
#         msg.tell("LOX 10 percent valve opened")

# def lox_ten_close():
#     global STATES
#     if check_2way_open:
#         print("Closing the LOX 10 percent valve")
#         GPIO.output(TEN_LOX_PIN, CLOSE)
#         STATES["VALVES"]["LOX 10 Percent Pressurant Valve"] = "Closed"
#         msg.tell("LOX 10 percent valve closed")

# def lox_press_open():
#     global STATES
#     if check_2way_open:
#         print("Opening the LOX pressurant valve")
#         GPIO.output(PRESS_LOX_PIN, OPEN)
#         STATES["VALVES"]["LOX Pressurant Valve"] = "Open"
#         msg.tell("LOX pressurant valve opened")

# def lox_press_close():
#     global STATES
#     if check_2way_open:
#         print("Closing the LOX pressurant valve")
#         GPIO.output(PRESS_LOX_PIN, CLOSE)
#         STATES["VALVES"]["LOX Pressurant Valve"] = "Closed"
#         msg.tell("LOX pressurant valve closed")

# def lox_main_open():
#     global STATES
#     if check_2way_open:
#         print("Opening the main LOX valve")
#         GPIO.output(MAIN_LOX_PIN, OPEN)
#         STATES["VALVES"]["LOX Main Valve"] = "Open"
#         msg.tell("Main LOX valve opened")

# def lox_main_close():
#     global STATES
#     if check_2way_open:
#         print("Closing the main LOX valve")
#         GPIO.output(MAIN_LOX_PIN, CLOSE)
#         STATES["VALVES"]["LOX Main Valve"] = "Closed"
#         msg.tell("Main LOX valve closed")

# def lox_vent_open():
#     global STATES
#     if check_2way_open:
#         print("Opening the LOX vent valve")
#         GPIO.output(VENT_LOX_PIN, OPEN)
#         STATES["VALVES"]["LOX Vent Valve"] = "Open"
#         msg.tell("LOX vent valve opened")

# def lox_vent_close():
#     global STATES
#     if check_2way_open:
#         print("Closing the LOX vent valve")
#         GPIO.output(VENT_LOX_PIN, CLOSE)
#         STATES["VALVES"]["LOX Vent Valve"] = "Closed"
#         msg.tell("LOX vent valve closed")

def ignitor_on():
    '''Sets the state of the ignitor GPIO pin to "HIGH" - connect to a relay'''
    global STATES
    print("Turning the ignitor pin on")
    GPIO.output(IGNITOR_PIN, GPIO.HIGH)  # Make sure this pin is actually set to "HIGH" for on
    STATES["Ignitor"] = "On"
    msg.tell("Turned the ignitor pin on")

def ignitor_off():
    '''Sets the state of the ignitor GPIO pin to "LOW"'''
    global STATES
    print("Turning the ignitor pin on")
    GPIO.output(IGNITOR_PIN, GPIO.LOW)
    STATES["Ignitor"] = "Off"
    msg.tell("Turned the ignitor pin off")

def a():
    '''Emergency abort - currently runs the "full abort" command'''
    print("USER ABORT")
    full_abort()
    msg.tell("SYSTEM ABORTED VIA USER INPUT")

def sys():
    global STATES
    states_string = json.dumps(STATES)
    print("Printed System States")
    sys = states_string.replace(",", "\n").replace("{", "\n").replace("}", "\n")
    msg.tell(sys)


def hold():
    print("ENTERING A HOLD STATE")
    hold = True
    msg.tell("ENTERING A HOLD STATE")
    while hold == True:
        sys()
        cmd = msg.input("IN HOLD STATE - USER COMMANDS AVAILABLE - ENTER 'yes' TO LEAVE HOLD")
        
        if cmd.upper() == "YES":
            hold = False
            msg.tell("Exiting the hold, moving forward")
        else:
            exe(cmd)

def read_sensors():
    '''Outputs the most recent data point(s) from all sensors'''
    out_string = "Sensor readings at "
    out_string += datetime.now().strftime("%H:%M:%S.%f")[:-3]
    out_string += ':\n'
    for item in sensors.Data:
        data_point = sensors.read(item)
        data_point = f'{data_point:.2f}'
        out_string += str(item) + data_point + '/n'
    msg.tell(out_string)

# ''' 
# ==========================================================================================
# COMPOUND FUNCTIONS AND COMMANDS (INTERDEPENDENT ON THE ABOVE SINGLE FUNCTIONS/ COMMANDS) |
# ==========================================================================================
# '''

def shutdown():
    print("Cleaning the pins of the RPi")
    print("Closing this program")
    if msg.demand("Are you sure you want to shutdown? [yes/no]") == 'yes':
        clean_up()
        msg.tell("Shutting down raspberry pi!")
        os.system('exit')
    else:
        msg.tell("Cancelled the shutdown of the pi")

def fuel_fill():
    print("Entering 'fill fuel' state")
    fuel_main_close()
    fuel_press_close()
    fuel_ten_close()
    fuel_vent_open()
    msg.tell("SYSTEM READY FOR FUEL FILLING - ALL FUEL VALVES CLOSED EXCEPT VENT")

def fill_lox():
    print("Entering LOX fill state")


def ignition():
    if msg.demand("Are you sure you want to start ignition? [yes/no]") == 'yes':
        
        if check_2way_open():
            msg.tell("Ignition beginning: Countdown from 10.")
            for sec in range(10):
                msg.tell("{}".format(10-sec))
                sleep(1)
            fuel_press_open()
            fuel_ten_open()
            ignitor_on()
            sleep(2)
            fuel_main_open()
            
            msg.tell("BOOM")
    else:
        msg.tell("Aborted the ignition procedure")

def reset():
    if msg.demand("Are you sure you want to reset the system? [yes/no]") == 'yes':
        print("RESETTING THE SYSTEM: CLOSING ALL VALVES - TURNING OFF IGNITOR")
        msg.tell("RESETTING THE SYSTEM: CLOSING ALL VALVES - TURNING OFF IGNITOR")
        enable_2way()
        fuel_ten_close()
        fuel_press_close()
        fuel_vent_close()
        fuel_main_close()
        ignitor_off()
        disable_2way()
    else:
        msg.tell("Cancelled the reset of the system")

def engine_abort():  # Ask if we want to open the press valves to depressurize after a hold
    print("ABORTING THE ENGINE SYSTEM")
    fuel_main_close()
    fuel_press_close()
    fuel_ten_close()
    sleep(0.5)
    fuel_vent_open()
    msg.tell("ABORTING THE ENGINE SYSTEM - PRESSURE VALVES CLOSED - MAIN VALVES CLOSED - VENT VALVES OPENED" )

def full_abort():
    print("FULLY ABORTING THE SYSTEM")
    fuel_ten_close()
    fuel_press_close()
    fuel_main_open()
    fuel_vent_open()
    msg.tell("FULLY ABORTING THE SYSTEM - PRESSURE VALVES CLOSED - MAIN VALVES OPENED - VENT VALVES OPENED")

    msg.tell("FULLY ABORTING THE SYSTEM - PRESSURE VALVES CLOSED - ALL MAIN AND VENT VALVES OPENED ")

# def hold_check():
#     hold()


#dictionary of all commands, and number of args
commands = {
    
    "log": [log, 2],
    "calibrate": [calibrate, 1],

    "ping": [ping, 1],
    "help": [help, 1],
    "reboot": [reboot, 1],
    "rr": [rr, 1],

    "led_test": [led_test, 1],
    "clean_up": [clean_up, 1],

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

    # "lox_ten_open": [lox_ten_open, 1],
    # "lox_ten_close": [lox_ten_close, 1],
    # "lox_press_open": [lox_press_open, 1],
    # "lox_press_close": [lox_press_close, 1],

    # "lox_vent_open": [lox_vent_open, 1],
    # "lox_vent_close": [lox_vent_close, 1],
    # "lox_main_open": [lox_main_open, 1],
    # "lox_main_close": [lox_main_close, 1],

    "fuel_fill": [fuel_fill, 1],
    
    "ignition": [ignition, 1],
    "ignitor_on": [ignitor_on, 1],
    "ignitor_off": [ignitor_off, 1],

    "full_abort": [full_abort, 1],
    "engine_abort": [engine_abort, 1],

    "read_sensors": [read_sensors, 1],

    # "pt_simulation": [pt_simulation, 2],

    "a": [a, 1],
    "sys": [sys, 1],
    "reset": [reset, 1],
    "shutdown": [shutdown, 1],
    "hold": [hold, 1]

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

if __name__ == "__main__":
    print("You can only see me if you run commands.py")
    example = engine_abort()
    print(example)