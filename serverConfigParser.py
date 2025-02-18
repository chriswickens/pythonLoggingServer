import configparser


def read_config():
    # Create a ConfigParser object
    config = configparser.ConfigParser()

    # Read the configuration file
    config.read('config.ini')

    # Access values from the configuration file
    server_ip = config.get('ServerSettings', 'ip_address')
    server_port = config.get('ServerSettings', 'port')
    max_clients = config.get('ServerSettings', 'max_clients')

    # Return a dictionary with the retrieved values
    config_values = {
        'server_ip': server_ip,
        'server_port': server_port,
        'max_clients': max_clients
    }

    return config_values


if __name__ == "__main__":
    # Call the function to read the configuration file
    config_data = read_config()
    print(f"The server IP address is: {config_data['server_ip']}")
    print(f"The server port is: {config_data['server_port']}")