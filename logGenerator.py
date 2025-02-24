import configparser
import re
import json
import serverConfigParser
from validLogLevels import VALID_LOGS
from datetime import datetime

"""
TODO:
Add a config option for the time_stamp formatting

"""

# Client list globals
client_id_number = 0  # Increments based on number of clients who have connected
client_id_dictionary = {}  # Dictionary of client IDs and IP addresses associated with them


"""
THIS NEEDS TO BE PUT IN THE MAIN SERVER CODE SO WHEN A CLIENT CONNECTED IT GENERATES THEIR ID
then the ID will need to be passed with their IP and port number into the logging function
to use if necessary...
Will require another mutex!
"""
# function to assign an IP address a client ID
def assign_client_id(ip_to_check):
    global client_id_number
    if ip_to_check not in client_id_dictionary:
        client_id_number += 1
        client_id_dictionary[ip_to_check] = client_id_number
        # print(f"Client ID assigned: {client_id_dictionary[ip_to_check]}")
    return client_id_dictionary[ip_to_check]  # Always return the assigned ID


"""
CHANGES: THIS MUST TAKE IN THE CLIENT_ID AS WELL SINCE IT NEEDS TO BE ASSIGNED BEFORE GETTING HERE
"""
def generate_log_message(log_type, client_id, client_ip_address, client_port, requested_log_message = "None") -> str:
    # # Create the object
    # config = configparser.ConfigParser()
    # # config.optionxform = str # force configParser to respect case sensitivity 

    # config_file_name = "config.ini"
    # # Read the config.ini file
    # config.read(config_file_name)

    config = serverConfigParser.get_config_data()

    #TEST
    sections = config.sections()
    print("Current log sections: ", sections)

    time_stamp = datetime.now() # Get the current time for the log to be generated

    # Store ANY variables used in a dictionary with a string name as a key to use
    # when generating the json string
    log_field_variables = {}
    log_field_variables["time_stamp"] = time_stamp.strftime("%d/%m/%Y %H:%M:%S")
    log_field_variables["log_type"] = log_type # the type of log to be generated
    log_field_variables["client_ip_address"] = client_ip_address
    log_field_variables["client_port"] = client_port
    log_field_variables["client_id"] = client_id # Generated in main.py when a client connects
    log_field_variables["requested_log_message"] = requested_log_message # Any messages to be put in the log

    # This is used to determine if a default log must be printed due to missing config.ini settings
    valid_log_config_missing = False
    print_default_order = False

    message_object = {} # Setup the message object (JSON)

    # Variables to store config file information to use later
    # valid_log_list = []
    valid_log_list = serverConfigParser.read_server_config_to_list("ValidLogs", "VALID_LOG_LIST")
    
    # If there was no valid log list, use a standard default
    if not valid_log_list:
        valid_log_list = ["TRACE", "DEBUG", "INFO", "WARN", "ERROR", "FATAL"]


    field_order = serverConfigParser.read_server_config_to_list("LogFieldArrangement", "FIELD_ORDER")


    """
    RE-CODING
    """
    # Check if ValidLogs and VALID_LOG_LIST exists
    

    # # Check if ValidLogs section exists
    # if config.has_section("ValidLogs"):
    #     # Check if VALID_LOGS option in ValidLogs section exists
    #     if not config.has_option("ValidLogs", "VALID_LOGS_LIST"):
    #         print("Server Error: No VALID_LOGS_LIST option in config.ini!")
    #         # PRINT A LOG ERROR
    #         valid_log_config_missing = True # print default log style
    #     else:
    #         valid_log_list = config.get("ValidLogs", "VALID_LOGS_LIST").split(", ")
    #         print("Valid Logs Gotten: ", valid_log_list)
    # else:
    #     # No ValidLogs section exists, print logs by default
    #     # PRINT A LOG ERROR
    #     print("Server Error: No ValidLogs section in config.ini!")
    #     valid_log_config_missing = True

    # # Check if there is log field order configuration available
    # if config.has_section("LogFieldArrangement"):
    #     if not config.has_option("LogFieldArrangement", "FIELD_ORDER"):
    #         # PRINT A LOG ERROR
    #         print("Server Error: No FIELD_ORDER option in config.ini! Default order will be used...")
    #     else:
    #         field_order = config.get("LogFieldArrangement", "FIELD_ORDER").split(", ")
    #         print("Valid FIELD_ORDER gotten: ", field_order)
    # else:
    #     # PRINT A LOG ERROR
    #     print("Server Error: No LogFieldArrangement section in config.ini! Default order will be used...")

    """
    Start generating the log
    """
    # # Is it a valid log type?
    # if not valid_log_config_missing:
    #     print("Formatting exists in config...")

    # If the log_type is not in the valid_log_list from the config
    # generate a requested_log_message saying so
    if log_type not in valid_log_list:
        log_field_variables["requested_log_message"] = f"Invalid log type requested: {log_type}"
        log_field_variables["log_type"] = "ERROR"

    # If a field order exists, construct the log in a specific way
    if field_order:
        for field in field_order:
            if field in log_field_variables:
                print(f"Field: {field}, Value: {log_field_variables[field]}")
                message_object[field] = log_field_variables[field]
            else:
                print(f"Warning: Field '{field}' in FIELD_ORDER is not found in field_variables.")
    
    # Otherwise, construct a default log style (all fields are printed!)
    else:
        print("Constructing default log message...")
        message_object.update(log_field_variables)

    # Print final JSON output
    print("DUMP:", json.dumps(message_object, default=str))

    return json.dumps(message_object)


    """
    START OF OLD CODE
    """
