def exe(user_command):
    user_method = user_command[0]
    user_args = user_command[1:]


def open(valve, percent = None):
    valve.open(percent)
    valve.state = "Open"


def close(valve, percent = None):
    valve.close(percent)
    valve.state = "Closed"

