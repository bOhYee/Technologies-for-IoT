import json
import urllib3
import time

if __name__ == "__main__":
	http = urllib3.PoolManager()
	while True:
		msg = input()
		msg = msg.split(':')
		if msg[0] == 'T':
			try:
				val = float(msg[1].strip())
			except:
				print('Cannot convert to float')
				continue
			data = {"bn": "Yun",
					"e": [{
						"n": "temperature",
						"t": time.time(),
						"v": val,
						"u": "Celsius"
					}]}
			json_data = json.dumps(data).encode('utf-8')
			r = http.request('POST', 'http://192.168.1.192:8989/log', body=json_data, headers={'Content-Type': 'application/json'}) //Check the machine's local IP and paste it in http://<IP>:8989/log
			print(str(r.status))
		else:
			print("Unrecognized message", msg)
