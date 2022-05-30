import cherrypy
import json
import time

dev_list = []
ser_list = []
user_list = []

class ResourceCatalogServer:

    def __init__(self):
        self.manageDevicesThread = threading.Thread(target=)
        self.subscription = {
            "REST": {
                "device"  : "http://192.168.0.10:8080/devices/subscription",
                "service" : "http://192.168.0.10:8080/services/subscription",
                "user"    : "http://192.168.0.10:8080/users/subscription"
            },
            "MQTT":{
                "device"  : {
                    "hostname" : "iot.eclipse.org",
                    "port" : "1883",
                    "topic" : "tiot/14/catalog/devices/subscription"
                }
            }
        }
        self.conf = {
            "/" : {
                "request.dispatch":cherrypy.dispatch.MethodDispatcher(),
                "tools.sessions.on": True
            }
        }

        cherrypy.config.update({"server.socket.host":"127.0.0.1"})
        cherrypy.config.update({"server.socket_port": 12012})
        cherrypy.tree.mount(ResourceCatalog(self.subscription), "/", self.conf)
        cherrypy.engine.start()

        while True:
            refresh(dev_list)
            refresh(ser_list)
            time.sleep(45)

    def refresh(self, listToRefresh):
        counter = 0
        toDelete = []
        curr_time = time.time()

        for obj in listToRefresh:
            diff_time = curr_time - obj["timestamp"]
            if diff_time > 120 :
                toDelete.append(counter)

            counter += 1

        for i in toDelete:
            del listToRefresh[i]


class ResourceCatalog:

    exposed = True

    def __init__(self, subscription):
        self.subscription = subscription

    def GET(self, **args):
        return json.dumps(self.subscription)
