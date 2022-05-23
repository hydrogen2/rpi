import enos
from enos.core.MqttClient import MqttClient
from enos.message.upstream.tsl.MeasurepointPostRequest import MeasurepointPostRequest

import time
from datetime import datetime
import hashlib
import os
from requests.models import PreparedRequest
import requests

time_now = str(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
timestamp = round(time.time()*1000.0)
dps_url = "http://iot-dps2-ppe1.envisioniot.com/dev/bootstrap"
deviceId = "rpiDeviceId_" + time_now #"rpiDeviceId_18/05/2022 16:19:16"
groupId= "ES4F5N"
groupsecret = "ZtqTOjHEvc"


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
            "deviceName": {"defaultValue": "RPI_" + time_now},
            "timezone": "+08:00"}

    response = requests.post(dps_url, json=body, headers=header)
    return response.json()





