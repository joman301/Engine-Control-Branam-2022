import Adafruit_BBIO.GPIO as GPIO
import Adafruit_BBIO.ADC as ADC
from time import sleep
from ADCDifferentialPi import ADCDifferentialPi

ADC.setup()

ADC_ADDR_ONE = 0x68
ADC_ADDR_TWO = 0x6b
ADC_BITRATE = 14
ADC_GAIN = 8

adc = ADCDifferentialPi(ADC_ADDR_ONE, ADC_ADDR_TWO, ADC_BITRATE)
adc.set_pga(ADC_GAIN)

while True:
    '''
    value = ADC.read("P9_40")  # Can also use "AIN1"
    value_celcius = ((value * 1.835 * 2) - 1.25) / 0.005
    print(value_celcius)
    value_fahrenherit = value_celcius * (9/5) + 32
    sleep(0.1)
    '''
    value = adc.read_voltage(1)
    print(value)
    sleep(0.1)
