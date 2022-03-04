'''Contains most commands that the user
can execute'''
from enum import Enum
import message as msg
import time
import os

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

#Rotates specified motor by specified number of steps
def rotate(motor, amount_deg):
    global LOX_MOTOR_POS_DEG, KER_MOTOR_POS_DEG

    motor_rotation_deg = amount_deg * GEAR_RATIO
    deg_per_step = 1.8
    step_count = int(motor_rotation_deg / deg_per_step)

    if(abs(amount_deg) >= 90):
        user_message = "Type \'yes\' to confirm %s degrees on device %s" % (amount_deg, Dev(motor).name)
        if msg.demand(user_message) != 'yes':
            msg.tell("Operation Cancelled")
            return 4

    msg.tell(("Rotating %s Motor %s degrees") % (Dev(motor).name, amount_deg))
    msg.cmd_ready()
'''
    if step_count > 0:
        dir = stepper.FORWARD
    else:
        dir = stepper.BACKWARD
        step_count = step_count * -1
        deg_per_step = deg_per_step *-1
    
    if motor == Dev.LOX_MOTOR:
        for i in range(step_count):
            if msg.is_stopped():
                msg.tell("Stopping LOX_MOTOR at position %.2f degrees" % (LOX_MOTOR_POS_DEG/GEAR_RATIO))
                break
            else:
                motors.stepper1.onestep(direction = dir, style=stepper.DOUBLE)
                LOX_MOTOR_POS_DEG += deg_per_step
                time.sleep(0.0001)
        motors.stepper1.release()
        msg.tell("Successfully set LOX_MOTOR position to %.2f degrees" % (LOX_MOTOR_POS_DEG/GEAR_RATIO))

    elif motor == Dev.KER_MOTOR:
        for i in range(step_count):
            if msg.is_stopped():
                msg.tell("Stopping KER_MOTOR at position %.2f degrees" % (KER_MOTOR_POS_DEG/GEAR_RATIO))
                break
            else:
                motors.stepper2.onestep(direction = dir, style=stepper.DOUBLE)
                KER_MOTOR_POS_DEG += deg_per_step
                time.sleep(0.0001)
        motors.stepper2.release()
        msg.tell("Successfully set KER_MOTOR position to %.2f degrees" % (KER_MOTOR_POS_DEG/GEAR_RATIO))
'''
def lox_motor_pos():
    msg.tell("LOX Motor rotated %.2f degrees" % (LOX_MOTOR_POS_DEG/GEAR_RATIO))

def ker_motor_pos():
    msg.tell("KEROSENE Motor rotated %.2f degrees" % (KER_MOTOR_POS_DEG/GEAR_RATIO))

def lox_is():
    rotate(Dev.LOX_MOTOR,10)

def lox_ds():
    rotate(Dev.LOX_MOTOR,-10)

def ker_is():
    rotate(Dev.KER_MOTOR,10)

def ker_ds():
    rotate(Dev.KER_MOTOR,-10)

def lox_inc(n):
    rotate(Dev.LOX_MOTOR,n)

def lox_dec(n):
    rotate(Dev.LOX_MOTOR,-1*n)

def ker_inc(n):
    rotate(Dev.KER_MOTOR,n)

def ker_dec(n):
    rotate(Dev.KER_MOTOR,-1*n)

def help():
    s = '''
    lox_is: runs 10 degrees forward on lox
    lox_ds: runs 10 degrees backward on lox
    ker_is: runs 10 degrees forward on kerosene
    ker_ds: runs 10 degrees backward on kerosene

    lox_inc [n]: runs n degrees forward on lox
    lox_dec [n]: runs n degrees backward on lox
    ker_inc [n]: runs n degrees forward on kerosene
    ker_dec [n]: runs n degrees backward on kerosene

    lox_motor_pos: return angular offset of lox motor
    ker_motor_pos: return angular offset of ker motor

    log [T/F]: start or stop logging sensor data
    calibrate: sets y-intercept of all sensors to 0

    ping: test connection
    help: print help menu
    rr: repeat last command
    reboot: restart server
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

#dictionary of all commands, and number of args
commands = {
    "lox_is": [lox_is, 1],
    "lox_ds": [lox_ds, 1],
    "ker_is": [ker_is, 1],
    "ker_ds": [ker_ds, 1],

    "lox_inc": [lox_inc, 2],
    "lox_dec": [lox_dec, 2],
    "ker_inc": [ker_inc, 2],
    "ker_dec": [ker_dec, 2],

    "lox_motor_pos": [lox_motor_pos, 1],
    "ker_motor_pos": [ker_motor_pos, 1],

    "log": [log, 2],
    "calibrate": [calibrate, 1],

    "ping": [ping, 1],
    "help": [help, 1],
    "reboot": [reboot, 1],
    "rr": [rr, 1]
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