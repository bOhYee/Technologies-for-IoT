import cherrypy
import json
import time
import paho.mqtt.client as PahoMQTT

# This resource catalog will use only JSON packages that are structured in a certain way
# The package must have a structure similar to the packages used in senML format
# {
#   "bn" : <UUID of the device>,
#   "e"  : <list of feature of the device> (in this case we will suppose that e contains always one element
# }
#
# An element of "e", for the DEVICES, has to be structured like this:
# {
#   "ep"   : <type of communication>, (MQTT or REST)
#   "res"  : <list of strings indicating the resources available for that device>,
#   "t"    : <time which the device has subscribed to the catalog or refreshed its subscription>
# }
#
# An element of "e", for the USERS, has to be structured like this:
# {
#   "name"     : <name of the user>,
#   "surname"  : <surname of the user>,
#   "email"    : <mail of the user>
# }
#
# An element of "e", for the SERVICES, has to be structured like this:
# {
#   "des"  : <description of the service>, (MQTT or REST)
#   "ep"   : <type of communication used by the service>,
#   "t"    : <time which the service has subscribed to the catalog or refreshed its subscription>
# }
#
# Configuration constants
RESOURCE_CATALOG_HOST = "127.0.0.1"
RESOURCE_CATALOG_PORT = 8080
MSG_BROKER_ADDRESS = "test.mosquitto.org"
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

# Lists of dictionaries managed by the ResourceCatalog
devices = []
users = []
services = []

# Used to determine if the catalog received some messages by MQTT protocol
isReceived = False
received = []


def check_body(resource, raw):
    if ("bn" not in raw.keys()) or ("e" not in raw.keys()):
        return False

    raw_body = raw["e"][0]
    if resource == 'devices':
        for k in raw_body.keys():
            if k not in ["ep", "res", "t"]:
                return False
    elif resource == 'users':
        for k in raw_body.keys():
            if k not in ["name", "surname", "email"]:
                return False
    elif resource == 'services':
        for k in raw_body.keys():
            if k not in ["des", "ep", "t"]:
                return False

    return True


def refresh(list_to_refresh):
    # Only used for services and devices, so the attribute "t" exists

    curr_time = time.time()

    for obj in list_to_refresh:
        diff_time = curr_time - float(obj["e"][0]["t"])
        if diff_time > 120:
            list_to_refresh.remove(obj)


def on_msg_received(client_id, userdata, msg):
    # Define which global constants are going to be used AND modified in the on_msg_received() function
    # Other constants do not need a similar declaration if not modified
    global isReceived
    global received
    global devices

    device_received = json.loads(msg.payload.decode("utf-8"))

    # Check messages received
    if not check_body("devices", device_received):
        raise Exception("The message is not well structured.")

    found = False
    for dev in devices:
        if dev["bn"] == device_received["bn"]:
            # Update timestamp
            dev["e"][0]["t"] = device_received["e"][0]["t"]
            found = True
            break

    if (not found) and (check_body("device", device_received)):
        devices.append(device_received)

    isReceived = True
    received.append(device_received)


def on_connect(client_id, userdata, flag, rc):
    print("Connected with result code " + str(rc))


