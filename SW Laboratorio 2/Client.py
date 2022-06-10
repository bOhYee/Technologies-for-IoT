import requests
import uuid
import time
import json
import paho.mqtt.client as PahoMQTT

# Configuration constants
RESOURCE_CATALOG_ADDRESS = "http://127.0.0.1:8080/"
MSG_BROKER_ADDRESS = "localhost"


class ClientREST:

    def __init__(self):
        self.devices_maintained = []
        self.subscription = {}

    def recover_subscription_data(self):
        req = requests.get(RESOURCE_CATALOG_ADDRESS)
        # Raises an exception if it cannot reach the ResourceCatalog
        if req.status_code != 200:
            req.raise_for_status()

        # Verify that the response contains a JSON as payload
        # if req.headers["Content-type"] != "application/json":
        #   raise ValueError("Error: response received does not include a JSON.")

        self.subscription = req.json()

    def get_subscription_data(self):
        return self.subscription

    def retrieve_all_reg_devices(self):
        url_dev = RESOURCE_CATALOG_ADDRESS + "devices/"

        return self.__retrieve(url_dev)

    def retrieve_device(self, uuid_dev):
        url_dev = RESOURCE_CATALOG_ADDRESS + "devices/" + str(uuid_dev)

        return self.__retrieve(url_dev)

    def retrieve_all_reg_users(self):
        url_usr = RESOURCE_CATALOG_ADDRESS + "users/"

        return self.__retrieve(url_usr)

    def retrieve_user(self, uuid_usr):
        url_usr = RESOURCE_CATALOG_ADDRESS + "users/" + str(uuid_usr)

        return self.__retrieve(url_usr)

    def __retrieve(self, url):
        req = requests.get(url)
        if req.status_code != 200:
            req.raise_for_status()

        return json.loads(req.text)

    def register_new_device(self):
        # Creation of the new device
        new_device = {}
        new_device["uuid"] = str(uuid.uuid1())
        new_device["ep"] = "REST"
        new_device["res"] = ["temperature", "pressure"]
        new_device["t"] = str(time.time())

        # Definition of the header of the request
        header = {}
        header["Content-Type"] = "application/json"

        self.devices_maintained.append(new_device)
        req = requests.post(self.subscription["REST"]["device"], headers=header, data=json.dumps(new_device))
        # If the request is invalid, raise an Exception
        if req.status_code != 200:
            req.raise_for_status()

    def refresh_devices(self):
        # If the request is invalid, raise an Exception
        header = {}
        header["Content-Type"] = "application/json"
        url = self.subscription["REST"]["device"]

        for dev in self.devices_maintained:
            dev["t"] = str(time.time())
            req = requests.put(url, headers=header, data=json.dumps(dev))
            # If the request is invalid, raise an Exception
            if req.status_code != 200:
                req.raise_for_status()


class ClientMQTT:

    def __init__(self, client_id):

        # Initially considered only as a Publisher
        self.isSubscriber = False

        self.id = client_id
        self.messageBroker = MSG_BROKER_ADDRESS
        self.mqttClient = PahoMQTT.Client(self.id, False)
        self.topic = []
        self.buffer = []
        self.devices_maintained = []
        self.subscription = {}

        self.__gen_recover_subscription_data()

    def gen_publish(self, topic, message):
        self.mqttClient.publish(topic, message, 2)

    def gen_subscribe(self, topic):
        if not self.isSubscriber :
            self.mqttClient.on_message = self.gen_msg_received
            self.isSubscriber = True

        self.topic.append(topic)
        self.mqttClient.subscribe(topic, 2)

    def gen_start(self):
        self.mqttClient.on_connect = self.gen_on_connect
        self.mqttClient.connect(self.messageBroker)
        self.mqttClient.loop_start()

    def gen_stop(self):
        if self.isSubscriber:
            for top in self.topic:
                self.mqttClient.unsubscribe(top)

        self.topic.clear()
        self.mqttClient.loop_stop()
        self.mqttClient.disconnect()

    def gen_msg_received(self, client_id, userdata, msg):
        print("Received message: '" + str(msg.payload) + "' regarding topic '" + str(msg.topic) + "'")

    def gen_on_connect(self, client_id, userdata, flag, rc):
        print("Connected with result code "+ str(rc))

    def __gen_recover_subscription_data(self):
        req = requests.get(RESOURCE_CATALOG_ADDRESS)

        # Raises an exception if it cannot reach the ResourceCatalog
        if req.status_code != 200:
            req.raise_for_status()

        # Verify that the response contains a JSON as payload
        # if req.headers["Content-type"] != "application/json":
        #   raise ValueError("Error: response received does not include a JSON.")

        self.subscription = req.json()

    def gen_get_subscription_data(self):
        return self.subscription

    def gen_register_new_device(self):
        # Creation of the new device
        new_device = {}
        new_device["uuid"] = str(uuid.uuid1())
        new_device["ep"] = "MQTT"
        new_device["res"] = ["heat"]
        new_device["t"] = str(time.time())
        self.devices_maintained.append(new_device)

        topic = self.subscription["MQTT"]["device"]["topic"]
        self.gen_publish(topic, json.dumps(new_device))

    def gen_refresh_devices(self):
        topic = self.subscription["MQTT"]["device"]["topic"]

        for dev in self.devices_maintained:
            dev["t"] = str(time.time())
            self.gen_publish(topic, json.dumps(dev))
