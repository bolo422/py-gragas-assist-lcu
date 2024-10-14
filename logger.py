from enum import Enum

class LogLevel(Enum):
    REGULAR = 200
    INFO = 300
    WARNING = 400
    ERROR = 500
    NONE = 9999

log_level = LogLevel.INFO

def parse_str(level):
    if level == 'REGULAR':
        return LogLevel.REGULAR
    elif level == 'INFO':
        return LogLevel.INFO
    elif level == 'WARNING':
        return LogLevel.WARNING
    elif level == 'ERROR':
        return LogLevel.ERROR
    elif level == 'NONE':
        return LogLevel.NONE
    else:
        return LogLevel.INFO

def set_log_level(level):
    global log_level
    log_level = level

def level_is_above_minimum(level):
    return level.value >= log_level.value

def log(level=LogLevel.INFO, *args):
    if level_is_above_minimum(level):
        message = " ".join(map(str, args))
        if level == LogLevel.INFO:
            print(f"\033[0;32m[INFO] - {message}\033[0m")
        elif level == LogLevel.WARNING:
            print(f"\033[0;33m[WARNING] - {message}\033[0m")
        elif level == LogLevel.ERROR:
            print(f"\033[0;31m[ERROR] - {message}\033[0m")

if __name__ == '__main__':
    log("This is an info message", LogLevel.INFO)
    log("This is a warning message", LogLevel.WARNING)
    log("This is an error message", LogLevel.ERROR)
