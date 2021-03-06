import uuid
import time
import json
import requests
import paho.mqtt.client as mqtt

# Configuration constants
MSG_BROKER_ADDRESS = "localhost"
RESOURCE_CATALOG_ADDRESS = "http://127.0.0.1:8080/"

temp_values = []
service_data = {
    "bn": "TempServiceGroup14",
    "e": []
}


def myOnConnect(client, userdata, flags, rc):
    # Print result of connection attempt
    print("Connected to broker with result code {0}".format(str(rc)))


# 4. retrieving the temperature measuremets from the MQTT endpoints
def myOnMessageReceived(client, userdata, message):
    global temp_values
    # A new message is received
    msg = json.loads(str(message.payload.decode("utf-8")))
    if "n" not in msg["e"][0] or "t" not in msg["e"][0] or "v" not in msg["e"][0] or "u" not in msg["e"][0]:
        raise Exception("Missing data!")
    if msg["e"][0]["n"] != 'temperature':
        raise Exception("Wrong data!")
    temp_values.append(msg["e"][0]["v"])


# retrieve information of the Catalog available subscriptions via REST
def recover_data():
    req = requests.get(RESOURCE_CATALOG_ADDRESS)
    # Raises an exception if it cannot reach the ResourceCatalog
    if req.status_code != 200:
        req.raise_for_status()

    subscription = req.json()
    return subscription["REST"]["service"]


def main():
    uuid_cl = str(uuid.uuid1())

    client = mqtt.Client(uuid_cl)
    client.on_connect = myOnConnect
    client.on_message = myOnMessageReceived
    client.connect(MSG_BROKER_ADDRESS)
    client.loop_start()

    # 1. retrieve information of the Catalog
    rest_url = recover_data()

    # 2. register as a new service through REST
    service = [{"n": uuid_cl, "ep": "TempService", "des": "I provide temperature data", "t": str(time.time())}]
    service_data["e"] = service

    # Define the header of the request
    header = {
        "Content-Type": "application/json"
    }

    r = requests.post(rest_url, headers=header, data=json.dumps(service_data))
    if r.status_code != 200:
        r.raise_for_status()

    # 3. retrieve information about the endpoint used by the Arduino Yun
    # Request all devices registered to find Arduino Yun
    req = requests.get(RESOURCE_CATALOG_ADDRESS + "devices/")
    if req.status_code != 200:
        req.raise_for_status()

    # Subscribe to the topic where temperature values are published
    devices = json.loads(req.text)
    for dev in devices:
        if "temperature" in dev["e"][0]["res"]:
            # Resources name and corresponding endpoints have the same index
            index_endpoint = dev["e"][0]["res"].index("temperature")
            topic = dev["e"][0]["ep"][index_endpoint]
            # print("Subscribing to " + topic)
            client.subscribe(topic, 2)

    while True:
        time.sleep(60)
        print(temp_values)

    client.loop_stop()
    client.disconnect()


if __name__ == '__main__':
    main()
