import configparser
from datetime import datetime
from genericpath import exists

# Config file name
config_file_name = "config.ini"

""" Config file sections and options """
# Server Settings
config_server_settings_section = "ServerSettings"
config_server_settings_option_ip = "ip_address"
config_server_settings_option_port = "port"
config_server_settings_option_max_clients = "max_clients"

# Configuration sections/options expected in config.ini file
# Valid Log Types
config_valid_log_section = "ValidLogs"
config_valid_log_option = "VALID_LOGS_LIST"

# Log Arrangement Settings
config_log_field_arrangement_section = "LogFieldArrangement"
config_log_field_arrangement_option = "FIELD_ORDER"
config_log_field_time_stamp_format_option = "TIME_STAMP_FORMAT"

# # Logs to ignore Settings
config_logs_to_ignore_section = "LogsToIgnore"
config_logs_to_ignore_option = "IGNORE_LOGS"

# Rate limiting Settings
config_logs_rate_limit_section = "RateLimiting"
config_logs_rate_limit_window_option = "rate_limit_window"
config_logs_rate_limit_max_requests_option = "max_requests"

# Read config data from the config file
def get_config_data() -> configparser.ConfigParser | None:
    # Get the config data to use
    if exists(config_file_name):
        print("Config file found...")
        # Interpolation is set to None for reading time stamp formats from config.ini file
        config = configparser.ConfigParser(interpolation=None)
        # Read the configuration file
        config.read(config_file_name)
        return config
    else:
        print("Config file NOT found! Defaults will be used...")
        return None

# Check for a section/option combo in the config
def does_section_option_exist(config, section_to_check, option_to_check):
    return config.has_section(section_to_check) and config.has_option(section_to_check, option_to_check)

def read_server_config_to_int(section_to_read, option_to_read):
    config = get_config_data()
    if config and does_section_option_exist(config, section_to_read, option_to_read):
        return config.getint(section_to_read, option_to_read)
    return None


def read_server_config_to_list(section_to_read, option_to_read):
    config = get_config_data()
    if config and does_section_option_exist(config, section_to_read, option_to_read):
        return [log.strip() for log in config.get(section_to_read, option_to_read).split(",")]
    return []


def read_server_config_to_string(section_to_read, option_to_read):
    config = get_config_data()
    if config and does_section_option_exist(config, section_to_read, option_to_read):
        return config.get(section_to_read, option_to_read)
    return ""


def read_server_socket_settings():
    config = get_config_data()
    if config is not None:

        print("Config Sections:", config.sections())

        # Check for IP address in config
        if does_section_option_exist(config, config_server_settings_section, config_server_settings_option_ip):
            server_ip = config.get('ServerSettings', 'ip_address')
        else:
            print("Server Error: Unable to find ip address setting, default 127.0.0.1 will be used!")
            server_ip = "127.0.0.1"

        # Check for port in config
        if does_section_option_exist(config, config_server_settings_section, config_server_settings_option_port):
            server_port = config.get('ServerSettings', 'port')
        else:
            print("Server Error: Unable to find port setting, default 1233 will be used!")
            server_port = "1233"
        
        # check for port
        if does_section_option_exist(config, config_server_settings_section, config_server_settings_option_max_clients):
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
        "server_ip": server_ip,
        "server_port": server_port,
        "max_clients": max_clients
    }

    print(f"Server Settings: {config_values}")
    return config_values

if __name__ == "__main__":
    # Call the function to read the configuration file
    # config_data = read_server_socket_settings()
    # print(f"The server IP address is: {config_data['server_ip']}")
    # print(f"The server port is: {config_data['server_port']}")

    # time_stamp_test = get_config_data()
    # dateString = read_server_config_to_string("LogFieldArrangement", "TIME_STAMP_FORMAT")
    # print(f"{datetime.now().strftime(dateString)}")

    print(read_server_config_to_int("RateLimiting", "rate_limit_window"))
    print(read_server_config_to_int("RateLimiting", "max_requests"))