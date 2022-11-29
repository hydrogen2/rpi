import enos
from enos.core.MqttClient import MqttClient
from enos.message.upstream.tsl.MeasurepointPostRequest import MeasurepointPostRequest

import time
from datetime import datetime
import hashlib
import os
from requests.models import PreparedRequest
import requests

def register_dps(dpsUrl, groupId, groupSecret):
    timestamp = round(time.time()*1000.0)
    deviceId = "rpiDeviceId_" + str(timestamp)

    dpsSign = "sn" + deviceId + "timestamp" + str(timestamp) + groupSecret
    dpsSign_encode = dpsSign.encode()
    dpsSign_sha256 = hashlib.sha256(dpsSign_encode)
    sign = dpsSign_sha256.hexdigest()

    header = {"Content-Type": "application/json"}

    body = {"deviceId": deviceId,
            "groupId": groupId,
            "dpsSignMethod" : "sha256",
            "dpsSignTimestamp": timestamp,
            "dpsSign": sign,
            "deviceName": {"defaultValue": deviceId},
            "timezone": "+08:00"}

    response = requests.post(dpsUrl, json=body, headers=header)
    return response.json()





