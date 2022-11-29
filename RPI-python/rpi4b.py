# adapted from temp_controller_with_thermostats.py
#

import os
import asyncio
import random
import logging

from azure.iot.device.aio import IoTHubDeviceClient
from azure.iot.device.aio import ProvisioningDeviceClient
from azure.iot.device import MethodResponse
from datetime import timedelta, datetime
from azureIot.pnp.pnp_helper import pnp_helper

from sensors.light_intensity import get_light_intensity
from sensors.temperature_humidity import get_temperature_humidity
from sensors.lcd_display import show_display

logging.basicConfig(level=logging.ERROR)

# the interfaces that are pulled in to implement the device.
# User has to know these values as these may change and user can
# choose to implement different interfaces.
senseHat_digital_twin_model_identifier = "dtmi:com:envisioniot:SenseHat;1"
device_info_digital_twin_model_identifier = "dtmi:azure:DeviceManagement:DeviceInformation;1"

# The device "TemperatureController" that is getting implemented using the above interfaces.
# This id can change according to the company the user is from
# and the name user wants to call this Plug and Play device
model_id = "dtmi:com:envisioniot:RPI4b;1"

# the components inside this Plug and Play device.
# there can be multiple components from 1 interface
# component names according to interfaces following pascal case.
device_information_component_name = "deviceInformation"
senseHat_1_component_name = "senseHat1"
serial_number = "some_serial_number"
#####################################################
# COMMAND HANDLERS : User will define these handlers
# depending on what commands the component defines

async def reboot_handler(values):
    if values:
        print("Rebooting after delay of {delay} secs".format(delay=values))
    print("Done rebooting")


async def display_msg_handler(values):
    if values:
        print(
            "Will display {msg} on the LED matrix".format(
                msg=values
            )
        )
        show_display(values)
    print("Done displaying")


# END COMMAND HANDLERS
#####################################################


#####################################################
# TELEMETRY TASKS


async def send_telemetry_from_rpi4b(device_client, telemetry_msg, component_name=None):
    msg = pnp_helper.create_telemetry(telemetry_msg, component_name)
    await device_client.send_message(msg)
    print("Sent message")
    print(msg)
    await asyncio.sleep(5)


#####################################################
# COMMAND TASKS


async def execute_command_listener(
    device_client,
    component_name=None,
    method_name=None,
    user_command_handler=None,
    create_user_response_handler=None,
):
    """
    Coroutine for executing listeners. These will listen for command requests.
    They will take in a user provided handler and call the user provided handler
    according to the command request received.
    :param device_client: The device client
    :param component_name: The name of the device like "sensor"
    :param method_name: (optional) The specific method name to listen for. Eg could be "blink", "turnon" etc.
    If not provided the listener will listen for all methods.
    :param user_command_handler: (optional) The user provided handler that needs to be executed after receiving "command requests".
    If not provided nothing will be executed on receiving command.
    :param create_user_response_handler: (optional) The user provided handler that will create a response.
    If not provided a generic response will be created.
    :return:
    """
    while True:
        if component_name and method_name:
            command_name = component_name + "*" + method_name
        elif method_name:
            command_name = method_name
        else:
            command_name = None

        command_request = await device_client.receive_method_request(command_name)
        print("Command request received with payload")
        values = command_request.payload
        print(values)

        if user_command_handler:
            await user_command_handler(values)
        else:
            print("No handler provided to execute")

        (response_status, response_payload) = pnp_helper.create_response_payload_with_status(
            command_request, method_name, create_user_response=create_user_response_handler
        )

        command_response = MethodResponse.create_from_method_request(
            command_request, response_status, response_payload
        )

        try:
            await device_client.send_method_response(command_response)
        except Exception:
            print("responding to the {command} command failed".format(command=method_name))


#####################################################
# PROPERTY TASKS


async def execute_property_listener(device_client):
    while True:
        patch = await device_client.receive_twin_desired_properties_patch()  # blocking call
        print(patch)
        properties_dict = pnp_helper.create_reported_properties_from_desired(patch)

        await device_client.patch_twin_reported_properties(properties_dict)


#####################################################
# An # END KEYBOARD INPUT LISTENER to quit application


def stdin_listener():
    """
    Listener for quitting the sample
    """
    while True:
        selection = input("Press Q to quit\n")
        if selection == "Q" or selection == "q":
            print("Quitting...")
            break


# END KEYBOARD INPUT LISTENER
#####################################################


