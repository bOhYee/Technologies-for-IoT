from Client import ClientREST
import time


# Main function
def main():
    c = ClientREST()

    # Imposing the recovery of the subscription data (should be implicit in the __init__ function)
    c.recover_subscription_data()

    while 1:
        # At every cycle we refresh the previously inserted devices and register a new device
        print("Refreshing devices...")
        c.refresh_devices()
        print("Registering a new device...")
        c.register_new_device()

        print("Waiting...")
        time.sleep(60)


if __name__ == "__main__":
    main()
