import enos
from enos.core.MqttClient import MqttClient
from enos.message.upstream.tsl.MeasurepointPostRequest import MeasurepointPostRequest

import time
from datetime import datetime
import hashlib
import os
from requests.models import PreparedRequest
import requests

timestamp = round(time.time()*1000.0)
dps_url = "http://iot-dps2-ppe1.envisioniot.com/dev/bootstrap"
deviceId = "RPIDeviceID" #"rpiDeviceId_" + time_now #"RPIDeviceId"
groupId= "WBCKBX" 
groupsecret = "Yfc43wGNHn" 


def register_dps():
    dpsSign = "sn" + deviceId + "timestamp" + str(timestamp) + groupsecret
    dpsSign_encode = dpsSign.encode()
    dpsSign_sha256 = hashlib.sha256(dpsSign_encode)
    sign = dpsSign_sha256.hexdigest()

    header = {"Content-Type": "application/json"}

    body = {"deviceId": deviceId,
            "groupId": groupId,
            "dpsSignMethod" : "sha256",
            "dpsSignTimestamp": timestamp,
            "dpsSign": sign,
            "deviceName": {"defaultValue": "RPI"}, #"RPI_" + time_now
            "timezone": "+08:00"}

    response = requests.post(dps_url, json=body, headers=header)
    return response.json()





