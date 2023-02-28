import json

def exe(user_command):
    user_method = user_command[0]
    user_args = user_command[1:]


def open(valve, percent = None):
    valve.open(percent)
    valve.state = "Open"


def close(valve, percent = None):
    valve.close(percent)
    valve.state = "Closed"


def sys(*args):
    print_me = {}

    for dict in args:
        if list(dict.keys()[0]).upper() == "VALVES":
            for valve in dict:
                print_me["Valves"][valve.name] = valve.state

        elif list(dict.keys()[0]).upper() == "SENSORS":
            for sensor in dict:
                print_me["Sensors"][sensor.name] = sensor.state
    
    states_string = json.dumps(print_me)
    print("Printed System States")
    print(states_string.replace(",", "\n")) #msg.tell
        