#####################################################
# MAIN STARTS
async def provision_device(provisioning_host, id_scope, registration_id, symmetric_key, model_id):
    provisioning_device_client = ProvisioningDeviceClient.create_from_symmetric_key(
        provisioning_host=provisioning_host,
        registration_id=registration_id,
        id_scope=id_scope,
        symmetric_key=symmetric_key,
    )

    provisioning_device_client.provisioning_payload = {"modelId": model_id}
    return await provisioning_device_client.register()


async def main():
    switch = os.getenv("IOTHUB_DEVICE_SECURITY_TYPE")
    if switch == "DPS":
        provisioning_host = (
            os.getenv("IOTHUB_DEVICE_DPS_ENDPOINT")
            if os.getenv("IOTHUB_DEVICE_DPS_ENDPOINT")
            else "global.azure-devices-provisioning.net"
        )
        id_scope = os.getenv("IOTHUB_DEVICE_DPS_ID_SCOPE")
        registration_id = os.getenv("IOTHUB_DEVICE_DPS_DEVICE_ID")
        symmetric_key = os.getenv("IOTHUB_DEVICE_DPS_DEVICE_KEY")

        registration_result = await provision_device(
            provisioning_host, id_scope, registration_id, symmetric_key, model_id
        )

        if registration_result.status == "assigned":
            print("Device was assigned")
            print(registration_result.registration_state.assigned_hub)
            print(registration_result.registration_state.device_id)
            device_client = IoTHubDeviceClient.create_from_symmetric_key(
                symmetric_key=symmetric_key,
                hostname=registration_result.registration_state.assigned_hub,
                device_id=registration_result.registration_state.device_id,
                product_info=model_id,
            )
        else:
            raise RuntimeError(
                "Could not provision device. Aborting Plug and Play device connection."
            )

    elif switch == "connectionString":
        conn_str = os.getenv("IOTHUB_DEVICE_CONNECTION_STRING")
        print("Connecting using Connection String " + conn_str)
        device_client = IoTHubDeviceClient.create_from_connection_string(
            conn_str, product_info=model_id
        )
    else:
        raise RuntimeError(
            "At least one choice needs to be made for complete functioning of this sample."
        )

    # Connect the client.
    await device_client.connect()

    ################################################
    # Update readable properties from various components

    properties_root = pnp_helper.create_reported_properties(serialNumber=serial_number)
    properties_senseHat1 = pnp_helper.create_reported_properties(
        senseHat_1_component_name,
    )
    properties_device_info = pnp_helper.create_reported_properties(
        device_information_component_name,
        swVersion="5.5",
        manufacturer="Contoso Device Corporation",
        model="Contoso 4762B-turbo",
        osName="Mac Os",
        processorArchitecture="x86-64",
        processorManufacturer="Intel",
        totalStorage=1024,
        totalMemory=32,
    )

    property_updates = asyncio.gather(
        device_client.patch_twin_reported_properties(properties_root),
        device_client.patch_twin_reported_properties(properties_senseHat1),
        device_client.patch_twin_reported_properties(properties_device_info),
    )

    ################################################
    # Get all the listeners running
    print("Listening for command requests and property updates")

    listeners = asyncio.gather(
        execute_command_listener(
            device_client, method_name="reboot", user_command_handler=reboot_handler
        ),
        execute_command_listener(
            device_client,
            senseHat_1_component_name,
            method_name="displayMessage",
            user_command_handler=display_msg_handler
        ),
        execute_property_listener(device_client),
    )

    ################################################
    # Function to send telemetry every 8 seconds

    async def send_telemetry():
        print("Sending telemetry from various components")

        while True:
            temperature, humidity = get_temperature_humidity()
            light_intensity = get_light_intensity()
            senseHat1_msg = {"temperature": temperature, "humidity": humidity, "brightness": light_intensity}
            await send_telemetry_from_temp_controller(
                device_client, senseHat1_msg, senseHat_1_component_name
            )

            memory_usage = round(psutil.virtual_memory().used/1024)
            workingset_msg = {"workingSet": memory_usage}
            await send_telemetry_from_temp_controller(device_client, workingset_msg)

    send_telemetry_task = asyncio.ensure_future(send_telemetry())

    # Run the stdin listener in the event loop
    loop = asyncio.get_running_loop()
    user_finished = loop.run_in_executor(None, stdin_listener)
    # # Wait for user to indicate they are done listening for method calls
    await user_finished

    if not listeners.done():
        listeners.set_result("DONE")

    if not property_updates.done():
        property_updates.set_result("DONE")

    listeners.cancel()
    property_updates.cancel()

    send_telemetry_task.cancel()

    # Finally, shut down the client
    await device_client.shutdown()


#####################################################
# EXECUTE MAIN

if __name__ == "__main__":
    asyncio.run(main())

    # If using Python 3.6 use the following code instead of asyncio.run(main()):
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(main())
    # loop.close()
