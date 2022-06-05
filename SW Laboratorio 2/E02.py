from Client import ClientREST
import time


# Main function
def main():
    c = ClientREST()

    # Imposing the recovery of the subscription data (should be implicit in the __init__ function)
    c.recover_subscription_data()

    while 1:
        # All devices
        print("Retrieving all devices registered...")
        print(c.retrieve_all_reg_devices())

        # Single device
        print("\nRetrieving a single device...")
        uuid = input("Digit a UUID: ")
        print(c.retrieve_device(uuid))

        # All users
        print("\nRetrieving all users registered...")
        print(c.retrieve_all_reg_users())

        # Single user
        print("\nRetrieving a single user...")
        uuid = input("Digit a UUID: ")
        print(c.retrieve_user(uuid))

        time.sleep(30)


if __name__ == "__main__":
    main()
