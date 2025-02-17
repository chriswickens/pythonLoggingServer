import socket
import threading
from validLogLevels import VALID_LOGS

# Server Configuration
host = '127.0.0.1'
port = 1233

# client ID tracking
current_id_number = 0

# Create Server Socket
ServerSocket = socket.socket()
try:
    ServerSocket.bind((host, port))
except socket.error as e:
    print(f"Socket binding error: {e}")
    exit(1)

print('Waiting for a Connection...')
ServerSocket.listen(5)

# Mutex for safe logging
log_lock = threading.Lock()

from collections import deque
import time
import threading

# Dictionary to track message timestamps per IP
rate_limit = {}
lock = threading.Lock()

# Settings
rate_limit_window = 5  # seconds
max_requests = 2  # Allow 2 messages per window
request_log = {}  # Dictionary to track requests per IP

def is_rate_limited(ip):
    # get the current time
    current_time = time.time()

    # check if the IP is NOT in the log
    if ip not in request_log:
        # Add the IP address to the request_log (deque() is NOT what you thought...)
        request_log[ip] = deque()

    # Remove old timestamps outside the rate limit window
    while request_log[ip] and request_log[ip][0] < current_time - rate_limit_window:
        request_log[ip].popleft()

    # If the length
    if len(request_log[ip]) >= max_requests:
        return True  # Rate limited

    # Otherwise, log the request and allow it
    request_log[ip].append(current_time)
    return False


def log_message(message):
    # Logs messages to a file safely using a mutex.
    log_lock.acquire()
    try:
        with open("server_log.txt", "a") as log_file:
            log_file.write(message + "\n")
    finally:
        log_lock.release()


def threaded_client(connection, client_address):
    client_ip_address = client_address[0]
    client_port = client_address[1]
    # Handles client communication and logs activity.
    connection.send(str.encode('Welcome to the Server\n'))

    # Logging idea: an index number for each client?

    while True:
        try:
            # receive data from the client
            data = connection.recv(2048)

            # if the data was null (blank?)
            if not data:
                break

            # check if the IP address is rate limited
            if is_rate_limited(client_ip_address):
                log_message(f"Rate limited: {client_ip_address}:{client_port}")
                continue


            # otherwise construct a message
            message = f"{client_ip_address}:{client_port} - {data.decode('utf-8')}"

            # write that message to the log file
            log_message(message)

            # send a reply to the client
            reply = 'Server Says: ' + data.decode('utf-8')

            # send all the data
            # connection.sendall(str.encode(reply))

        # if there was an error
        except Exception as e_error:
            log_message(f"Error with {client_ip_address}:{client_port} - {e_error}")
            break
    # close the connection and log that
    connection.close()
    log_message(f"Connection closed: {client_ip_address}:{client_port}")


# main loop
while True:
    # accept the client connection
    client, address = ServerSocket.accept()
    print(f'A client connected: {address[0]}:{address[1]}')
    log_message(f'New connection from {address[0]}:{address[1]}')

    # Run the threaded_client function using threading (multi client support)
    threading.Thread(target=threaded_client, args=(client, address), daemon=True).start()

ServerSocket.close()
exit(0)
