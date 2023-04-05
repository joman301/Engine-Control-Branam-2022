from ADCDifferentialPi import ADCDifferentialPi
from time import sleep

# A/D Differential Sensor
ADC_ADDR_ONE = 0x68
ADC_ADDR_TWO = 0x6b
ADC_BITRATE = 14
ADC_GAIN = 8

adc = ADCDifferentialPi(ADC_ADDR_ONE, ADC_ADDR_TWO, ADC_BITRATE)
adc.set_pga(ADC_GAIN)

while True:
    print(adc.read_voltage(1))
    sleep(0.1)