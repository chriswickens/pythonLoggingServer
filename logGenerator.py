"""
FILE : logGenerator.py
PROJECT : SENG2040 Assignment 3
Programmers : Chris Wickens, Melissa Reyes
First Version : Feb/17/2025
Description : Contains the logic to generate serialized JSON strings to be written to a log file.
Intended to be used with serverMain.py and serverConfigParser.py

Contains ONE function : generate_log_message()

Uses config.ini to control:
style of logs (field placement)
valid log types
ignored log types
time stamp format
"""

import json
import serverConfigParser
from datetime import datetime

# Default valid log types
default_valid_logs = ["TRACE", "DEBUG", "INFO", "WARN", "ERROR", "FATAL"]
default_time_stamp_format = "%d/%m/%Y %H:%M:%S"

"""
generate_log_message(log_type, client_id, client_ip_address, client_port, requested_log_message = "None"):
Generates a log message, displays various details based on the configuration file field order details.
requested_log_message is used when the client sends an unknown log type, it can also be expanded later
to include a specific message from a client.

Returns:
A serialized JSON object as a string that represents the intended log message to be saved to the log file
"""
def generate_log_message(log_type, client_id, client_ip_address, client_port, requested_log_message = "None") -> str:

    time_stamp = datetime.now() # Get the current time for the log to be generated

    # Try to read the timestamp config
    time_stamp_format = serverConfigParser.read_server_config_to_string(
        serverConfigParser.config_log_field_arrangement_section, 
        serverConfigParser.config_log_field_time_stamp_format_option)
    
    # If no time stamp format was found in the config, use the default
    if not time_stamp_format:
        time_stamp_format = default_time_stamp_format

    # Store ANY variables used in a dictionary with a string name as a key to use
    # when generating the json string
    log_field_variables = {}
    log_field_variables["time_stamp"] = time_stamp.strftime(time_stamp_format)
    log_field_variables["log_type"] = log_type # the type of log to be generated
    log_field_variables["client_ip_address"] = client_ip_address
    log_field_variables["client_port"] = client_port
    log_field_variables["client_id"] = client_id # Generated in main.py when a client connects
    log_field_variables["requested_log_message"] = requested_log_message # Any messages to be put in the log

    message_object = {} # Setup the message object (JSON)

    # Variables to store config file information to use later
    # valid_log_list = []
    valid_log_list = serverConfigParser.read_server_config_to_list(
        serverConfigParser.config_valid_log_section, 
        serverConfigParser.config_valid_log_option)
    
    # If there was no valid log list, use a standard default
    if not valid_log_list:
        valid_log_list = default_valid_logs

    # Get the order of the fields from the config file
    field_order = serverConfigParser.read_server_config_to_list(
        serverConfigParser.config_log_field_arrangement_section, 
        serverConfigParser.config_log_field_arrangement_option)

    # If the log_type is not in the valid_log_list
    # generate a requested_log_message saying so
    if log_type not in valid_log_list:
        log_field_variables["requested_log_message"] = f"Invalid log type requested: {log_type}"
        log_field_variables["log_type"] = "ERROR"

    # If a field order exists, construct the log in a specific way
    if field_order:
        for field in field_order:
            if field in log_field_variables:
                # print(f"Field: {field}, Value: {log_field_variables[field]}")
                message_object[field] = log_field_variables[field]
            else:
                print(f"Warning: Field '{field}' in FIELD_ORDER is not found in field_variables.")
    
    # Otherwise, construct a default log style (all fields are printed!)
    else:
        # print("Constructing default log message...")
        message_object.update(log_field_variables)

    # Print final JSON output
    # print("DUMP:", json.dumps(message_object, default=str))

    # Return the constructed message to be logged
    return json.dumps(message_object)