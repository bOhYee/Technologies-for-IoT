from GlobalConst import *
import requests
import uuid
import time
import json


class Client:

    def __init__(self):
        self.devices_maintained = []
        self.subscription = {}

    def recover_subscription_data(self):
        req = requests.get(RESOURCE_CATALOG_ADDRESS)
        # Raises an exception if it cannot reach the ResourceCatalog
        if req.status_code != 200:
            req.raise_for_status()

        # Verify that the response contains a JSON as payload
        if req.headers["Content-type"] != "application/json":
            raise ValueError("Error: response received does not include a JSON.")

        self.subscription = req.json()

    def get_subscription_data(self):
        return self.subscription

    def register_new_device(self):
        # Creation of the new device
        new_device = {}
        new_device["uuid"] = str(uuid.uuid1())
        new_device["ep"] = "REST"
        new_device["res"] = ["temperature", "pressure"]
        new_device["t"] = str(time.time())

        # Definition of the header of the request
        header = {}
        header["Content-Type"] = "application/json"

        self.devices_maintained.append(new_device)
        req = requests.post(self.subscription["REST"]["device"], headers=header, data=json.dumps(new_device))
        # If the request is invalid, raise an Exception
        if req.status_code != 200:
            req.raise_for_status()

    def refresh_devices(self):
        # If the request is invalid, raise an Exception
        header = {}
        header["Content-Type"] = "application/json"
        url = self.subscription["REST"]["devices"]

        for dev in self.devices_maintained:
            req = requests.put(url, headers=header, data=json.dumps(dev))
            # If the request is invalid, raise an Exception
            if req.status_code != 200:
                req.raise_for_status()


# Main
def main():
    c = Client()
    c.recover_subscription_data()

    while 1:
        c.register_new_device()
        c.refresh_devices()

        time.sleep(60)


if __name__ == "__main__":
    main()
