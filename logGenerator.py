import re
import json
from validLogLevels import VALID_LOGS
from datetime import datetime

# client_message = "DEBUG|ClientName|Hello there!"

# Client list globals
client_id_number = 0  # Increments based on number of clients who have connected
client_id_dictionary = {}  # Dictionary of client IDs and IP addresses associated with them


# function to assign an IP address a client ID
def assign_client_id(ip_to_check):
    global client_id_number
    if ip_to_check not in client_id_dictionary:
        client_id_number += 1
        client_id_dictionary[ip_to_check] = [client_id_number]
        # print(f"Client ID assigned: {client_id_dictionary[ip_to_check]}")
    return client_id_dictionary[ip_to_check]  # Always return the assigned ID


def generate_log_message(client_ip_address, client_port, received_client_message):

    # Get the client ID generated
    client_id = assign_client_id(client_ip_address)

    message_identifier = 0
    message_client_name = 1
    message_data = 2

    print(f'LOG GENERATOR: IP: {client_ip_address} - Port: {client_port} - Message: {received_client_message}')

    # Get the client ID, if not found return None
    # client_id = client_id_dictionary.get(client_ip_address, None)

    print(f"Client ID: {client_id}")
    # if None was returned, log an error instead!
    if client_id is None:
        # this is where you would call a log and report the IP address was not assigned a CLIENT_ID
        return "Error: Client ID not found!"

    # probably an ELSE for the if statement above, so if the ID is not found, it writes an error about that
    current_time = datetime.now()
    split_message = received_client_message.split("|")

    if len(split_message) < 3:
        return json.dumps({
            "type": "ERROR",
            "request_type": "INVALID",
            "time_stamp": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "client_id": assign_client_id(client_ip_address),
            "ip_address": client_ip_address,
            "port": client_port,
            "message": "Invalid log format"
        })

    # Check if the requested log message type exists in VALID_LOGS
    if split_message[message_identifier] in VALID_LOGS:

        print("Create JSON object with data...\n")

        # From validLogLevels.py
        # VALID_LOGS = ["TRACE", "DEBUG", "INFO", "WARN", "ERROR", "FATAL"]

        message_object = {"time_stamp": current_time.strftime("%d/%m/%Y %H:%M:%S")}  # Create the blank message object to start

        match split_message[message_identifier]:
            case "TRACE":
                print("Trace Message...\n")
                message_object["request_type"] = split_message[message_identifier]
            case "DEBUG":
                print("Debug Message...\n")
                message_object["request_type"] = split_message[message_identifier]
            case "INFO":
                print("Info Message...\n")
                message_object["request_type"] = split_message[message_identifier]
            case "WARN":
                # Ex: Something happened, but the program can recover (file not found for example)
                print("Warn Message...\n")
                message_object["request_type"] = split_message[message_identifier]
            case "ERROR":
                print("Error Message...\n")
                message_object["request_type"] = split_message[message_identifier]
            case "FATAL":
                print("Fatal Message...\n")
                message_object["request_type"] = split_message[message_identifier]
        print(f"Message Object: {message_object}")
        message_object.update({
            "client_id": client_id,
            # "client_name": split_message[message_client_name],
            # "ip_address": client_ip_address,
            # "port": int(client_port),
            # "message": split_message[message_data]
        })

    # If the requested log message type does NOT exist, return an error logging the details requested
    # by the client
    else:
        message_object = {
            "type": "ERROR",
            "request_type": split_message[message_identifier],
            "time_stamp": current_time.strftime("%d/%m/%Y %H:%M:%S"),
            "client_id": client_id,
            "ip_address": client_ip_address,
            "port": client_port,
            "message": split_message[message_data]
        }

    # Return the constructed json string to print
    return json.dumps(message_object)


# if __name__ == "__main__":
#     # Assign client IDs correctly
#     # When a client connects, you need to assign it an ID
#     # the ID will be used when printing logging information
#     client_id_dictionary["192.168.0.1"] = assign_client_id("192.168.0.1")
#     client_id_dictionary["192.168.0.55"] = assign_client_id("192.168.0.55")
#
#     print(f"The client ID list: \n{client_id_dictionary}")
#
#     # How to generate the message to be put in the log file
#     message = generate_log_message("192.168.0.55", 1234, client_message)
#     print(f"The output from generate_log_message: \n{message}")
#     exit(0)
