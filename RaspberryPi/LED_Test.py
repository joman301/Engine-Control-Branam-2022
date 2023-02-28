# try:
#     import RPi.GPIO as GPIO
# except:
#     print("Error importing RPi.GPIO. You need to run this with sudo privileges!")
from time import sleep
import yaml
from classes import *
from test_commands import *


# GPIO.setmode(GPIO.BOARD)

# LED_1 = 37
# GPIO.setup(LED_1, GPIO.OUT)

with open('setup.yaml', 'r') as file:
    raw_dict = yaml.safe_load(file)

valves = {}
for list_entry in raw_dict["valves"]:
    valve_name = list(list_entry.keys())[0].upper()
    valves[valve_name] = Valve(valve_name, list_entry[valve_name]["pin"], list_entry[valve_name]["type"], list_entry[valve_name]["init"])

sensors = {}
for list_entry in raw_dict["sensors"]:
    sensor_name = list(list_entry.keys())[0].upper()
    sensors[sensor_name] = Valve(sensor_name, list_entry[valve_name]["pin"], list_entry[valve_name]["type"], list_entry[valve_name]["init"])
print(valves)