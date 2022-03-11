import threading

import commands as cmd
import message as msg

__author__ = "Aidan Cantu"

def execute():
    '''Thread which executes all commands'''
    while(True):
        user_command = msg.get_cmd()
        user_command = cmd.parse(user_command)
        if len(user_command) == 0:
            msg.cmd_ready()
            continue
        if user_command[0] == "stop": # if user_command[0].lower() == "stop":  (Taking out the lowercase function, this is backup)
            msg.stop()
            for x in threading.enumerate():
                if x.getName()=="command":
                    x.join()
            msg.tell("all commands exited")
            msg.resume()
            msg.cmd_ready()
        else:
            x = threading.Thread(name='command', target=cmd.exe, args = [user_command])
            x.start()

def main():

    # Begin listening for and sending requests over socket
    sender = threading.Thread(name='sender', target=msg.sender)
    sender.start()

    receiver = threading.Thread(name='receiver', target=msg.receiver)
    receiver.start()

    logger = threading.Thread(name='logger', target=msg.send_logs)
    logger.start()

    dummyyy = threading.Thread(name='dummyyy', target=msg.send_dummy_data)
    dummyyy.start()

    executer = threading.Thread(name='executer', target=execute)
    executer.start()
            

if __name__ == "__main__":
    main()