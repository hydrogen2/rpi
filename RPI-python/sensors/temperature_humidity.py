import seeed_dht

temp_humi_sensor = seeed_dht.DHT("11", 16) #Connect to port D16

def get_temperature_humidity():
    humidity, temperature = temp_humi_sensor.read()
    print("Temperature:", temperature)
    print("Humidity:", humidity)
    return temperature, humidity
    


