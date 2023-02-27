try:
    import RPi.GPIO as GPIO
except:
    print("Error importing RPi.GPIO. You need to run this with sudo privileges!")
from time import sleep


GPIO.setmode(GPIO.BOARD)

LED_1 = 37
GPIO.setup(LED_1, GPIO.OUT)

while True:
    GPIO.output(LED_1, GPIO.HIGH)
    sleep(1)
    GPIO.output(LED_1, GPIO.LOW)
    sleep(1)

