from grove.grove_light_sensor_v1_2 import GroveLightSensor

light_sensor = GroveLightSensor(0) #Connect to port A0

def get_light_intensity():
    light_intensity = light_sensor.light
    print("Light Intensity", light_intensity)
    return light_intensity
    

