# Testing various pyton things!

import re
import json

valid_logging = ["INFO", "DEBUG"]

client_message = "INFO|ClientName|Hello there!"


def generate_log_message(client_ip_address, client_port, received_client_message, message_type):
    print(f'IP: {client_ip_address}\nPort: {client_port}\nMessage: {received_client_message}')

    split_message = received_client_message.split("|")

    if split_message[0] in valid_logging:
        print("Create JSON object with data...\n")
        message_object = {
            "type": split_message[0],
            "ip_address": client_ip_address,
            "port": client_port,
            "message": client_message
        }
        print(json.dumps(message_object))
        print(json.dumps(message_object))
    return


generate_log_message("192.111.111.1", 1222, client_message, "none")

exit(0)