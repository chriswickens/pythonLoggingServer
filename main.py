import socket
import threading
import time
from collections import deque
import serverConfigParser
from validLogLevels import VALID_LOGS
import logGenerator

# Mutex for safe logging
log_writer_mutex = threading.Lock()

# Another mutex for the rate limiting request_log
rate_limiting_dict_mutex = threading.Lock()

# Dictionary to track message timestamps by IP
request_log = {}
# Rate limiting options
rate_limit_window = 5  # seconds
max_requests = 2  # Allow 2 messages per window

def setup_server():
    """Set up the server socket using config data."""
    config_data = serverConfigParser.read_config()
    server_ip = config_data['server_ip']
    server_port = int(config_data['server_port'])
    max_clients = int(config_data['max_clients'])

    server_socket = socket.socket()

    try:
        server_socket.bind((server_ip, server_port))
    except socket.error as e:
        # This should be written to the log...FYI.
        print(f"Socket binding error: {e}")
        exit(1)

    print('Waiting for a Connection...')
    server_socket.listen(max_clients)
    return server_socket


def log_message(message):
    """Logs messages to a file using a mutex to prevent race conditions"""
    with log_writer_mutex:  # Grab the mutex
        with open("server_log.txt", "a") as log_file:
            log_file.write(message + "\n")


def check_for_rate_limiting(ip):
    """Check if the IP address has been rate limited."""
    current_time = time.time()

    # Grab the mutex for the rate limiting dictionary
    with rate_limiting_dict_mutex:
        if ip not in request_log:
            request_log[ip] = deque() # Create a double ended queue

        # Check for and remove timestamps in the queue for the IP if they are no longer needed
        while request_log[ip] and request_log[ip][0] < current_time - rate_limit_window:
            request_log[ip].popleft()

        # Otherwise if the number of requests in the log from a specific IP
        # are greater than or equal to the valid MAX number of requests in a timeframe
        # the IP is rate limited
        if len(request_log[ip]) >= max_requests:
            return True  # Rate limited

        # Append the current ip log with the current time
        # if the IP is not rate limited
        request_log[ip].append(current_time)
    return False


def client_connected(connection, client_address):
    """A thread that handles clients and their logging"""
    client_ip, client_port = client_address

    # Bool to ensure limited logging when a client is rate limited
    stop_log_rate_limited = False

    # Not needed, this is a logger
    # connection.send(b'Welcome to the Server\n')

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
                    log_message(f"Rate limited: {client_ip}:{client_port}")
                    stop_log_rate_limited = True
                continue
            else:
                stop_log_rate_limited = False

            # If the client is not in the rate limiting list
            # create a message and log the message
            message = logGenerator.generate_log_message(client_ip, client_port, data.decode('utf-8'))
            log_message(message)

        except Exception as e:
            # Produce an ERROR regarding the connection of the client
            message = logGenerator.generate_log_message(client_ip, client_port, f"FATAL|logger|FATAL ERROR : {client_ip}:{client_port} - {e}")
            log_message(message)
            break

    connection.close()
    # Log when the client has disconnected
    message = logGenerator.generate_log_message(client_ip, client_port, f"INFO|logger|Client Disconnected: {client_ip}:{client_port}")
    print(f'A client DISCONNECTED: {address[0]}:{address[1]}')
    log_message(message)


if __name__ == "__main__":

    requested_server_socket = setup_server()

    while True:
        client, address = requested_server_socket.accept()
        print(f'A client connected: {address[0]}:{address[1]}')

        # Start a thread for the new client
        threading.Thread(target=client_connected, args=(client, address), daemon=True).start()