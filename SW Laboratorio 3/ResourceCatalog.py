import cherrypy
import json
import time
from Client import GenClientMQTT

# Configuration constants
RESOURCE_CATALOG_HOST = "127.0.0.1"
RESOURCE_CATALOG_PORT = 8080
SUBSCRIPTION = {
                    "REST": {
                        "device": "http://127.0.0.1:8080/devices/subscription",
                        "service": "http://127.0.0.1:8080/services/subscription",
                        "user": "http://127.0.0.1:8080/users/subscription"
                    },
                    "MQTT": {
                        "device": {
                            "hostname": "iot.eclipse.org",
                            "port": "1883",
                            "topic": "tiot/group14/catalog/devices/subscription"
                        }

                    }
                }

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
        diff_time = curr_time - float(obj["t"])
        if diff_time > 120:
            toDelete.append(counter)

        counter += 1

    for i in toDelete:
        del listToRefresh[i]


class ResourceCatalogREST:
    exposed = True

    def __init__(self):
        self.subscription = SUBSCRIPTION

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

    # Create resources
    def POST(self, *uri, **params):
        if len(uri) != 2:
            raise cherrypy.HTTPError(400, "Bad Request: wrong URI for POST.")

        if uri[-1] != "subscription":
            raise cherrypy.HTTPError(400, "Bad Request: malformed syntax.")

        contentType = cherrypy.request.headers['Content-Type']
        if contentType != "application/json":
            raise cherrypy.HTTPError(400, "Bad Request: wrong Content-Type")

        rawBody = json.loads(cherrypy.request.body.read())
        if checkBody(uri[0], rawBody):
            if uri[0] == 'devices':
                devices.append(rawBody)
            elif uri[0] == 'users':
                users.append(rawBody)
            elif uri[0] == 'services':
                services.append(rawBody)
        else:
            raise cherrypy.HTTPError(400, "Bad Request: invalid body")

    # Update resources
    def PUT(self, *uri, **params):
        if len(uri) != 2:
            raise cherrypy.HTTPError(400, "Bad Request: wrong URI for POST.")

        if uri[-1] != "subscription":
            raise cherrypy.HTTPError(400, "Bad Request: malformed syntax.")

        contentType = cherrypy.request.headers['Content-Type']
        if contentType != "application/json":
            raise cherrypy.HTTPError(400, "Bad Request: wrong Content-Type")

        rawBody = json.loads(cherrypy.request.body.read())
        if checkBody(uri[0], rawBody):
            found = False
            id = rawBody["uuid"]
            if uri[0] == 'devices':

                for d in devices:
                    if d["uuid"] == id:
                        # Update timestamp
                        d["t"] = rawBody["t"]
                        found = True
                        break

                if not found:
                    devices.append(rawBody)

            if uri[0] == 'users':

                for u in users:
                    if u["uuid"] == id:
                        found = True
                        break

                if not found:
                    users.append(rawBody)

            if uri[0] == 'services':

                for s in services:
                    if s["uuid"] == id:
                        # Update timestamp
                        s["t"] = rawBody["t"]
                        found = True

                if not found:
                    services.append(rawBody)

        else:
            raise cherrypy.HTTPError(400, "Bad Request: invalid body")


class ResourceCatalogMQTT:

    def __init__(self, client_id):
        self.id = client_id
        self.messageBroker = MSG_BROKER_ADDRESS
        self.mqttClient = PahoMQTT.Client(self.id, False)
        self.topic = ""
        self.buffer = []
        self.subscription = SUBSCRIPTION
        self.isSubscribed = False

    def gen_publish(self, topic, message):
        self.mqttClient.publish(topic, message, 2)

    def gen_subscribe(self):
        if not self.isSubscribed :
            self.topic = self.subscription["MQTT"]["device"]["topic"]
            self.mqttClient.subscribe(self.topic, 2)
            self.isSubscribed = True

    def gen_start(self):
        self.mqttClient.on_connect = self.gen_on_connect
        self.mqttClient.on_message = self.gen_msg_received
        self.mqttClient.connect(self.messageBroker)
        self.mqttClient.loop_start()

        if not self.isSubscribed:
            self.gen_subscribe()

    def gen_stop(self):
        self.mqttClient.unsubscribe(self.topic)
        self.mqttClient.loop_stop()
        self.mqttClient.disconnect()

    def gen_msg_received(self, client_id, userdata, msg):
        print("Received message: '" + str(msg.payload) + "' regarding topic '" + str(msg.topic) + "'")
        device_received = json.loads(msg.payload.decode("utf-8"))

        # Check messages received
        if not checkBody("devices", device_received):
            raise Exception("The message is not well structured.")

        found = False
        for dev in devices:
            if dev["uuid"] == device_received["uuid"]:
                dev["t"] = device_received["t"]  # update timestamp
                found = True
                break

        if not found:
            devices.append(device_received)

        topic = self.topic + "/" + str(device_received["uuid"])
        msg = "Device" + (str(device_received["uuid"])) + " data correctly added or updated"
        self.gen_publish(topic, msg)

        # Just to test
        print(msg)

    def gen_on_connect(self, client_id, userdata, flag, rc):
        print("Connected with result code "+ str(rc))


def main():
    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True,
        }
    }

    cherrypy.tree.mount(ResourceCatalogREST(), '/', conf)
    cherrypy.config.update({'server.socket_host': RESOURCE_CATALOG_HOST})
    cherrypy.config.update({'server.socket_port': RESOURCE_CATALOG_PORT})
    cherrypy.engine.start()

    dev = ResourceCatalogMQTT("Yun_Group14")
    dev.gen_start()
    dev.gen_subscribe()
    # (CATALOG AS SUBSCRIBER) when a device publishes its info on this topic the catalog will retrieve them
    # (CATALOG AS PUBLISHER) for every device saved via MQTT a new specific topic will be generated

    while True:
        # Just to test
        print("Printing devices...")
        print(devices)
        print("")
        # print(services)
        # print(users)

        # Print updated lists to file resourcesData.json
        json_object = str(users) + str(devices) + str(services)
        #with open("resourcesData.json", "w") as outfile:
        #    outfile.write(json_object)

        # Refreshing the lists
        refresh(devices)
        refresh(services)
        time.sleep(60)


if __name__ == "__main__":
    main()