from pressureCalibrate import PressureConverter
from ExpanderPi import ADC

# Pressure reading function
def read_pressure():
    adc = ADC()
    converter = PressureConverter()

    # Example: Read voltage from channel 2
    voltage = adc.read_adc_voltage(2, 0)
    pressure = converter(voltage)

    return {"sensor": "PS-001","name":"WaterPressure", "value": pressure}
