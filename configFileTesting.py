import configparser


def read_config():
    # Create a ConfigParser object
    config = configparser.ConfigParser()

    # Read the configuration file
    config.read('config.ini')

    # Access values from the configuration file
    server_ip = config.get('ServerSettings', 'ipAddress')
    server_port = config.get('ServerSettings', 'port')

    # Return a dictionary with the retrieved values
    config_values = {
        'server_ip': server_ip,
        'server_port': server_port,
    }

    return config_values


if __name__ == "__main__":
    # Call the function to read the configuration file
    config_data = read_config()
    print(f"The server IP address is: {config_data['server_ip']}")
    print(f"The server port is: {config_data['server_port']}")