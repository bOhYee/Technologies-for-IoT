import cherrypy
import json
import time
from conversion import *
import collections

CONVERSIONS = []
class ProducerWebService(object):
	exposed = True

	def POST(self, *uri, **params):
		global CONVERSIONS
		contentLength = cherrypy.request.headers['Content-Length']
		if contentLength=="0":
			raise cherrypy.HTTPError(400, "Bad Request: payload does not contain a body")
		rawBody = cherrypy.request.body.read(int(contentLength))
		jsonDict = json.loads(rawBody)
		if 'targetUnit' not in jsonDict.keys() or 'originalUnit' not in jsonDict.keys() or 'values' not in jsonDict.keys():
			raise cherrypy.HTTPError(404, "Bad Request: URI is not correctly formatted")
		if jsonDict['targetUnit'] not in ['C','K','F'] or jsonDict['originalUnit'] not in ['C','K','F']:
			raise cherrypy.HTTPError(404, "Bad Request: this service only supports Celsius, Fahrenhite and Kelvin measure units.")
		jsonDict['convertedValues'] = []
		for i in range(len(jsonDict['values'])):
			converted = Conversion(float(jsonDict['values'][i]),jsonDict['originalUnit'],jsonDict['targetUnit'])
			converted.convert()
			jsonDict['convertedValues'].append(converted.getTarget())
		CONVERSIONS = { 'values': jsonDict['values'],
						'convertedValues': jsonDict['convertedValues'],
						'originalUnit': jsonDict['originalUnit'],
						'targetUnit': jsonDict['targetUnit'],
						'timestamp': time.time()
						}
		print(CONVERSIONS)
		return json.dumps(CONVERSIONS)

if __name__ == '__main__':
	conf = {
		'/': {
			'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
		}
	}

	cherrypy.tree.mount(ProducerWebService(), '/converter', conf)
	cherrypy.config.update({'server.socket_host': '127.0.0.1'})
	cherrypy.config.update({'server.socket_port': 8080})

	cherrypy.engine.start()
	cherrypy.engine.block()