#     # Get the client ID generated
#     client_id = assign_client_id(client_ip_address)

#     message_identifier = 0
#     message_client_name = 1
#     message_data = 2


#     # if None was returned, log an error instead!
#     if client_id is None:
#         # this is where you would call a log and report the IP address was not assigned a CLIENT_ID
#         return "Error: Client ID not found!"

#     # probably an ELSE for the if statement above, so if the ID is not found, it writes an error about that
#     # split_message = received_client_message.split("|") # used because you love networking messages...RIGHT.
#     current_time = datetime.now()

#     # get the value from the message for the log type requested
#     # log_type = split_message[message_identifier] # This is the split you were using before, dont bother now....
#     # print(f"Log Type: {log_type}")


#     # THIS CODE WAS FOR WHEN THERE WAS A CLIENT NAME AND DATA...ASK ED!!
#     """ASK ED ABOUT THIS CODE, do we need to care about this? Probably not....as per usual, Melissa is prolly correct....."""
#     # received_client_name = "UnknownClientName"
#     # received_client_data = "NoDataReceived"

#     # match len(split_message):
#     #     case 2:
#     #         received_client_name = split_message[message_client_name]
#     #     case 3 | _:
#     #         received_client_name = split_message[message_client_name]
#     #         received_client_data = split_message[message_data]

#     message_object = {"time_stamp": current_time.strftime("%d/%m/%Y %H:%M:%S")}  # Create the blank message object to start

#     # match received_client_message:
#     #     case "TRACE":
#     #         print("Trace Message...\n")
#     #         message_object["log_level"] = received_client_message
#     #     case "DEBUG":
#     #         print("Debug Message...\n")
#     #         message_object["log_level"] = received_client_message
#     #     case "INFO":
#     #         print("Info Message...\n")
#     #         message_object["log_level"] = received_client_message
#     #     case "WARN":
#     #         # Ex: Something happened, but the program can recover (file not found for example)
#     #         print("Warn Message...\n")
#     #         message_object["log_level"] = received_client_message
#     #     case "FATAL":
#     #         print("Fatal Message...\n")
#     #         message_object["log_level"] = received_client_message
#     #     case "ERROR":
#     #         print("Error Message...\n")
#     #         message_object["log_level"] = received_client_message
#     #     case _:
#     #         print(f"DEFAULT CASE generate_log_message() - Error Message...{received_client_message}\n")
#     #         message_object["log_level"] = "ERROR"
#     #         message_object["requested_type"] = received_client_message


#     """
#     Brainstorming: If we need to make sure the log format is configurable, we should assign values
#     Then you can check to see if the requested log type is valid and act accordingly
#     example (probably not a great idea)
#     Have the matcvh/case rely on a bool, if something invalid is sent, the FALSE bool is used to generate the log message
#     that also includes the ERROR data rather than being a properly formed message with no error data?
#     Something to consider....

#     How to do this (basic level)

#     Use a dictionary to associate the VALUES with their KEY
#     Ex: client_ip <- variable is associated with the STRING "client_id" <- used to match with the values in the config later!

#     So you need a dictionary of all available types of data for the log and their associated variable
#     log_message_definitions = {
#     "time_stamp": current_time.strftime("%d/%m/%Y %H:%M:%S") <- THE FORMAT FOR THIS CAN BE IN THE CONFIG TOO!!!
#     "log_level": log_level
#     "client_ip": client_ip
#     "client_port": client_port
#     "request_log_message": request_log_message
#     "requested_type": requested_type
#     }

#     Now that you would have all of these stored somewhere as key/value pairs, you can check the config section
#     to see if the string keys match anything in the config file
#     Need to research: How to iterate over the values in the config file data:
#     Grab the data from the config (already know how!)
#     Split the parts into their own pieces in a LIST (.split I think?...)
#     Call the list something like...format_config_list ?
#     To generate a LIST that will only contain the strings of the above keys to compare them with when printing
#     find a way to iterate over the KEYS in format_config_list and see if they are in log_message_definitions
#     If they are, add them to the object being constructed.

#     I think this will work? That's for Friday me to look into.
#     """
#     match log_type:
#         case log_level if log_level in VALID_LOGS:
#             message_object["log_level"] = log_level
#         case _:
#             print(f"DEFAULT CASE generate_log_message() - Error Message...{log_type}\n")
#             message_object["log_level"] = "ERROR"
#             message_object["requested_type"] = log_type
#             requested_log_message = "Invalid log type requested"



#     # print(f"Message Object: {message_object}")

#     # Form the rest of the message after the request_type has been added
#     message_object.update({
#         "client_id": client_id,
#         # "client_name": received_client_name,
#         "ip_address": client_ip_address,
#         "port": client_port,
#         "log_message": requested_log_message
#         # "message": received_client_data
#     })

# # Return the constructed json string to print
#     return json.dumps(message_object)

"""
END OF OLD CODE
"""

# if __name__ == "__main__":
#     # Assign client IDs correctly
#     # When a client connects, you need to assign it an ID
#     # the ID will be used when printing logging information
#     client_id_dictionary["192.168.0.1"] = assign_client_id("192.168.0.1")
#     client_id_dictionary["192.168.0.55"] = assign_client_id("192.168.0.55")
#
#     print(f"The client ID list: \n{client_id_dictionary}")
#
#     # How to generate the message to be put in the log file
#     message = generate_log_message("192.168.0.55", 1234, client_message)
#     print(f"The output from generate_log_message: \n{message}")
#     exit(0)
