from grove.display.jhd1802 import JHD1802

lcd = JHD1802() #I2C Port

def show_display(temperature, light_intensity, humidity):
    lcd.clear()
    
    lcd.setCursor(0, 0)
    lcd.write("Temp:{}".format(temperature))
                    
    lcd.setCursor(0, 7)
    lcd.write("Light:{}".format(light_intensity))
            
    lcd.setCursor(1, 0)
    lcd.write("Humidity:{}".format(humidity))

    
