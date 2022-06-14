import uuid
import time
import json
import requests
import paho.mqtt.client as mqtt

# Client name
import urllib3

CLIENT_NAME = "Group_14"
# Broker IP
HOST_NAME = '127.0.0.1'
RESOURCE_CATALOG_ADDRESS = "http://127.0.0.1:8080/"

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
    if topic[-1] == 'command':
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


if __name__ == '__main__':
    client = mqtt.Client(CLIENT_NAME)
    client.on_connect = myOnConnect
    client.on_message = myOnMessageReceived
    client.connect(HOST_NAME, 1883)
    client.loop_start()

    # iscriversi al topic /tiot/group14/command per controllare uno dei LED della board
    client.subscribe("tiot/group14/command")

    # 1. retrieve information of the Catalog
    topic_data = recoverData()
    print(topic_data)
    
    # 2. register as a new device through MQTT communicating the topic for temperature measurements and for led command
    device = [{"ep": ["TempSensor", "LedSensor"], "res": ["temperature", "led"], "t": str(time.time())}]
    device_data["bn"] = str(uuid.uuid1())
    device_data["e"] = device
    print(str(json.dumps(device_data)))
    client.publish(topic_data, json.dumps(device_data), 2)

    while True:
        # retrieve temperature values from arduino
        http = urllib3.PoolManager()
        msg = http.request("GET", "http://127.0.0.1:8080/arduino/temperature")
        json_msg = json.loads(str(msg))
        val = json_msg["e"][0]["v"]
        time.sleep(10)
        # format the data in senML and publish them
        TEMP["t"] = time.time()
        TEMP["v"] = val
        MESSAGE["e"] = [TEMP]
        json_data = json.dumps(MESSAGE).encode('utf-8')
        client.publish("tiot/group14", json_data)
        # 3. renew each 1 minute the subscription
        time.sleep(60)
        device_data["e"][0]["t"] = str(time.time())
        client.publish(topic_data, str(json.dumps(device_data)), 2)
        print("Aggiornamento: " + str(json.dumps(device_data)))

    client.unsubscribe(topic_data)
    client.loop_stop()
    client.disconnect()
