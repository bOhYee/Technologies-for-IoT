import paho.mqtt.client as PahoMQTT
import time
import json
import random

import urllib3
import uuid

MESSAGE = {
    "bn": "YunGroup14",
    "e": []
}
TEMP = {
    "n": "temperature",
    "t": 0,
    "v": 0,
    "u": "Celsius"
}


class MyMQTT:
    def __init__(self, clientID):
        self.clientID = clientID

        self._topic = ""
        self._isSubscriber = False

        # create an instance of paho.mqtt.client
        self._paho_mqtt = PahoMQTT.Client(clientID, False)

        # register the callback
        self._paho_mqtt.on_connect = self.myOnConnect
        self._paho_mqtt.on_message = self.myOnMessageReceived

        self.messageBroker = 'test.mosquitto.org'

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
        print("Connected to %s with result code: %d" % (self.messageBroker, rc))

    def mySubscribe(self, topic):
        print("Subscribing to %s" % topic)
        # subscribe for a topic
        self._paho_mqtt.subscribe(topic, 2)

        self._isSubscriber = True
        self._topic = topic

    def myOnMessageReceived(self,paho_mqtt , userdata, message):
        # A new message is received
        topic = message.topic.split('/')
        msg1 = str(message.payload.decode("utf-8"))
        msg = json.loads(msg1)
        if topic[-1] == "command":
            if "e" not in msg or "bn" not in msg:
                print("E:3")
            elif "n" not in msg["e"][0] or "t" not in msg["e"][0] or "v" not in msg["e"][0] or "u" not in msg["e"][0]:
                print("E:3")
            elif msg["e"][0]["n"] != 'led':
                print("E:4")
            elif msg["e"][0]["v"] not in [0, 1]:
                print("E:5")
            else:
                peripheral = msg["e"][0]["n"]
                value = msg["e"][0]["v"]
                print("L:" + str(value))


if __name__ == "__main__":
    yun = MyMQTT(str(uuid.uuid1()))
    yun.start()
    yun.mySubscribe("/tiot/group14/command")

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
                print("E:1")
                continue
        
            # Format the data in SenML and publish 
            TEMP["t"] = time.time()
            TEMP["v"] = val
            MESSAGE["e"]=[TEMP]
            yun.myPublish("/tiot/group14/", json.dumps(MESSAGE).encode("utf-8"))
        else:
            print("E:2")
    yun.stop()
# string for led command
# '{\"bn\": \"YunGroup14\",\"e\": [{\"n\": \"led\",\"t\": null,\"v\": 1,\"u\": null}]}'