class ResourceCatalogREST:
    exposed = True

    def __init__(self):
        self.subscription = SUBSCRIPTION

    def GET(self, *uri, **params):
        # Define which global constants are going to be used AND modified in this function
        # Other constants do not need a similar declaration if not modified
        global devices
        global users
        global services

        if len(uri) == 0:
            return json.dumps(self.subscription)

        elif len(uri) <= 2:
            if uri[0] == 'devices':
                if len(uri) == 1:
                    return json.dumps(devices)
                else:
                    for d in devices:
                        if d["bn"] == uri[1]:
                            return json.dumps(d)

                raise cherrypy.HTTPError(404, "Invalid uuid")

            elif uri[0] == 'users':
                if len(uri) == 1:
                    return json.dumps(users)
                else:
                    for u in users:
                        if u["bn"] == uri[1]:
                            return json.dumps(u)

                raise cherrypy.HTTPError(404, "Invalid uuid")

            elif uri[0] == 'services':
                if len(uri) == 1:
                    return json.dumps(services)
                else:
                    for s in services:
                        if s["bn"] == uri[1]:
                            return json.dumps(s)

                raise cherrypy.HTTPError(404, "Invalid uuid")

        else:
            raise cherrypy.HTTPError(404, "Wrong number of parameters.")

    # Create resources
    def POST(self, *uri, **params):
        # Define which global constants are going to be used AND modified in this function
        # Other constants do not need a similar declaration if not modified
        global devices
        global users
        global services

        if len(uri) != 2:
            raise cherrypy.HTTPError(400, "Bad Request: wrong URI for POST.")

        if uri[-1] != "subscription":
            raise cherrypy.HTTPError(400, "Bad Request: malformed syntax.")

        contentType = cherrypy.request.headers['Content-Type']
        if contentType != "application/json":
            raise cherrypy.HTTPError(400, "Bad Request: wrong Content-Type")

        rawBody = json.loads(cherrypy.request.body.read())
        if check_body(uri[0], rawBody):
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
        # Define which global constants are going to be used AND modified in this function
        # Other constants do not need a similar declaration if not modified
        global devices
        global users
        global services

        if len(uri) != 2:
            raise cherrypy.HTTPError(400, "Bad Request: wrong URI for POST.")

        if uri[-1] != "subscription":
            raise cherrypy.HTTPError(400, "Bad Request: malformed syntax.")

        contentType = cherrypy.request.headers['Content-Type']
        if contentType != "application/json":
            raise cherrypy.HTTPError(400, "Bad Request: wrong Content-Type")

        rawBody = json.loads(cherrypy.request.body.read())
        if check_body(uri[0], rawBody):
            found = False
            id = rawBody["bn"]
            if uri[0] == 'devices':

                for d in devices:
                    if d["bn"] == id:
                        # Update timestamp
                        d["e"][0]["t"] = rawBody["e"][0]["t"]
                        found = True
                        break

                if not found:
                    devices.append(rawBody)

            if uri[0] == 'users':

                for u in users:
                    if u["bn"] == id:
                        found = True
                        break

                if not found:
                    users.append(rawBody)

            if uri[0] == 'services':

                for s in services:
                    if s["bn"] == id:
                        # Update timestamp
                        s["e"][0]["t"] = rawBody["e"][0]["t"]
                        found = True

                if not found:
                    services.append(rawBody)

        else:
            raise cherrypy.HTTPError(400, "Bad Request: invalid body")


def main():
    # Define which global constants are going to be used AND modified in the main() function
    # Other constants do not need a similar declaration if not modified
    global isReceived
    global received
    global devices
    global users
    global services

    # Configuration of the cherrypy instance
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

    # (CATALOG AS SUBSCRIBER) when a device publishes its info on this topic the catalog will retrieve them
    # (CATALOG AS PUBLISHER) for every device saved via MQTT a new specific topic will be generated
    dev = PahoMQTT.Client("Yun_Group14", True)
    dev.on_message = on_msg_received
    dev.on_connect = on_connect
    dev.connect(MSG_BROKER_ADDRESS)
    dev.loop_start()

    # Subscribe to the topic which every client will use to subscribe new devices
    # Directly taken from the SUBSCRIPTION constant
    dev.subscribe(SUBSCRIPTION["MQTT"]["device"]["topic"], 2)

    while True:
        # Just to test
        print("Printing devices...")
        print(devices)
        print("")

        print("Printing services...")
        print(services)
        print("")

        # If the ResourceCatalog has received some subscription through a MQTT Broker, it needs to tell those client
        # that their devices have been registered
        if isReceived:
            for device_received in received:
                # Publish the reception message
                topic = SUBSCRIPTION["MQTT"]["device"]["topic"] + "/" + str(device_received["e"][0]["uuid"])
                message = "Device " + (str(device_received["e"][0]["uuid"])) + " data correctly added or updated"
                dev.publish(topic, message, 2)

            received.clear()
            isReceived = False

        # Print updated lists to file resourcesData.json
        json_object = str(users) + str(devices) + str(services)
        with open("resourcesData.json", "w") as outfile:
            outfile.write(json_object)

        # Refreshing the lists
        refresh(devices)
        refresh(services)
        time.sleep(5)

    dev.unsubscribe(topic)
    dev.loop_stop()
    dev.disconnect()


if __name__ == "__main__":
    main()
