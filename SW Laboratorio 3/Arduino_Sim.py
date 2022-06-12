import paho.mqtt.client as PahoMQTT
import time
import json
import uuid
import requests
import random

# Program to simulate HW 3/E03 exercise
# With this, we can simulate a communication between devices without having an arduino physically

# Configuration constants
RESOURCE_CATALOG_ADDRESS = "http://127.0.0.1:8080/"
MSG_BROKER_ADDRESS = "localhost"
BASE_TOPIC_PUB = "tiot/group14/"
BASE_TOPIC_SUB = "tiot/group14/command/"
LOW = 0
HIGH = 1

# LED state
led_state = 0


def on_connect(client_id, userdata, flag, rc):
    print("Connected with result code " + str(rc))


def on_message(client_id, userdata, msg):
    global led_state

    payload = json.loads(msg.payload)
    body = payload["e"][0]
    if not (body["v"] == HIGH or body["v"] == LOW):
        raise Exception("Value received not valid!")

    led_state = body["v"]
    print("LED state passed to " + str(body["v"]))


def main():
    # Define the uuid of the arduino client
    uuid_cl = str(uuid.uuid1())

    # Define the topic used to subscribe and publish
    topic_p = BASE_TOPIC_PUB + uuid_cl
    topic_s = BASE_TOPIC_SUB + uuid_cl

    payload = {
        "bn": "YunGroup14",
        "e": [{
            "n": "temperature",
            "t": "",
            "v": 0.0,
            "u": "celsius"
        }]
    }

    # Get the subscription from the catalog
    req = requests.get(RESOURCE_CATALOG_ADDRESS)
    if req.status_code != 200:
        req.raise_for_status()

    subscription = req.json()

    # Define the device
    new_device = {
        "bn": uuid_cl,
        "e": [{
            "ep": "MQTT",
            "res": ["led"],
            "t": str(time.time())
        }]
    }

    # Define the header of the request
    header = {
        "Content-Type": "application/json"
    }

    # Make public this device
    req = requests.post(subscription["REST"]["device"], headers=header, data=json.dumps(new_device))
    if req.status_code != 200:
        req.raise_for_status()

    # Create the MQTT client
    a_client = PahoMQTT.Client(uuid_cl, True)
    a_client.on_connect = on_connect
    a_client.on_message = on_message
    a_client.connect(MSG_BROKER_ADDRESS)
    a_client.loop_start()
    a_client.subscribe(topic_s, 2)
    a_client.subscribe(subscription["MQTT"]["device"]["topic"] + "/" + uuid_cl, 2)

    while True:
        time.sleep(10)
    # payload["e"][0]["t"] = str(time.time())
    # payload["e"][0]["v"] = float(random.randrange(-273, 500, 3))
    # a_client.publish(topic_p, json.dumps(payload), 2)

    a_client.unsubscribe(topic_s)
    a_client.unsubscribe(subscription["MQTT"]["device"]["topic"] + "/" + uuid_cl)
    a_client.loop_stop()
    a_client.disconnect()


if __name__ == "__main__":
    main()
