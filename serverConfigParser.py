from asyncio.windows_events import NULL
import configparser
from genericpath import exists

config_file_name = "config.ini"

# Read config data from the config file
def get_config_data() -> configparser.ConfigParser | None:
    
    # Get the config data to use
    if exists(config_file_name):
        print("Config file found...")
        config = configparser.ConfigParser()
        # Read the configuration file
        config.read(config_file_name)
        return config
    else:
        return None

# Check for a section/option combo in the config
def does_section_option_exist(config, section_to_check, option_to_check):
    return config.has_section(section_to_check) and config.has_option(section_to_check, option_to_check)

def read_ignored_logs():
    config = get_config_data()
    if config is not None:
        print("Got config...")
        if does_section_option_exist(config, "LogsToIgnore", "IGNORE_LOGS"):
            # return the list of logs to ignore
            return [log.strip() for log in config.get("LogsToIgnore", "IGNORE_LOGS").split(", ")]
        else:
            return []
    else:
        # logs to ignore not found
        return []

def read_server_config_to_list(section_to_read, option_to_read):
        config = get_config_data()
        if config is not None:
            print("READ SERVER CONFIG TO LIST: Got config...")
            if does_section_option_exist(config, section_to_read, option_to_read):
                # return the list of logs to ignore
                return [log.strip() for log in config.get(section_to_read, option_to_read).split(", ")]
            else:
                return []
        else:
            # logs to ignore not found
            return []


def read_server_settings():

        config = get_config_data()
        if config is not None:

            print("Config Sections:", config.sections())

            # Check for IP address in config
            if does_section_option_exist(config, "ServerSettings", "ip_address"):
                server_ip = config.get('ServerSettings', 'ip_address')
            else:
                print("Server Error: Unable to find ip address setting, default 127.0.0.1 will be used!")
                server_ip = "127.0.0.1"

            # Check for port in config
            if does_section_option_exist(config, "ServerSettings", "port"):
                server_port = config.get('ServerSettings', 'port')
            else:
                print("Server Error: Unable to find port setting, default 1233 will be used!")
                server_port = "1233"
            
            # check for port
            if does_section_option_exist(config, "ServerSettings", "max_clients"):
                max_clients = config.get('ServerSettings', 'max_clients')
            else:
                print("Server Error: Unable to find max client setting, default 5 will be used!")
                max_clients = "5"        

        else:
            print("No config file found, using defaults...")
            server_ip = "127.0.0.1"
            server_port = "1233"
            max_clients = "5"

        # Return a dictionary with the retrieved values
        config_values = {
            'server_ip': server_ip,
            'server_port': server_port,
            'max_clients': max_clients
        }

        print(f"Server Settings: {config_values}")
        return config_values

if __name__ == "__main__":
    # Call the function to read the configuration file
    config_data = read_server_settings()
    print(f"The server IP address is: {config_data['server_ip']}")
    print(f"The server port is: {config_data['server_port']}")