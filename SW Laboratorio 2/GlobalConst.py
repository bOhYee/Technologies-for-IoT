# Constants to use to avoid error between Clients and ResourceCatalogs configuration

RESOURCE_CATALOG_HOST = "127.0.0.1"
RESOURCE_CATALOG_PORT = 8080
RESOURCE_CATALOG_ADDRESS = "http://127.0.0.1:8080/"
SUBSCRIPTION = {
                    "REST": {
                        "device": "http://127.0.0.1:8080/devices/subscription",
                        "service": "http://127.0.0.1:8080/services/subscription",
                        "user": "http://127.0.0.1:8080/users/subscription"
                    },
                    "MQTT": {
                        "device": {
                            "hostname": "iot.eclipse.org",
                            "port": "1883",
                            "topic": "tiot/group14/catalog/devices/subscription"
                        }

                    }
                }

