import paho.mqtt.client as PahoMQTT
import time
import json
import random

import urllib3

MESSAGE = {
    "bn": "YunGroup14",
    "e": []
}
TEMP = {
    "n": "temperature",
    "t": 0,
    "val": 0,
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


if __name__ == "__main__":
    yun = MyMQTT("Yun_Group14")
    yun.start()
    yun.mySubscribe("tiot/group14/command")

    while True:
        #retrieve temperature values from arduino
        http = urllib3.PoolManager()
        msg = http.request("GET", "http://127.0.0.1:8080/arduino/temperature")
        json_msg = json.loads(msg.data.decode('utf-8'))
        val = json_msg["e"][0]["v"]
        time.sleep(10)
        # format the data in senML and publish them
        TEMP["t"] = time.time()
        TEMP["v"] = val
        MESSAGE["e"] = [TEMP]
        json_data = json.dumps(MESSAGE).encode('utf-8')
        yun.myPublish("tiot/group14", json_data)

# string for led command
# "{\"bn\": \"YunGroup14\",\"e\": [{\"n\": \"led\",\"t\": null,\"v\": 1,\"u\": null}]}"
