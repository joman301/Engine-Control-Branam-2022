import RPi.GPIO as GPIO
from time import sleep

GPIO.setmode(GPIO.BOARD)

LED_1 = 36
LED_2 = 37
LED_3 = 35
LED_4 = 33

GPIO.setup(LED_1, GPIO.OUT)
GPIO.setup(LED_2, GPIO.OUT)
GPIO.setup(LED_3, GPIO.OUT)
GPIO.setup(LED_4, GPIO.OUT)

LEDs = [LED_1, LED_2, LED_3, LED_4]

while True:
    for LED in LEDs:
        GPIO.output(LED, GPIO.HIGH)
        sleep(1)
        GPIO.output(LED, GPIO.LOW)
        sleep(1)
        
