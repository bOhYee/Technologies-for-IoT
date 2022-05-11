import cherrypy
std_params = ["value", "originalUnit", "targetUnit"]
std_unit = ["C", "F", "K"]

def check_params(std, target):
    for param in std:
        if not(param in target):
            return -1

    return 0

def check_values(std, target):
    i = 0
    for unit in target.values():
        if i != 0 and not(unit in std):
            return -1
        i += 1

    return 0

class TempConverter(object):

    exposed=True

    def GET(self, **args):
        oldValue = 0
        newValue = 0

        if(len(args) == 3):
            if check_params(std_params, args) == -1:
                raise cherrypy.HTTPError(400, "Parameters not valid")

            if check_values(std_unit, args) == -1:
                raise cherrypy.HTTPError(400, "Values not valid")

            oldValue = int(args.get(std_params[0]))
            if(args.get(std_params[1]) == std_unit[0] and args.get(std_params[2]) == std_unit[2]):
                newValue = oldValue + 273.15
        else:
            raise cherrypy.HTTPError(400, "Missing values")

        return newValue



def main():
    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True
        }
    }

    cherrypy.config.update({'server.socket_host': '127.0.0.1'})
    cherrypy.config.update({'server.socket_port': 8080})
    cherrypy.tree.mount (TempConverter(), '/converter', conf)
    cherrypy.engine.start()
    cherrypy.engine.block()


if __name__ == '__main__':
    main()
