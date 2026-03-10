import sys
import datetime
import re
from stockiv.config.paths import LOGS_DIR

# Regex pattern to match ANSI escape sequences (e.g. terminal colors)
ANSI_ESCAPE = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

class TeeLogger:
    """Intersects and duplicates terminal output streams to a local file, stripping ANSI codes."""
    def __init__(self, name: str, original_stream):
        self.original_stream = original_stream
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = LOGS_DIR / f"{name}_{timestamp}.log"
        self._file = open(self.log_file, "a", encoding="utf-8")

    def write(self, data):
        self.original_stream.write(data)
        self.original_stream.flush()
        
        # Clean the data from ANSI color codes before writing to log file
        clean_data = ANSI_ESCAPE.sub('', data)
        self._file.write(clean_data)
        self._file.flush()

    def flush(self):
        self.original_stream.flush()
        self._file.flush()
        
    def close(self):
        self._file.close()

def setup_global_logger(name: str):
    """
    Overrides sys.stdout and sys.stderr to capture full terminal output into a file.
    Use this at the highest entry point of execution.
    """
    sys.stdout = TeeLogger(f"{name}_stdout", sys.stdout)
    sys.stderr = TeeLogger(f"{name}_stderr", sys.stderr)
