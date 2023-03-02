import RPi.GPIO as GPIO

class Valve:
    def __init__(self, name, pin, valve_type, initial_state):
        self.name = name
        self.pin = pin
        self.type = valve_type
        self.initial = initial_state

        self.input = GPIO.IN
        self.output = GPIO.OUT
        self.ball_open = GPIO.HIGH
        self.ball_close = GPIO.LOW

        self.state = self.initial

        if valve_type.upper() == "BALL":
            self.setup_ball()
        elif valve_type.upper() == "NEEDLE":
            self.setup_needle()
        else:
            raise TypeError("Only 'Ball' or 'Needle' is allowed for valve types")

    
    def setup_ball(self):
        GPIO.setup(self.pin, self.output)

        if self.initial.upper() == "OPEN":
            self.action = self.open
        elif self.initial.upper() == "CLOSED":
            self.state = self.close
        else:
            print("You misentered something for " + self.name + "'s initial state")

    
    def setup_needle(self):
        GPIO.setup(self.pin, self.output)
        print("I will setup the needle valve!")


    def open(self, percent=None):
        if self.type.upper() == "BALL":
            GPIO.output(self.pin, self.ball_open)

    
    def close(self):
        if self.type.upper() == "BALL":
            GPIO.output(self.pin, self.ball_close)


    def cleanup(self):
        GPIO.cleanup()


class Sensor:
    def __init__(self, name, pins, sensor_type):
        self.name = name
        self.pins = pins
        self.type = sensor_type
        self.state = "Not reading"
    


if __name__ == "__main__":
    example = Valve("main_fuel", 1, "ball", "closed")