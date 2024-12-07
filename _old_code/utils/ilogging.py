import json
import os
from datetime import datetime

class CustomLogger:
    def __init__(self, log_dir="logs"):
        """
        Initializes the Logger class, setting up the log file in the specified directory.
        
        :param log_dir: Directory where log files will be saved. Defaults to 'logs'.
        """
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)  # Ensure the directory exists
        self.log_filename = self.create_log_file()

    def create_log_file(self):
        """Creates a new log file with a unique name based on the current timestamp."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = f"log_{timestamp}.json"
        return os.path.join(self.log_dir, log_filename)

    def log(self, key, value):
        """Logs a key-value pair with a timestamp to the current log file."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            key: value
        }
        # Append the entry to the log file
        with open(self.log_filename, "a") as file:
            json.dump(entry, file)
            file.write("\n")  # Write each log entry on a new line



