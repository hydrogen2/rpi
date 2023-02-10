import time

from rpi_dps import register_dps
from rpi_connect import connect
from sensors.lcd_display import show_msg

dpsUrl = "https://iot-dps2-ppe1.envisioniot.com/dev/bootstrap"
groupId = "D4KJCC"
groupSecret = "D8QQlxh5zV"


def connected_to_internet(url='http://www.google.com/', timeout=5):
    try:
        _ = requests.head(url, timeout=timeout)
        return True
    except requests.ConnectionError:
        print("No internet connection available.")
    return False


def check_success_register(response):
    if "ds" in response:
        return True
    else:
        return False


if __name__ == "__main__":

    try:
        while not connected_to_internet():
            show_msg("Waiting for WiFi")

        show_msg("Registering Device to: " + groupId)
        response = register_dps(dpsUrl, groupId, groupSecret)
        while not check_success_register(response):
            show_msg("Fail to get Device")
            time.sleep(5)
            response = register_dps(dpsUrl, groupId, groupSecret)

        show_msg("Device registered")

        connect(response)
    except:
        show_msg("Error")
