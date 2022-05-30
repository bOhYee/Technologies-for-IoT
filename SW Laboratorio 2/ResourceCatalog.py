import cherrypy
import json


class ResourceCatalogServer:

    def __init__(self):
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
        cherrypy.engine.block()

class ResourceCatalog:

    exposed = True

    def __init__(self, subscription):
        self.subscription = subscription

    def GET(self, **args):
        return json.dumps(self.subscription)
