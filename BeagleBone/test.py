import Adafruit_BBIO.GPIO as GPIO
import Adafruit_BBIO.ADC as ADC
from time import sleep

ADC.setup()
while True:
    value = ADC.read("P9_40")  # Can also use "AIN1"
    print(value)
    value_converted = value * 1.8
    print(value_converted)
    sleep(0.1)
