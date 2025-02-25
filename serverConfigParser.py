"""
FILE : serverConfigParser.py
PROJECT : SENG2040 Assignment 3
Programmers : Chris Wickens, Melissa Reyes
First Version : Feb/17/2025
Description : Contains the logic to parse configuration details from a config.ini file.
If no config.ini file is found, sensible defaults are used to setup the server.

Functions:
get_config_data()
does_section_option_exist(config, section_to_check, option_to_check)
read_server_config_to_int(section_to_read, option_to_read)
read_server_config_to_list(section_to_read, option_to_read)
read_server_config_to_string(section_to_read, option_to_read)
read_server_socket_settings()
"""
import configparser
from genericpath import exists

# Config file name
config_file_name = "config.ini"
server_default_ip = "127.0.0.1"
server_default_port = "1233"
server_default_max_clients = "5"

""" Config file sections and options """
# Server Settings
config_server_settings_section = "ServerSettings"
config_server_settings_option_ip = "ip_address"
config_server_settings_option_port = "port"
config_server_settings_option_max_clients = "max_clients"

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
config_rate_limit_section = "RateLimiting"
config_rate_limit_window_option = "rate_limit_window"
config_rate_limit_max_requests_option = "max_requests"

"""
get_config_data():
Reads configuration data from a configuration file and returns a configParser object.
The object can then be use by other functions to parse out specific config data.

Returns:
ConfigParser object that contains configuration data.
"""
def get_config_data() -> configparser.ConfigParser | None:
    # Get the config data to use
    if exists(config_file_name):
        # Interpolation is set to None for reading time stamp formats from config.ini file
        config = configparser.ConfigParser(interpolation=None)
        # Read the configuration file
        config.read(config_file_name)
        return config
    else:
        print("Config file NOT found! Defaults will be used...")
        return None

"""
does_section_option_exist(config, section_to_check, option_to_check):
Check if a section AND option exist in the config file, return true/false.

config : A configParser object containing the configuration file details
section_to_check : A string of the section name to check if it exists
option_to_check : A string of the option name to check if it exists

Returns:
True or False if the section AND option exists or do not
"""
def does_section_option_exist(config, section_to_check, option_to_check):
    return config.has_section(section_to_check) and config.has_option(section_to_check, option_to_check)

"""
read_server_config_to_int(section_to_read, option_to_read):
Read an option from a section of a config file and return it as an integer or None

section_to_check : A string of the section name to check
option_to_check : A string of the option name to check

Returns:
An integer repesentation of the option being checked
or None if the option does not exist.
"""
def read_server_config_to_int(section_to_read, option_to_read):
    config = get_config_data()
    if config and does_section_option_exist(config, section_to_read, option_to_read):
        return config.getint(section_to_read, option_to_read)
    return None

"""
read_server_config_to_list(section_to_read, option_to_read):
Read an option from a section of a config file and return it as a list or an empty list

section_to_check : A string of the section name to check
option_to_check : A string of the option name to check

Returns:
An list repesentation of the option being checked
or an empty list if the option does not exist.
"""
def read_server_config_to_list(section_to_read, option_to_read):
    config = get_config_data()
    if config and does_section_option_exist(config, section_to_read, option_to_read):
        return [log.strip() for log in config.get(section_to_read, option_to_read).split(",")]
    return []

"""
read_server_config_to_string(section_to_read, option_to_read):
Read an option from a section of a config file and return it as a string or an empty string

section_to_check : A string of the section name to check
option_to_check : A string of the option name to check

Returns:
An string repesentation of the option being checked
or an empty string if the option does not exist.
"""
def read_server_config_to_string(section_to_read, option_to_read):
    config = get_config_data()
    if config and does_section_option_exist(config, section_to_read, option_to_read):
        return config.get(section_to_read, option_to_read)
    return ""

"""
read_server_socket_settings():
Checks the configutation file for server setup details (ip, port, max clients).
This is used to create the necessary socket for the server.
If no details are found, sensible defaults are used. (loopback IP is defaulted)

section_to_check : A string of the section name to check
option_to_check : A string of the option name to check

Returns:
An string repesentation of the option being checked
or an empty string if the option does not exist.
"""
def read_server_socket_settings():
    config = get_config_data()
    if config is not None:

        # print("Config Sections:", config.sections())

        # Check for IP address in config
        if does_section_option_exist(config, config_server_settings_section, config_server_settings_option_ip):
            server_ip = config.get('ServerSettings', 'ip_address')
        else:
            print("Server Error: Unable to find ip address setting, default 127.0.0.1 will be used!")
            server_ip = server_default_ip

        # Check for port in config
        if does_section_option_exist(config, config_server_settings_section, config_server_settings_option_port):
            server_port = config.get('ServerSettings', 'port')
        else:
            print("Server Error: Unable to find port setting, default 1233 will be used!")
            server_port = server_default_port
        
        # check for max clients
        if does_section_option_exist(config, config_server_settings_section, config_server_settings_option_max_clients):
            max_clients = config.get('ServerSettings', 'max_clients')
        else:
            print("Server Error: Unable to find max client setting, default 5 will be used!")
            max_clients = server_default_max_clients        

    # If no configuration file was found
    else:
        print("No config file found, using defaults...")
        server_ip = server_default_ip
        server_port = server_default_port
        max_clients = server_default_max_clients

    # Return a dictionary with the retrieved values
    config_values = {
        "server_ip": server_ip,
        "server_port": server_port,
        "max_clients": max_clients
    }

    # print(f"Server Settings: {config_values}")
    return config_values

# if __name__ == "__main__":
#     # Call the function to read the configuration file
#     # config_data = read_server_socket_settings()
#     # print(f"The server IP address is: {config_data['server_ip']}")
#     # print(f"The server port is: {config_data['server_port']}")

#     # time_stamp_test = get_config_data()
#     # dateString = read_server_config_to_string("LogFieldArrangement", "TIME_STAMP_FORMAT")
#     # print(f"{datetime.now().strftime(dateString)}")

#     print(read_server_config_to_int("RateLimiting", "rate_limit_window"))
#     print(read_server_config_to_int("RateLimiting", "max_requests"))