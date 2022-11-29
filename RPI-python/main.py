from rpi_dps import register_dps
from rpi_connect import connect
from sensors.lcd_display import show_msg

dpsUrl = "https://iot-dps2-ppe1.envisioniot.com/dev/bootstrap"
groupId = "WBCKBX"
groupSecret = "Yfc43wGNHn"

def connected_to_internet(url='http://www.google.com/', timeout=5):
    try:
        _ = requests.head(url, timeout=timeout)
        return True
    except requests.ConnectionError:
        print("No internet connection available.")
    return False

if __name__ == "__main__":

    try:
        while connected_to_internet() == False:
            show_msg("Waiting for WiFi")

        show_msg("Registering Device to: "+groupId)
        response = register_dps(dpsUrl, groupId, groupSecret)
        show_msg("Device registered")

        connect(response)
    except:
        show_msg("Error")



