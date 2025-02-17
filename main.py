import socket
import threading
import validLogLevels


# Server Configuration
host = '127.0.0.1'
port = 1233

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


def log_message(message):
    # Logs messages to a file safely using a mutex.
    log_lock.acquire()
    try:
        with open("server_log.txt", "a") as log_file:
            log_file.write(message + "\n")
    finally:
        log_lock.release()


def threaded_client(connection, address):
    # Handles client communication and logs activity.
    connection.send(str.encode('Welcome to the Server\n'))
    while True:
        try:
            # receive data from the client
            data = connection.recv(2048)

            # if the data was null (blank?)
            if not data:
                break

            # otherwise construct a message
            message = f"{address[0]}:{address[1]} - {data.decode('utf-8')}"

            # write that message to the log file
            log_message(message)

            # send a reply to the client
            reply = 'Server Says: ' + data.decode('utf-8')

            # send all the data
            connection.sendall(str.encode(reply))

        # if there was an error
        except Exception as e:
            log_message(f"Error with {address[0]}:{address[1]} - {e}")
            break
    # close the connection and log that
    connection.close()
    log_message(f"Connection closed: {address[0]}:{address[1]}")


while True:
    client, address = ServerSocket.accept()
    print(f'Connected to: {address[0]}:{address[1]}')
    log_message(f'New connection from {address[0]}:{address[1]}')
    threading.Thread(target=threaded_client, args=(client, address), daemon=True).start()

ServerSocket.close()
