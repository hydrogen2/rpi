import enos
from enos.core.MqttClient import MqttClient
import time
from datetime import datetime

import psutil

from sensors.light_intensity import get_light_intensity
from sensors.temperature_humidity import get_temperature_humidity
from sensors.lcd_display import show_display
from post_measurepoint import post_measurepoint
from post_attributes import update_attribute

def connect(response):
    client = MqttClient(response["murl"],
                        response["pk"],
                        response["dk"],
                        response["ds"])
    
    client.connect()
    print()
    print("Connecting Client")
    
    update_attribute(client)
    
    try:
        while True:
            # Get temperature and humidity function
            temperature, humidity = get_temperature_humidity()            
            post_measurepoint(client, "temperature", temperature)
            post_measurepoint(client, "humidity", humidity)  
            
            # Get light intensity function
            light_intensity = get_light_intensity()          
            post_measurepoint(client, "lightValue", light_intensity)           
            
            #CPU Usage
            cpu_usage = psutil.cpu_percent()
            print("CPU Load", cpu_usage, "%")
            post_measurepoint(client, "cpuUsage", cpu_usage)
            
            #Memory Usage
            memory_usage = round(psutil.virtual_memory().used/1024/1024)
            print("Memory Usage", memory_usage, "mb")
            post_measurepoint(client, "memoryUsage", memory_usage)
            
            #Memory Percentage
            memory_percentage = psutil.virtual_memory().percent
            print("Memory Percentage", memory_percentage, "%")
            post_measurepoint(client, "memoryPct", memory_percentage)
            
            print("Post MeasurementPoint on IoTHub at", datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
            print(f"{'-'*50}")
            
            # Show display on LCD Function
            show_display(temperature, light_intensity, humidity)
            time.sleep(10)
            
    except KeyboardInterrupt:
        print("\nKeyboard interrupt called")
        client.close()
        time.sleep(1)
        print("Client Closed")


