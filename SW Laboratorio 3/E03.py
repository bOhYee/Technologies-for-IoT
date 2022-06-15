import paho.mqtt.client as PahoMQTT
import uuid
import requests
import time
import json

# Configuration constants
RESOURCE_CATALOG_ADDRESS = "http://127.0.0.1:8080/"
MSG_BROKER_ADDRESS = "localhost"
BASE_TOPIC_PUB = "tiot/group14/command/"

# Used to check that the connection to the MQTT Broker
isConnected = False


def on_connect(id, userdata, flag, rc):
    global isConnected

    print("Connected with result code " + str(rc))
    isConnected = True


def main():
    # Define the uuid of the client
    uuid_cl = str(uuid.uuid1())

    req = requests.get(RESOURCE_CATALOG_ADDRESS)
    if req.status_code != 200:
        req.raise_for_status()

    # Convert the received payload from JSON to dictionary
    subscription = req.json()

    # Define the service
    new_service = {
        "bn" : uuid_cl,
        "e":[{
            "des": "Turn on/off LED",
            "ep" : "LedService",
            "t" : str(time.time())
        }]
    }

    # Define the header of the request
    header = {
        "Content-Type" : "application/json"
    }

    # Make public this service
    req = requests.post(subscription["REST"]["service"], headers=header, data=json.dumps(new_service))
    if req.status_code != 200:
        req.raise_for_status()

    # Request all devices registered to find those who publish the state of the LEDs
    req = requests.get(RESOURCE_CATALOG_ADDRESS + "devices/")
    if req.status_code != 200:
        req.raise_for_status()

    # Filter the list of devices through removing the ones who do not have a LED
    devices = json.loads(req.text)
    for dev in devices:
        if "led" not in dev["e"][0]["res"] :
            devices.remove(dev)

    # Create the MQTT client
    c = PahoMQTT.Client(uuid_cl, True)
    c.on_connect = on_connect
    c.connect(MSG_BROKER_ADDRESS)
    c.loop_start()

    while not isConnected:
        pass

    # Define the structure of the payload for the MQTT packages
    payload = {
        "bn": "YunGroup14",
        "e": [{
            "n": "led",
            "t": 0,
            "v": 0,
            "u": "null"
        }]
    }

    # Init value for the cycle
    # All devices will have the same LED value every cycle
    led_value = 0

    while True:
        for dev in devices:
            # Recover the name and body of the device structure
            name = dev["bn"]
            dev_body = dev["e"][0]
            index_endpoint = dev_body["res"].index("led")
            endpoint = dev["ep"][index_endpoint]

            # Create the topic with the uuid
            topic = BASE_TOPIC_PUB + str(name) + "/" + str(endpoint)

            payload["bn"] = name
            payload["e"][0]["v"] = led_value
            c.publish(topic, json.dumps(payload), 2)

        # Create the package to send
        if led_value == 0:
            led_value = 1
        else:
            led_value = 0

        # Sleep for 15 seconds
        time.sleep(15)

    c.loop_stop()
    c.disconnect()


if __name__ == "__main__":
    main()
