# Basic Python Logging Server

This program was used for my Network Application Development course.
It is a logging server that contains a configuration file to edit the settings for the server.

The logs are produced using a JSON output that is intended to be ready by any log viewer that supports a JSON style format.

## The "config.ini" file allows for the following settings to be changed:<br>
- **ServerSettings** : The IP/Port and max supported clients
- **ValidLogs** : The types of logs that it will produce (default will allow a connected client to have logs generated for: TRACE, DEBUG, INFO, WARN, ERROR, FATAL
- **LogFieldArrangment** : How the arrangement of the log details will be produced
- **TIME_STAM_FORMAT** : Allows for timestamp formatting in the log entry
- **LogsToIgnore** : Log types in this section will be ignored and will not be shown in the log file
- **RateLimiting** : 
  - **rate_limit_window** - The time window to ignore multiple log requests (more than 1 every X seconds will be ignored)
  - **max_requests** - If more than Y logs are received in the rate_limit_window, the client will be rate limited

Please feel free to use this code for any purpose, it is very basic and was an assignment intended to help me learn a language I have not previously worked with and to better understand server logging.
