import paho.mqtt.client as PahoMQTT
import uuid
import requests
import time

# Configuration constants
RESOURCE_CATALOG_ADDRESS = "http://127.0.0.1:8080/"
MSG_BROKER_ADDRESS = "localhost"

def main():
    req = requests.get(RESOURCE_CATALOG_ADDRESS)
    if req.status_code != 200:
        req.raise_for_status()

    # Convert the received payload from JSON to dictionary
    subscription = req.json()

    # Define the service
    new_service = {
        "uuid" : str(uuid.uuid1()),
        "ep" : "MQTT",
        "res" : [],
        "t" : str(time.time())
    }

    # Define the header of the request
    header = {
        "Content-Type" = "application/json"
    }

    # Make public this service
    req = requests.post(subscription["REST"]["service"], headers=header, data=json.dumps(new_service))
    if req.status_code != 200:
        req.raise_for_status()

    # Request all devices registered to find those who publish the state of the LEDs
    req = requests.get(RESOURCE_CATALOG_ADDRESS + "devices/")
    if req.status_code != 200:
        req.raise_for_status()

    devices = json.loads(req.text)
    for dev in devices:
        if "led" not in dev["res"] :
            devices.remove(dev)


    c = PahoMQTT.Client("Client_E02_G14")
    c.on_connect = on_connect
    c.on_message = on_message
    c.connect(MSG_BROKER_ADDRESS)
    c.loop_start()



    c.loop_stop()
    c.disconnect()

if __name__ == "__main__":
    main()
