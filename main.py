import json
import socket
import threading
import time
from collections import deque
from typing import Any
import serverConfigParser
import logGenerator

# Mutex's's
log_writer_mutex = threading.Lock() # for writing the log file
rate_limiting_dict_mutex = threading.Lock() # for writing to the rate limiting dictionary
client_id_list_mutex = threading.Lock() # for writing to the client_id_list

# Dictionary to track message timestamps by IP
rate_limit_log = {}

# List for ignored logs
ignored_logs = []

# Rate limiting options
# Put these in the config file
rate_limit_window = 5  # X seconds
max_requests = 2  # Allow X messages per window

# Client tracking
client_id_number = 0  # Increments based on number of clients who have connected
client_id_dictionary = {}  # Dictionary of client IDs and IP addresses associated with them

def get_ignored_logs_config():
    global ignored_logs
    ignored_logs = serverConfigParser.read_server_config_to_list("LogsToIgnore", "IGNORE_LOGS")

def setup_server() -> socket.socket:
    """Set up the server socket using config data."""
    
    get_ignored_logs_config()

    # Get config data
    config_data = serverConfigParser.read_server_settings()

    # Assign server settings
    server_ip = config_data['server_ip']
    server_port = int(config_data['server_port'])
    max_clients = int(config_data['max_clients'])

    server_socket = socket.socket()

    try:
        server_socket.bind((server_ip, server_port))
    except socket.error as e:
        # This should be written to the log...FYI.
        print(f"Socket binding error: {e}")
        message = logGenerator.generate_log_message("FATAL", "NONE", "NONE", "NONE", f"Socket Binding Error: {e}")
        log_message(message)
        exit(1)

    print('Server started!\nWaiting for a Connection...')
    message = logGenerator.generate_log_message("INFO", "SERVER", server_ip, server_port, "Server started...")
    log_message(message)
    server_socket.listen(max_clients)
    return server_socket

def is_log_type_ignored(message) -> bool:
    # # Create the object
    # config = configparser.ConfigParser()
    # config_file_name = "config.ini"

    # # Read the config.ini file
    # config.read(config_file_name)

    # Storage for logs to be ignored


    # if config.has_section("LogsToIgnore"):
    #     if not config.has_option("LogsToIgnore", "IGNORE_LOGS"):
    #         print("Server Error: No IGNORE_LOGS option in config.ini - ALL LOG TYPES WILL BE RECORDED!")
    #         return False
    #     else:
    #         # Get the value and split it correctly
    #         ignored_logs = [log.strip() for log in config.get("LogsToIgnore", "IGNORE_LOGS").split(", ")]
    #         print("IGNORE_LOGS gotten:", ignored_logs)
    # else:
    #     print("Server Error: No LogsToIgnore SECTION in config.ini - ALL LOG TYPES WILL BE RECORDED!")
    #     return False
    
    # print("check_ignored_log_types(): It got here, the list exists! Use it!")

    # Load the message as a JSON object
    message_object = json.loads(message)
    log_type = message_object.get("log_type", "")
    
    # print(f"CHECK IGNORE DEBUG: log_type='{log_type}', ignored_logs={ignored_logs}")

    # Check if log_type should be ignored
    if log_type in ignored_logs:
        # print("IGNORE THE LOG!")
        return True
    else:
        # print("PRINT THE LOG!!")
        return False

def log_message(message) -> None:
    """Logs messages to a file using a mutex to prevent race conditions"""
    # print("MESSAGE IN LOG_MESSAGE: ", message)
    """ THIS IS WHERE YOU NEED TO CHECK IF THE MESSAGE WILL EVEN BE LOGGED! """
    # Check if log is to be ignored
    ignored_message = is_log_type_ignored(message)
    if not ignored_message:
        with log_writer_mutex:  # Grab the mutex
            with open("server_log.txt", "a") as log_file:
                log_file.write(message + "\n")
    else: # Dont need this output really...
        print("Message not printed, due to ignoring it!")

def check_for_rate_limiting(ip) -> bool:
    """Check if the IP address has been rate limited."""
    current_time = time.time()

    # Grab the mutex for the rate limiting dictionary
    with rate_limiting_dict_mutex:
        if ip not in rate_limit_log:
            rate_limit_log[ip] = deque() # Create a double ended queue for each IP

        # Check if the IP exists in the queue
        # and if the timestamp for its last message is less than the current_time minus the rate_limit_window
        while rate_limit_log[ip] and rate_limit_log[ip][0] < current_time - rate_limit_window:
            rate_limit_log[ip].popleft() # Pop off the oldest time stamp

        # Otherwise if the number of requests in the log from a specific IP
        # are greater than or equal to the valid MAX number of requests in a timeframe
        # the IP is rate limited
        if len(rate_limit_log[ip]) >= max_requests:
            return True  # Rate limited

        # Append the current ip log with the current time
        # if the IP is not rate limited
        rate_limit_log[ip].append(current_time)
    return False

# function to assign an IP address a client ID
def assign_client_id(client_connection_info) -> Any:
    global client_id_number
    with client_id_list_mutex:
        if client_connection_info not in client_id_dictionary:
            client_id_number += 1
            client_id_dictionary[client_connection_info] = client_id_number
            # print(f"Client ID assigned: {client_id_dictionary[ip_to_check]}")
        return client_id_dictionary[client_connection_info]  # Always return the assigned ID


"""
Function that handles client connections
"""
def client_connected(connection, client_address) -> None:
    """A thread that handles clients and their logging"""
    client_ip, client_port = client_address

    # get a client id for this IP
    # This did send the client_ip, but I wanted to try sending the address to allow 
    # multiple clients from one IP but different ports
    client_id = assign_client_id(client_address)

    # Bool to ensure limited logging when a client is rate limited
    stop_log_rate_limited = False

    # Log their connection
    message = logGenerator.generate_log_message("INFO", client_id, client_ip, client_port, "Client connected to server")
    log_message(message)


    """The main loop"""
    while True:
        try:
            data = connection.recv(2048)
            # If there was no data sent
            if not data:
                break

            # Check to see if the client has been spamming the logger
            if check_for_rate_limiting(client_ip):
                if not stop_log_rate_limited:
                    # log_message(f"Rate limited: {client_ip}:{client_port}")
                    message = logGenerator.generate_log_message("WARN", client_id, client_ip, client_port, "Client is RATE LIMITED")
                    log_message(message)
                    stop_log_rate_limited = True
                continue
            else:
                stop_log_rate_limited = False

            # If the client is not in the rate limiting list
            # create a message and log the message
            message = logGenerator.generate_log_message(data.decode('utf-8'), client_id, client_ip, client_port)
            log_message(message)

        except Exception as e:
            # Produce an ERROR regarding the connection of the client
            message = logGenerator.generate_log_message("FATAL", client_id, client_ip, client_port, f"Crtitical socket error - {e}")
            log_message(message)
            break

    connection.close()
    # Log when the client has disconnected
    message = logGenerator.generate_log_message("INFO", client_id, client_ip, client_port, f"Client Disconnected from server")
    print(f'A client DISCONNECTED: {address[0]}:{address[1]}')
    log_message(message)


if __name__ == "__main__":

    requested_server_socket = setup_server()

    while True:
        client, address = requested_server_socket.accept()
        print(f'A client connected: {address[0]}:{address[1]}')

        # Start a thread for the new client
        threading.Thread(target=client_connected, args=(client, address), daemon=True).start()