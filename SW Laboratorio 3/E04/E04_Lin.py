import paho.mqtt.client as PahoMQTT
import requests
import time
import json
import random

import urllib3
import uuid

# Configuration constants
RESOURCE_CATALOG_ADDRESS = "http://127.0.0.1:8080/"
MSG_BROKER_ADDRESS = "test.mosquitto.org"

# Used to check that the connection to the MQTT Broker
isConnected = False

MESSAGE = {
    "bn": "YunGroup14",
    "e": []
}
TEMP = {
    "n": "",
    "t": 0,
    "v": 0,
    "u": "null"
}

class MyMQTT:
    def __init__(self, clientID):
        self.clientID = clientID

        self.endpoints=[]
        self.endpoints.append("tempSensor_raw")
        self.endpoints.append("PIRSensor")
        self.endpoints.append("microSensor")

        self._topic = []
        self._isSubscriber = False

        # create an instance of paho.mqtt.client
        self._paho_mqtt = PahoMQTT.Client(clientID, False)

        # register the callback
        self._paho_mqtt.on_connect = self.myOnConnect
        self._paho_mqtt.on_message = self.myOnMessageReceived

        self.messageBroker = MSG_BROKER_ADDRESS

    def start(self):
        # manage connection to broker
        self._paho_mqtt.connect(self.messageBroker, 1883)
        self._paho_mqtt.loop_start()

    def stop(self):
        if self._isSubscriber:
            # remember to unsuscribe if it is working also as subscriber
            self._paho_mqtt.unsubscribe(self._topic)

        self._paho_mqtt.loop_stop()
        self._paho_mqtt.disconnect()

    def myPublish(self, topic, message):
        # publish a message with a certain topic
        self._paho_mqtt.publish(topic, message, 2)

    def myOnConnect(self, paho_mqtt, userdata, flags, rc):
        global isConnected
        isConnected = True

    def mySubscribe(self, topic):
        # subscribe for a topic
        self._paho_mqtt.subscribe(topic, 2)

        self._isSubscriber = True
        self._topic.append(topic)

    def myOnMessageReceived(self, paho_mqtt, userdata, message):
        # A new message is received
        topic = message.topic.split('/')
        msg1 = str(message.payload.decode("utf-8"))
        msg = json.loads(msg1)
        if topic[3] == "command":
            if "e" not in msg or "bn" not in msg:
                print("E:3")
            elif "n" not in msg["e"][0] or "t" not in msg["e"][0] or "v" not in msg["e"][0] or "u" not in msg["e"][0]:
                print("E:3")
            else:
                match topic[5]:
                    case "temperature":
                        try:
                            print("A:%f" % (float(msg["e"][0]["v"])))
                        except:
                            print("E:1")
                    case "presence":
                        try:
                            print("B:%f" % (float(msg["e"][0]["v"])))
                        except:
                            print("E:1")
                    case default:
                        print("E:2")

if __name__ == "__main__":
    yun = MyMQTT(str(uuid.uuid1()))
    yun.start()

    req = requests.get(RESOURCE_CATALOG_ADDRESS)
    if req.status_code != 200:
        req.raise_for_status()

    # Convert the received payload from JSON to dictionary
    subscription = req.json()

    # Define the service
    new_service = {
        "bn": "SensorsServiceGroup14",
        "e": [{
            "n": yun.clientID,
            "des": "Outputs data produced from sensors",
            "ep": ["tempSensor_raw", "PIRSensor", "microSensor"],
            "t": str(time.time())
        }]
    }

    # Define the header of the request
    header = {
        "Content-Type": "application/json"
    }

    # Make public this service
    req = requests.post(subscription["REST"]["service"], headers=header, data=json.dumps(new_service))
    if req.status_code != 200:
        req.raise_for_status()

    #Wait some time so the other clients can connect
    time.sleep(5)

    req = requests.get(RESOURCE_CATALOG_ADDRESS + "services/")
    if req.status_code != 200:
        req.raise_for_status()

    services = json.loads(req.text)
    for serv in services:
        if "ActuatorsServiceGroup14" not in serv["bn"]:
            services.remove(serv)

    time.sleep(1)
    
    while not isConnected:
        pass

    for serv in services:
        for i in range(len(serv["e"][0]["ep"])):
            yun.mySubscribe("/tiot/group14/command/"+ serv["e"][0]["n"] +"/"+ serv["e"][0]["ep"][i] +"/")

    while True:
        MESSAGE["e"].clear()

        # Retrieve temperature values from arduino
        msg = input()
        msg = msg.split(":")

        # Check if the value received is a float
        match msg[0]:
            case 'T':
                # Format the data in SenML and publish
                TEMP["n"] = "temperature"
                TEMP["t"] = time.time()
                TEMP["v"] = msg[1].strip()
                MESSAGE["e"]=[TEMP]
                yun.myPublish("/tiot/group14/"+ yun.clientID +"/"+ yun.endpoints[0] +"/", json.dumps(MESSAGE).encode("utf-8"))
            case 'P':
                TEMP["n"] = "PIRPresence"
                TEMP["t"] = time.time()
                TEMP["v"] = msg[1].strip()
                MESSAGE["e"]=[TEMP]
                yun.myPublish("/tiot/group14/"+ yun.clientID +"/"+ yun.endpoints[1] +"/", json.dumps(MESSAGE).encode("utf-8"))
            case 'M':
                TEMP["n"] = "MicrophonePresence"
                TEMP["t"] = time.time()
                TEMP["v"] = msg[1].strip()
                MESSAGE["e"]=[TEMP]
                yun.myPublish("/tiot/group14/"+ yun.clientID +"/"+ yun.endpoints[2] +"/", json.dumps(MESSAGE).encode("utf-8"))
            case default:
                print("E:4")
    yun.stop()