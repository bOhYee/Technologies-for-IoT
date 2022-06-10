import uuid
import time
import json
import requests
import paho.mqtt.client as mqtt

# Client name
CLIENT_NAME = "Group_14"
# Broker IP
HOST_NAME = '127.0.0.1'
RESOURCE_CATALOG_ADDRESS = "http://127.0.0.1/"

temp_values = []
service_data = {
    "bn": "ServiceGroup14",
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
    temp_values.append(msg["e"][0]["val"])


# retrieve information of the Catalog available subscriptions via REST
def recoverData():
    req = requests.get(RESOURCE_CATALOG_ADDRESS)
    # Raises an exception if it cannot reach the ResourceCatalog
    if req.status_code != 200:
        req.raise_for_status()
    subscription = req.json()
    return subscription["REST"]["service"]


if __name__ == '__main__':
    client = mqtt.Client(CLIENT_NAME)
    client.on_connect = myOnConnect
    client.on_message = myOnMessageReceived
    client.connect(HOST_NAME, 1883)
    client.loop_start()

    # 1. retrieve information of the Catalog
    rest_url = recoverData()
    print(rest_url)

    # 2. register as a new service through REST
    service = [{"uuid": str(uuid.uuid1()), "ep": "TempService", "des": "I provide temperature data",
               "t": str(time.time())}]
    service_data["e"] = service
    json_data = json.dumps(service_data).encode('utf-8')
    r = requests.post(rest_url, service_data)
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
        if ["bn"] == "DeviceGroup14": #look for our Arduino device
            res_list = dev["e"][0]["res"]
            if "temperature" in res_list:
                index_endpoint = res_list.index("temperature") # resources name and corresponding endpoints have the same index
                client.subscribe(dev["e"][0]["ep"][index_endpoint])
        else:
            raise Exception("Device not available")

    time.sleep(60)
    client.loop_stop()
    client.disconnect()

"""
The exchanged data is in senML format.
All following values have to be considered as examples, not actual values
2. The service will register to the catalog using the following data format:
    service_data = {
        "bn": "ServiceGroup14",
        "e": [{ "uuid": str(uuid.uuid1()), 
                "ep": "TempService", 
                "des": "I provide temperature data",
                "t": str(time.time())}]
    }
3. The retrieved data about the Arduino Yun device will be in the following format:
    device = {
        "bn": "DeviceGroup14",
        "e": [{ "uuid": "uniqueDeviceID", 
                "ep": ["TempSensor", "LedSensor"],  
                "res": ["temperature","led"],
                "t": "timeValue"}]
    }
4. The temperature measurements retrieved from the MQTT endpoints will come in the following format:
    temp_data = {
        "bn": "YunGroup14",
        "e": [{ "n": "temperature",
                "t": 0,
                "val": 0,
                "u": "Celsius"
    }
"""