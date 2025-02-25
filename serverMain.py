"""
FILE : serverMain.py
PROJECT : SENG2040 Assignment 3
Programmers : Chris Wickens, Melissa Reyes
First Version : Feb/17/2025
Description : A simple logging server that allows a client to connect
and print out specific types of logs. It uses a config.ini file to control most
of its configuration options.
Intended to be used with logGenerator.py and serverConfigParser.py

Contains the following functions:
get_ignored_logs_config()
get_rate_limiting_config()
setup_server()
is_log_type_ignored(message)
log_message(message)
check_for_rate_limiting(ip)
assign_client_id(client_connection_info)
client_connected(connection, client_address)

"""

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
rate_limit_window = 0  # X seconds
max_requests = 0  # Allow X messages per window

# Client tracking
client_id_number = 0  # Increments based on number of clients who have connected
client_id_dictionary = {}  # Dictionary of client IDs and IP addresses associated with them

"""
get_ignored_logs_config():
Reads the ignored log types from the server configuration and stores them globally.

This function retrieves the list of log types that should be ignored from the configuration file
and assigns them to the global variable `ignored_logs`.
"""
def get_ignored_logs_config():
    global ignored_logs
    ignored_logs = serverConfigParser.read_server_config_to_list(
        serverConfigParser.config_logs_to_ignore_section, 
        serverConfigParser.config_logs_to_ignore_option)

"""
get_rate_limiting_config():
Reads the rate limiting settings from the server configuration and stores them globally.

This function retrieves the rate limiting window and the maximum number of requests allowed
within that window. If no valid values are found, it assigns default values.

Global Variables:
rate_limit_window (int): The time window for rate limiting (default: 5 seconds).
max_requests (int): The maximum number of requests allowed within the window (default: 2).
"""
def get_rate_limiting_config():
    global rate_limit_window
    global max_requests
    rate_limit_window = serverConfigParser.read_server_config_to_int(
        serverConfigParser.config_rate_limit_section, 
        serverConfigParser.config_rate_limit_window_option)
    
    max_requests = serverConfigParser.read_server_config_to_int(
        serverConfigParser.config_rate_limit_section, 
        serverConfigParser.config_rate_limit_max_requests_option)

    # If None was returned (no valid value)
    if rate_limit_window == None:
        rate_limit_window = 5
    if max_requests == None:
        max_requests = 2

"""
setup_server():
Initializes and sets up the server socket using configuration data.

This function reads server socket settings, binds the server socket to the specified IP and port,
and starts listening for incoming connections.

Returns:
socket.socket: The configured server socket.
"""
def setup_server() -> socket.socket:
    """Set up the server socket using config data."""
    
    # Setup the ignored logs from config
    get_ignored_logs_config()

    # Setup rate limiting
    get_rate_limiting_config()

    # Get config data
    config_data = serverConfigParser.read_server_socket_settings()

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
    print("=====================================================")
    print(f'Server Details:\nServer IP {server_ip}\nServer Port: {server_port}\nServer started!\nWaiting for a Connection...')
    print("=====================================================")
    message = logGenerator.generate_log_message("INFO", "SERVER", server_ip, server_port, "Server started...")
    log_message(message)
    server_socket.listen(max_clients)
    return server_socket

"""
is_log_type_ignored(message):
Checks whether the log type in the given message should be ignored.

Parameters:
message (str): A JSON-formatted log message.

Returns:
bool: True if the log type is in the ignored list, False otherwise.
"""
def is_log_type_ignored(message) -> bool:
    # Load the message as a JSON object
    message_object = json.loads(message)
    log_type = message_object.get("log_type", "")

    # Check if log_type should be ignored
    if log_type in ignored_logs:
        return True
    else:
        return False

"""
log_message(message):
Logs a message to a file, ensuring thread safety using a mutex.

This function first checks if the message should be ignored. If not, it writes the log to
a file using a mutex to prevent race conditions.

Parameters:
message (str): The log message to be written to the file.
"""
def log_message(message) -> None:
    """Logs messages to a file using a mutex to prevent race conditions"""
    """ THIS IS WHERE YOU NEED TO CHECK IF THE MESSAGE WILL EVEN BE LOGGED! """
    # Check if log is to be ignored
    ignored_message = is_log_type_ignored(message)
    if not ignored_message:
        with log_writer_mutex:  # Grab the mutex
            with open("server_log.txt", "a") as log_file:
                log_file.write(message + "\n")
    # else: # Dont need this output really...
    #     print("Message not printed, due to ignoring it!")

"""
check_for_rate_limiting(ip):
Checks if an IP address is rate limited based on recent request timestamps.

This function keeps track of request timestamps for each IP address and ensures that requests
exceeding the allowed threshold within the configured time window are blocked.

Parameters:
ip (str): The IP address of the client.

Returns:
bool: True if the IP is rate limited, False otherwise.
"""
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

"""
assign_client_id(client_connection_info):
Assigns a unique client ID to a given client connection.

This function checks if the client connection information already has an assigned ID.
If not, it assigns a new unique ID and stores it in a dictionary.

Parameters:
client_connection_info (tuple): The client's connection details (IP and port).

Returns:
Any: The assigned client ID.
"""
# function to assign an IP address a client ID
def assign_client_id(client_connection_info) -> Any:
    global client_id_number
    with client_id_list_mutex:
        if client_connection_info not in client_id_dictionary:
            client_id_number += 1
            client_id_dictionary[client_connection_info] = client_id_number
        return client_id_dictionary[client_connection_info]  # Always return the assigned ID


"""
client_connected(connection, client_address):
Handles a client connection in a separate thread.

This function manages client communication, checks for rate limiting, and logs messages.
It continuously listens for incoming data until the client disconnects.

Parameters:
connection (socket.socket): The socket object representing the client connection.
client_address (tuple): The client's IP address and port.
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

"""
Main Function
"""
if __name__ == "__main__":

    requested_server_socket = setup_server()

    while True:
        client, address = requested_server_socket.accept()
        print(f'A client connected: {address[0]}:{address[1]}')

        # Start a thread for the new client
        threading.Thread(target=client_connected, args=(client, address), daemon=True).start()