import re
import json
from validLogLevels import VALID_LOGS
from datetime import datetime

valid_logging = ["INFO", "DEBUG"]

client_message = "INFO|ClientName|Hello there!"

# Client list globals
client_id_number = 0
client_id_list = {}


# function to assign an IP address a client ID
def assign_client_id(ip_to_check):
    global client_id_number
    if ip_to_check not in client_id_list:
        client_id_number += 1
        client_id_list[ip_to_check] = [client_id_number]
    return client_id_list[ip_to_check][0]  # Always return the assigned ID


def generate_log_message(client_ip_address, client_port, received_client_message):
    message_identifier = 0
    message_client_name = 1
    message_data = 2
    print(f'IP: {client_ip_address}\nPort: {client_port}\nMessage: {received_client_message}')

    # Get the client ID, if not found return None
    client_id = client_id_list.get(client_ip_address, None)
    # if None was returned, log an error instead!
    if client_id is None:
        # this is where you would call a log and report the IP address was not assigned a CLIENT_ID
        return "Error: Client ID not found!"

    # probably an ELSE for the if statement above, so if the ID is not found, it writes an error about that
    current_time = datetime.now()
    split_message = received_client_message.split("|")

    if split_message[message_identifier] in VALID_LOGS:
        print("Create JSON object with data...\n")
        message_object = {
            "client_id": client_id,
            "time_stamp": current_time.strftime("%d/%m/%Y %H:%M:%S"),
            "type": split_message[message_identifier],
            "client_name": split_message[message_client_name],
            "ip_address": client_ip_address,
            "port": client_port,
            "message": split_message[message_data]
        }

        # Where you would PRINT to the log with the data
        return json.dumps(message_object)
    else:
        return "Invalid message type!"


# Assign client IDs correctly
client_id_list["192.168.0.1"] = assign_client_id("192.168.0.1")
client_id_list["192.168.0.55"] = assign_client_id("192.168.0.55")

print(f"The client ID list: \n{client_id_list}")

# How to generate the message to be put in the log file
message = generate_log_message("192.168.0.55", 1234, client_message)
print(f"The output from generate_log_message: \n{message}")
exit(0)
