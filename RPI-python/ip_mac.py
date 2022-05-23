import socket
import re, uuid

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8",80))
    ip_address = s.getsockname()[0]
    s.close()
    return ip_address
    
def get_mac():
    mac_address = (":".join(re.findall("..", "%012x" % uuid.getnode())))
    return mac_address
    




