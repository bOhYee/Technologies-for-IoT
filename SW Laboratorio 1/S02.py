import cherrypy
import json
from conversion import *


class ConvertTemperature(object):
    exposed = True

    def GET(self, *uri, **params):
        if len(uri) == 3 and len(params) == 0:
            if uri[1] != uri[2]:
                if uri[1] in std_unit and uri[2] in std_unit:
                    try:
                        c = Conversion(float(uri[0]), uri[1], uri[2])
                        c.convert()
                        data = {'originalValue': c.getValue(),
                                'originalUnit': c.getUnit(),
                                'targetUnit': c.get_tUnit(),
                                'targetValue': c.getTarget()
                                }
                        return json.dumps(data)
                    except:
                        raise cherrypy.HTTPError(404, "Error! Value is not a number.")
                else:
                    raise cherrypy.HTTPError(404, "Error! URI is not correctly formatted.")
            else:
                raise cherrypy.HTTPError(404, "Error! Invalid conversion.")
        else:
            raise cherrypy.HTTPError(404, "Error! URI parameters must be 3 and QUERY parameters must be 0.")


if __name__ == '__main__':
    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
        }
    }

    cherrypy.tree.mount(ConvertTemperature(), '/converter', conf)
    cherrypy.config.update({'server.socket_host': '127.0.0.1'})
    cherrypy.config.update({'server.socket_port': 8080})
    cherrypy.engine.start()
    cherrypy.engine.block()
