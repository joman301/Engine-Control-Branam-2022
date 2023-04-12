from ADCDifferentialPi import ADCDifferentialPi
from time import sleep

# A/D Differential Sensor
ADC_ADDR_ONE = 0x68
ADC_ADDR_TWO = 0x69
ADC_BITRATE = 14
ADC_GAIN = 8

adc = ADCDifferentialPi(ADC_ADDR_ONE, ADC_ADDR_TWO, ADC_BITRATE)
adc.set_pga(ADC_GAIN)

sleep(1)
while True:
    print("PT 5: " + str(adc.read_voltage(5)))
    print("PT 6: " + str(adc.read_voltage(6)))
    print("PT 7: " + str(adc.read_voltage(7)))
    print("PT 8: " + str(adc.read_voltage(8)) + "\n")
    sleep(0.1)