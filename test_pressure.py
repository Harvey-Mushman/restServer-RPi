# import time as t
# import smbus
# import sys

# DEVICE_BUS = 1
# DEVICE_ADDR = 0x10
# bus = smbus.SMBus(DEVICE_BUS)

# while True:
#     try:
#         for i in range(1,5):
#             bus.write_byte_data(DEVICE_ADDR, i, 0xFF)
#             t.sleep(1)
#             bus.write_byte_data(DEVICE_ADDR, i, 0x00)
#             t.sleep(1) 
#     except KeyboardInterrupt as e:
#         print("Quit the Loop")+
#         sys.exit()

import time
from ExpanderPi import ADC, RTC, DAC

# from thermistorCalibrate import volt2temp
from pressureCalibrate import PressureConverter

dac = DAC()
adc = ADC()
rtc = RTC()

rtc.set_date("2012-04-23T12:32:11")
rtc.set_frequency(3)
rtc.enable_output()

pressure_converter = PressureConverter()

while (True):
  # Vin = 4.096V
  Vout = adc.read_adc_voltage(2,0)
 
  print(Vout, pressure_converter(Vout))
  # time.sleep(1)
  time.sleep(60)
