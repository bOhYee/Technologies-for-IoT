import uuid
import time
import json
import requests
import paho.mqtt.client as mqtt

# Configuration constants
RESOURCE_CATALOG_ADDRESS = "http://127.0.0.1:8080/"
MSG_BROKER_ADDRESS = "localhost"
BASE_TOPIC_PUB = "tiot/group14/"
BASE_TOPIC_SUB = "tiot/group14/command/"

MESSAGE = {
    "bn": "YunGroup14",
    "e": []
}
TEMP = {
    "n": "temperature",
    "t": 0.0,
    "v": 0.0,
    "u": "Celsius"
}

device_data = {
    "bn": "DeviceGroup14",
    "e": []
}


def myOnConnect(client, userdata, flags, rc):
    # Print result of connection attempt
    print("Connected to broker with result code {0}".format(str(rc)))


# reagire ai messaggi controllandone il formato
def myOnMessageReceived(client, userdata, message):
    # A new message is received
    topic = message.topic.split('/')
    msg = json.loads(str(message.payload.decode("utf-8")))
    if topic[-1] == "LedSensor":
        if "e" not in msg or "bn" not in msg:
            return "Missing data!"
        if "n" not in msg["e"][0] or "t" not in msg["e"][0] or "v" not in msg["e"][0] or "u" not in msg["e"][0]:
            return "Missing data!"
        if msg["e"][0]["n"] != 'led':
            return "Invalid name."
        if msg["e"][0]["v"] not in [0, 1]:
            return "Invalid led command."
        peripheral = msg["e"][0]["n"]
        value = msg["e"][0]["v"]
        print("L:" + str(value))


# retrieve information of the Catalog available subscriptions via MQTT
def recoverData():
    req = requests.get(RESOURCE_CATALOG_ADDRESS)
    # Raises an exception if it cannot reach the ResourceCatalog
    if req.status_code != 200:
        req.raise_for_status()
    subscription = req.json()

    return subscription["MQTT"]["device"]["topic"]


def main():
    uuid_cl = str(uuid.uuid1())

    client = mqtt.Client(uuid_cl)
    client.on_connect = myOnConnect
    client.on_message = myOnMessageReceived
    client.connect(MSG_BROKER_ADDRESS)
    client.loop_start()

    # 1. retrieve information of the Catalog
    topic_data = recoverData()

    # 2. register as a new device through MQTT communicating the topic for temperature measurements and for led command
    temp_ep = BASE_TOPIC_PUB + uuid_cl + "/TempSensor"
    led_ep = BASE_TOPIC_SUB + uuid_cl + "/LedSensor"
    device = [{"n": uuid_cl, "ep": [temp_ep, led_ep], "res": ["temperature", "led"], "t": str(time.time())}]
    device_data["e"] = device
    client.publish(topic_data, json.dumps(device_data), 2)

    # iscriversi al topic per controllare uno dei LED della board
    client.subscribe(led_ep, 2)

    while True:
        MESSAGE["e"].clear()
        # Retrieve temperature values from arduino
        msg = input()
        msg = msg.split(":")
        # Check if the value received is a float
        if msg[0] == 'T':
            try:
                val = float(msg[1].strip())
            except:
                print("Cannot convert to float!")
                continue

            # Format the data in senML and publish them
            TEMP["t"] = time.time()
            TEMP["v"] = val
            MESSAGE["e"] = [TEMP]
            client.publish(temp_ep, json.dumps(MESSAGE).encode('utf-8'))
            print("Published" + str(MESSAGE) + " at " + temp_ep)

        # Renew each 1 minute the subscription
        time.sleep(60)
        device_data["e"][0]["t"] = str(time.time())
        client.publish(topic_data, str(json.dumps(device_data)), 2)
        print("Aggiornamento: " + str(json.dumps(device_data)))

    client.unsubscribe(topic_data)
    client.loop_stop()
    client.disconnect()


if __name__ == '__main__':
    main()
