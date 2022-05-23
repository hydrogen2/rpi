from enos.message.upstream.tsl.AttributeUpdateRequest import AttributeUpdateRequest
from ip_mac import get_ip, get_mac

def update_attribute(client):
    ip_attribute = AttributeUpdateRequest.builder().add_attribute("ipAddr", get_ip()).build()
    client.publish(ip_attribute)
    mac_attribute = AttributeUpdateRequest.builder().add_attribute("macAddr", get_mac()).build()
    client.publish(mac_attribute)
    longitude_attribute = AttributeUpdateRequest.builder().add_attribute("longitude", 103.851959).build()
    client.publish(longitude_attribute)
    latitude_attribute = AttributeUpdateRequest.builder().add_attribute("latitude", 1.290270).build()
    client.publish(latitude_attribute)
    print("Attributes Uploaded")
    print()




