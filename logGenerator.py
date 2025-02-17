import re
import json
from validLogLevels import VALID_LOGS
from datetime import datetime

# Client list globals
client_id_number = 0  # Increments based on number of clients who have connected
client_id_dictionary = {}  # Dictionary of client IDs and IP addresses associated with them


# function to assign an IP address a client ID
def assign_client_id(ip_to_check):
    global client_id_number
    if ip_to_check not in client_id_dictionary:
        client_id_number += 1
        client_id_dictionary[ip_to_check] = client_id_number
        # print(f"Client ID assigned: {client_id_dictionary[ip_to_check]}")
    return client_id_dictionary[ip_to_check]  # Always return the assigned ID


def generate_log_message(client_ip_address, client_port, received_client_message):

    # Get the client ID generated
    client_id = assign_client_id(client_ip_address)

    message_identifier = 0
    message_client_name = 1
    message_data = 2


    # if None was returned, log an error instead!
    if client_id is None:
        # this is where you would call a log and report the IP address was not assigned a CLIENT_ID
        return "Error: Client ID not found!"

    # probably an ELSE for the if statement above, so if the ID is not found, it writes an error about that
    # split_message = received_client_message.split("|") # used because you love networking messages...RIGHT.
    current_time = datetime.now()

    # get the value from the message for the log type requested
    # log_type = split_message[message_identifier] # This is the split you were using before, dont bother now....
    # print(f"Log Type: {log_type}")


    # THIS CODE WAS FOR WHEN THERE WAS A CLIENT NAME AND DATA...ASK ED!!
    """ASK ED ABOUT THIS CODE, do we need to care about this? Probably not....as per usual, Melissa is prolly correct....."""
    # received_client_name = "UnknownClientName"
    # received_client_data = "NoDataReceived"

    # match len(split_message):
    #     case 2:
    #         received_client_name = split_message[message_client_name]
    #     case 3 | _:
    #         received_client_name = split_message[message_client_name]
    #         received_client_data = split_message[message_data]

    message_object = {"time_stamp": current_time.strftime("%d/%m/%Y %H:%M:%S")}  # Create the blank message object to start

    match received_client_message:
        case "TRACE":
            print("Trace Message...\n")
            message_object["log_level"] = received_client_message
        case "DEBUG":
            print("Debug Message...\n")
            message_object["log_level"] = received_client_message
        case "INFO":
            print("Info Message...\n")
            message_object["log_level"] = received_client_message
        case "WARN":
            # Ex: Something happened, but the program can recover (file not found for example)
            print("Warn Message...\n")
            message_object["log_level"] = received_client_message
        case "FATAL":
            print("Fatal Message...\n")
            message_object["log_level"] = received_client_message
        case "ERROR":
            print("Error Message...\n")
            message_object["log_level"] = received_client_message
        case _:
            print(f"UNDERSCORE - Error Message...{received_client_message}\n")
            message_object["requested_type"] = received_client_message
            message_object["log_level"] = "UNKNOWN"

    # print(f"Message Object: {message_object}")

    # Form the rest of the message after the request_type has been added
    message_object.update({
        "client_id": client_id,
        # "client_name": received_client_name,
        "ip_address": client_ip_address,
        "port": client_port,
        # "message": received_client_data
    })

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
