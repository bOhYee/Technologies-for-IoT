import cherrypy
import json
from Conversion import *
std_params = ["value", "originalUnit", "targetUnit"]
std_unit = ["C", "F", "K"]


def check_params(std, target):
    for param in target:
        if param not in std:
            return -1

    return 0


def check_values(params, std, target):
    if target[params[1]] in std and target[params[2]] in std:
        return 0
    else:
        return -1


class TempConverter(object):

    exposed=True

    def GET(self, **args):
        oldValue = 0
        newValue = 0
        dictToExp = {}

        if len(args) == 3:
            if check_params(std_params, args) == -1:
                raise cherrypy.HTTPError(400, "Parameters not valid")

            if check_values(std_params, std_unit, args) == -1:
                raise cherrypy.HTTPError(400, "Values not valid")

            oldValue = int(args.get(std_params[0]))
            conv = Conversion(oldValue, args.get(std_params[1]), args.get(std_params[2]))
            newValue = conv.getTarget()

            dictToExp["origValue"] = oldValue
            dictToExp["origUnit"] = args.get(std_params[1])
            dictToExp["targetValue"] = newValue
            dictToExp["targetUnit"] = args.get(std_params[2])
            print(dictToExp)
            return json.dumps(dictToExp)
        else:
            raise cherrypy.HTTPError(400, "Missing values")


def main():
    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True
        }
    }

    cherrypy.config.update({'server.socket_host': '127.0.0.1'})
    cherrypy.config.update({'server.socket_port': 5605})
    cherrypy.tree.mount (TempConverter(), '/converter', conf)
    cherrypy.engine.start()
    cherrypy.engine.block()


if __name__ == '__main__':
    main()
