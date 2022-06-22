import paho.mqtt.client as PahoMQTT
import uuid
import requests
import time
import json
import math

# Configuration constants
RESOURCE_CATALOG_ADDRESS = "http://127.0.0.1:8080/"
MSG_BROKER_ADDRESS = "test.mosquitto.org"
TIMEOUT_PIR = 5
N_SOUND_EVENTS = 3
SOUND_INTERVAL = 5

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
        self.endpoints.append("temperature")
        self.endpoints.append("presence")

        self.temperature = 0
        self.presence = 0
        self.lastPresenceTime = 0
        self.firstPresenceTime = 0
        self.events = 0
        self.firstEventMicro = 0
        self.lastEventMicro = 0

        self._topic = []
        self._isSubscriber = False

        # create an instance of paho.mqtt.client
        self._paho_mqtt = PahoMQTT.Client(clientID, False)

        # register the callback
        self._paho_mqtt.on_connect = self.myOnConnect
        self._paho_mqtt.on_message = self.myOnMessageReceived

        self.messageBroker = 'test.mosquitto.org'

    def start(self):
        # manage connection to broker
        self._paho_mqtt.connect(MSG_BROKER_ADDRESS, 1883)
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
        print("Published message %s on topic %s" % (message, topic))

    def myOnConnect(self, paho_mqtt, userdata, flags, rc):
        global isConnected
        print("Connected to %s with result code: %d" % (self.messageBroker, rc))
        isConnected = True

    def mySubscribe(self, topic):
        print("Subscribing to %s" % topic)
        # subscribe for a topic
        self._paho_mqtt.subscribe(topic, 2)

        self._isSubscriber = True
        self._topic.append(topic)

    def myOnMessageReceived(self, paho_mqtt, userdata, message):
        # A new message is received
        print("Received message %s on topic %s" % (message, message.topic))
        topic = message.topic.split('/')
        msg1 = str(message.payload.decode("utf-8"))
        msg = json.loads(msg1)
        if "e" not in msg or "bn" not in msg:
            print("Request badly structured")
        elif "n" not in msg["e"][0] or "t" not in msg["e"][0] or "v" not in msg["e"][0] or "u" not in msg["e"][0]:
            print("Request badly structured")
        else:
            match topic[4]:
                case "tempSensor_raw":
                    try:
                        R = (1023.0 / float(msg["e"][0]["v"])) - 1.0
                        R = R * 100000
                        self.temperature = float(1.0/((math.log(R/100000))/4275+1/298.15)-273.15)
                    except:
                        print("Data handling error")
                case "PIRSensor":
                    try:
                        if int(msg["e"][0]["v"]) == 1:
                            self.presence = 1
                            self.lastPresenceTime = time.time()
                            if self.firstPresenceTime == 0:
                                self.firstPresenceTime = self.lastPresenceTime
                        elif int(msg["e"][0]["v"]) == 0:
                            timePassedMinutes = (self.lastPresenceTime - self.firstPresenceTime) / 60
                            if timePassedMinutes >= TIMEOUT_PIR:
                                self.firstPresenceTime = 0
                                self.presence = 0
                    except:
                        print("Data handling error")
                case "microSensor":
                    try:
                        if int(msg["e"][0]["v"]) == 1:
                            self.events+=1
                            self.lastEventMicro = time.time()
                            if self.events >= N_SOUND_EVENTS:
                                self.events = 0
                                self.presence = 1
                                self.firstEventMicro = 0
                            if self.firstEventMicro == 0:
                                self.firstEventMicro = self.lastEventMicro
                        elif int(msg["e"][0]["v"]) == 0:
                            timePassed = (self.lastEventMicro - self.firstEventMicro) / 60
                            if self.timePassed >= SOUND_INTERVAL:
                                self.events = 0
                                self.firstEventMicro = 0
                                self.lastEventMicro = 0
                    except:
                        print("Data handling error")
                case default:
                    print("Request's syntax is wrong")    

def main():
    # Create the MQTT client
    c = MyMQTT(str(uuid.uuid1()))
    c.start()

    req = requests.get(RESOURCE_CATALOG_ADDRESS)
    if req.status_code != 200:
        req.raise_for_status()

    # Convert the received payload from JSON to dictionary
    subscription = req.json()

    # Define the service
    new_service = {
        "bn": "ActuatorsServiceGroup14",
        "e": [{
            "n": c.clientID,
            "des": "Controls a set of actuators",
            "ep": ["temperature", "presence"],
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

    # Request all devices registered to find those who publish certain measurements
    req = requests.get(RESOURCE_CATALOG_ADDRESS + "services/")
    if req.status_code != 200:
        req.raise_for_status()

    # Filter the list of devices through removing the ones who doesn't publish certain measurements
    services = json.loads(req.text)
    for serv in services:
        if "SensorsServiceGroup14" not in serv["bn"]:
            services.remove(serv)

    time.sleep(1)

    while not isConnected:
        pass
        
    for serv in services:
        for i in range(len(serv["e"][0]["ep"])):
            c.mySubscribe("/tiot/group14/"+ serv["e"][0]["n"] +"/"+ serv["e"][0]["ep"][i] +"/")

    while True:
        
        TEMP["n"] = "temperature"
        TEMP["t"] = time.time()
        TEMP["v"] = c.temperature
        MESSAGE["e"]=[TEMP]
        c.myPublish("/tiot/group14/command/"+ c.clientID +"/"+ c.endpoints[0] +"/", json.dumps(MESSAGE).encode("utf-8"))
        
        TEMP["n"] = "presence"
        TEMP["t"] = time.time()
        TEMP["v"] = c.presence
        MESSAGE["e"]=[TEMP]
        c.myPublish("/tiot/group14/command/"+ c.clientID +"/"+ c.endpoints[1] +"/", json.dumps(MESSAGE).encode("utf-8"))
        # Sleep for 2 seconds
        time.sleep(5)

    c.stop()

if __name__ == "__main__":
    main()