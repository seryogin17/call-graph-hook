import sys
import os
import logging
from datetime import datetime as dt


## ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ##
class LoggingFormatter(logging.Formatter):
    """Colors log messages depending on the their logging level.
    REF https://stackoverflow.com/a/14859558"""
    
    ANSI_YELLOW = "\u001b[33m"
    ANSI_RED = "\u001b[31m"
    ANSI_RESET = "\u001b[0m"

    def __init__(self):
        super().__init__(
            fmt='%(asctime)s | %(filename)-20s| line %(lineno)3d: [%(levelname)8s]  %(message)s',
            datefmt="%d-%m-%Y %H:%M:%S")  
    
    def format(self, record):
        ## Save the original format configured by the user when the logger 
        ## ...formatter was instantiated
        format_orig = self._style._fmt

        ## Replace the original format with one customized by logging level
        if record.levelno == logging.WARNING:
            self._style._fmt = f"{self.ANSI_YELLOW}{format_orig}{self.ANSI_RESET}"

        if record.levelno == logging.ERROR or record.levelno == logging.CRITICAL:
            self._style._fmt = f"{self.ANSI_RED}{format_orig}{self.ANSI_RESET}"

        ## Call the original formatter class to do the grunt work
        result = logging.Formatter.format(self, record)

        ## Restore the original format configured by the user
        self._style._fmt = format_orig

        return result


## ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ##
def get_colored_logger(scriptname: str, log_dir: str = "./", level=logging.DEBUG, to_stdout=False):
    ## Setup logging capabilities

    RUN_ID = dt.strftime(dt.now(), "%d%m%Y-%H%M")

    os.mkdir(log_dir) if not os.path.isdir(log_dir) else None

    logger = logging.getLogger(scriptname)
    logger.setLevel(level)

    formatter = logging.Formatter('%(asctime)s | %(filename)-20s| line %(lineno)3d: [%(levelname)8s]  %(message)s', '%d-%m-%Y %H:%M:%S')

    log_name = f"{os.path.splitext(os.path.basename(scriptname))[0]}.{RUN_ID}.log"
    log_path = os.path.join(log_dir, log_name)

    fh = logging.FileHandler(log_path)
    fh.setLevel(logging.DEBUG)

    ch = logging.StreamHandler(sys.stdout) if to_stdout else logging.StreamHandler()
    ch.setLevel(level)

    fh.setFormatter(formatter)
    ch.setFormatter(LoggingFormatter())

    logger.addHandler(fh)
    logger.addHandler(ch)

    return logger
