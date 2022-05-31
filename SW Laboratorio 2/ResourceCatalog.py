import cherrypy
import json
import time
import paho.mqtt.client as PahoMQTT

devices = []
users = []
services = []


def checkBody(resource, rawBody):
    if resource == 'devices':
        for k in rawBody.keys():
            if k not in ["uuid", "ep", "res", "t"]:
                return False
    elif resource == 'users':
        for k in rawBody.keys():
            if k not in ["uuid", "name", "surname", "email"]:
                return False
    elif resource == 'services':
        for k in rawBody.keys():
            if k not in ["uuid", "des", "ep", "t"]:
                return False
    return True


def refresh(listToRefresh):
    counter = 0
    toDelete = []
    curr_time = time.time()

    for obj in listToRefresh:
        diff_time = curr_time - obj["t"]
        if diff_time > 120:
            toDelete.append(counter)

        counter += 1

    for i in toDelete:
        del listToRefresh[i]


class ResourceCatalog:
    exposed = True

    def __init__(self):
        self.subscription = {
            "REST": {
                "device": "http://192.168.0.10:8080/devices/subscription",
                "service": "http://192.168.0.10:8080/services/subscription",
                "user": "http://192.168.0.10:8080/users/subscription"
            },
            "MQTT": {
                "device": {
                    "hostname": "iot.eclipse.org",
                    "port": "1883",
                    "topic": "tiot/group14/catalog/devices/subscription"
                }

            }
        }

    def GET(self, *uri, **params):
        if len(uri) == 0:
            return json.dumps(self.subscription)

        elif len(uri) <= 2:
            if uri[0] == 'devices':
                if len(uri) == 1:
                    return json.dumps(devices)
                else:
                    for d in devices:
                        if d["uuid"] == uri[1]:
                            return json.dumps(d)
                raise cherrypy.HTTPError(404, "Invalid uuid")

            elif uri[0] == 'users':
                if len(uri) == 1:
                    return json.dumps(users)
                else:
                    for u in users:
                        if u["uuid"] == uri[1]:
                            return json.dumps(u)
                raise cherrypy.HTTPError(404, "Invalid uuid")

            elif uri[0] == 'services':
                if len(uri) == 1:
                    return json.dumps(services)
                else:
                    for s in services:
                        if s["uuid"] == uri[1]:
                            return json.dumps(s)
                raise cherrypy.HTTPError(404, "Invalid uuid")
            else:
                raise cherrypy.HTTPError(404, "Wrong number of parameters.")

    #create resources
    def POST(self, *uri, **params):
        if uri[-1] == 'subscription':
            contentType = cherrypy.request.headers['Content-Type']
            if contentType != "application/json":
                raise cherrypy.HTTPError(400, "Bad Request: wrong Content-Type")
            rawBody = dict(cherrypy.request.body.read())
            if checkBody(uri[0], rawBody) is True:
                if uri[0] == 'devices':
                    devices.append(json.loads(str(rawBody)))
                elif uri[0] == 'users':
                    users.append(json.loads(str(rawBody)))
                elif uri[0] == 'services':
                    services.append(json.loads(str(rawBody)))
            else:
                raise cherrypy.HTTPError(400, "Bad Request: invalid body")

    #update resources
    def PUT(self,*uri, **params):
        if uri[-1] == 'subscription':
            contentType = cherrypy.request.headers['Content-Type']
            if contentType != "application/json":
                raise cherrypy.HTTPError(400, "Bad Request: wrong Content-Type")
            rawBody = dict(cherrypy.request.body.read())
            id = rawBody["uuid"]
            if checkBody(uri[0], rawBody) is True:
                found = False
                if uri[0] == 'devices':
                    for d in devices:
                        if d["uuid"] == id:
                            d["t"] = rawBody["t"] #update timestamp
                            found = True
                    if found is False:
                        devices.append(json.loads(str(rawBody)))
                if uri[0] == 'users':
                    for u in users:
                        if u["uuid"] == id:
                            found = True
                    if found is False:
                        users.append(json.loads(str(rawBody)))
                if uri[0] == 'services':
                    for s in services:
                        if s["uuid"] == id:
                            s["t"] = rawBody["t"] #update timestamp
                            found = True
                    if found is False:
                        services.append(json.loads(str(rawBody)))
            else:
                raise cherrypy.HTTPError(400, "Bad Request: invalid body")



class ResourceCatalogMQTT():

    def __init__(self, clientID):
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

    def myPublish(self, topic, message): #pub
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

    def myOnMessageReceived(self, paho_mqtt, userdata, message): # add or update device info
        # A new message is received
        topic = message.topic.split('/')
        msg = dict(message.payload.decode('utf-8'))
        found = False
        if checkBody("devices", msg) is True:
            for d in devices:
                if d["uuid"] == msg["uuid"]:
                    d["t"] = msg["t"]  # update timestamp
                    found = True
            if found is False:
                devices.append(json.loads(str(msg)))
            self.myPublish(str(topic) + "/" + str(msg["uuid"]),"Device" + (str(msg["uuid"])) + " data correctly added or updated")
        else:
            raise Exception("The message is not well structured.")



if __name__ == "__main__":
    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tool.session.on': True
        }
    }

    cherrypy.tree.mount(ResourceCatalog(), '/', conf)
    cherrypy.config.update({'server.socket_host': '127.0.0.1'})
    cherrypy.config.update({'server.socket_port': 8080})
    cherrypy.engine.start()

    dev = ResourceCatalogMQTT("Yun_Group14")
    dev.start()
    dev.mySubscribe("tiot/group14/catalog/devices/subscription")
    # (CATALOG AS SUBSCRIBER) when a device publishes its info on this topic the catalog will retrive them
    # (CATALOG AS PUBLISHER) for every device saved via MQTT a new specific topic will be generated

    while True:
        refresh(devices)
        refresh(services)
        #print updated lists to file resourcesData.json
        json_object = str(users) + str(devices) + str(services)
        with open("resourcesData.json", "w") as outfile:
            outfile.write(json_object)
        time.sleep(45)
