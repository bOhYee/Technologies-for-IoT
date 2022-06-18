import cherrypy
import json

data_list = []

class TemperatureWebService(object):
    exposed = True

    def GET(self):
        return json.dumps(data_list)

    def POST(self):
        contentType= cherrypy.request.headers['Content-Type']
        if contentType != "application/json":
            raise cherrypy.HTTPError(400, "Bad Request: wrong Content-Type")
        rawBody = cherrypy.request.body.read()
        data_list.append(json.loads(rawBody))


if __name__ == '__main__':
    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
        }
    }

    cherrypy.tree.mount(TemperatureWebService(), '/log', conf)
    cherrypy.config.update({'server.socket_host': '192.168.1.192'}) #Insert the server machine's local IP
    cherrypy.config.update({'server.socket_port': 8989})

    cherrypy.engine.start()
    cherrypy.engine.block()
