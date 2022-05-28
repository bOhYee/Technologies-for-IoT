import json
import urllib3
import time

if __name__ == "__main__":
    http = urllib3.PoolManager()
    while True:
        msg = input("Temperature: ")
        try:
            val = float(msg)
        except:
            print("Cannot convert to float")
            continue
        data = {"bn": "Yun",
                "e": [{
                    "n": "temperature",
                    "t": time.time(),
                    "v": val,
                    "u": "Celsius"
                }]}
        json_data = json.dumps(data).encode('utf-8')
        r = http.request('POST', 'http://127.0.0.1:8080/log', body=json_data, headers={'Content-Type': 'application/json'})
        print(str(r.status))
