import paho.mqtt.client as PahoMQTT
import time
import json
import uuid
import requests

# Configuration constants
RESOURCE_CATALOG_ADDRESS = "http://127.0.0.1:8080/"
MSG_BROKER_ADDRESS = "localhost"
BASE_TOPIC_PUB = "tiot/group14/"
BASE_TOPIC_SUB = "tiot/group14/command/"

def on_connect(client_id, userdata, flag, rc):
    print("Connected with result code "+ str(rc))

def on_message(client_id, userdata, msg):
    print("Received message: '" + str(msg.payload) + "' regarding topic '" + str(msg.topic) + "'")

def main():
    # Define the uuid of the arduino client
    uuid_cl = str(uuid.uuid1())
    # Define the topic used to subscribe and publish
    topic_p = BASE_TOPIC_PUB + uuid_cl
    topic_s = BASE_TOPIC_SUB + uuid_cl

    payload = {
        "bn" : "YunGroup14",
        "e": {
            "n" : "temperature",
            "t" : 0,
            "v" : 0,
            "u" : "celsius"
        }
    }

    # Get the subscription from the catalog
    req = requests.get(RESOURCE_CATALOG_ADDRESS)
    if req.status_code != 200:
        req.raise_for_status()

    subscription = req.json()

    # Define the device
    new_service = {
        "uuid" : uuid_cl,
        "ep" : "MQTT",
        "res" : [],
        "t" : str(time.time())
    }

    # Define the header of the request
    header = {
        "Content-Type" = "application/json"
    }

    # Make public this device
    req = requests.post(subscription["REST"]["device"], headers=header, data=json.dumps(new_service))
    if req.status_code != 200:
        req.raise_for_status()

    # Create the MQTT client
    a_client = PahoMQTT.Client("Yun_Group14", False)
    a_client.on_connect = on_connect
    a_client.on_message = on_message
    a_client.connect(MSG_BROKER_ADDRESS)
    a_client.loop_start()
    a_client.subscribe(topic_s, 2)

    while True:
        time.sleep(10)
        payload["e"]["t"] = time.time()
        payload["e"]["v"] = float(random.randrange(-273, 500, 3))
        a_client.publish(topic_p, json.dumps(payload), 2)


if __name__ == "__main__":
    main()
