from rpi_dps2 import register_dps
from rpi_connect import connect

if __name__ == "__main__":
    print("Self-registering device on DPS")
    response = register_dps()
    print("Device registered")
    
    connect(response)
    
    



