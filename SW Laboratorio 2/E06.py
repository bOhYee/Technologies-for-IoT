from Client import ClientMQTT
import time


# Main function
def main():
    c = ClientMQTT("Client_14")
    c.gen_start()

    while 1:
        # At every cycle we refresh the previously inserted devices and register a new device
        print("Refreshing devices...")
        # c.refresh_devices()
        print("Registering a new device...")
        c.gen_register_new_device()

        print("Waiting...")
        time.sleep(15)

    #c.gen_stop()


if __name__ == "__main__":
    main()
