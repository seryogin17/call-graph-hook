import sys
import os
import asyncio
import sqlite3
import pandas as pd # type: ignore
import logging

from datetime import datetime as dt
from typing import List, Tuple, Union


## ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ##
def stringify_list_items_for_sql(lst: List[str]) -> str:
    lst = [f'"{item}"' for item in lst]
    return ", ".join(lst)


## ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ##
def stringify_dict_items_for_sql(dct: dict) -> str:
    assignments = [f'{key} == "{value}"' for key, value in dct.items()]
    return ", ".join(assignments)


## ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ##
def get_valid_seq_entries_by_path(column_input: str, path_db: str, logger: logging.Logger, paths: List[str] = [], qc_ok_statuses: List[str] = ["OK"]) -> pd.DataFrame:
    conn = sqlite3.connect(path_db)

    statuses = stringify_list_items_for_sql(qc_ok_statuses)

    if paths:
        filenames = list(map(lambda path: os.path.basename(path), paths))

        filenames_q = stringify_list_items_for_sql(filenames)
        query = f"""SELECT * FROM Sequence 
                        WHERE ({column_input} IN ({filenames_q})) 
                        AND ((QC_Status IN {f"({statuses})"})
                            OR (QC_Status IS NULL));
                """
    else:
        logger.info("No filenames supplied; will process all traces passing QC")
        query = f'SELECT * FROM Sequence WHERE (QC_Status IN {f"({qc_ok_statuses})"})'

    return pd.read_sql(query, con=conn)


## ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ##
def scatter_df(df: pd.DataFrame) -> List[List]:
    return [row for row in df.itertuples()]


## ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ##
async def gather_with_concurrency(n, *tasks):
    semaphore = asyncio.Semaphore(n)

    async def sem_task(task):
        async with semaphore:
            return await task
    
    return await asyncio.gather(*(sem_task(task) for task in tasks))


## ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ##
# def get_proc_output(cmd: str, caller_funcname: str, logger: logging.Logger) -> dict:
#     logger.debug(f'({caller_funcname}) CMD: "{cmd}"')
    
#     proc = subprocess.run(cmd, shell=True, capture_output=True)

#     rc = proc.returncode    
#     stdout = proc.stdout.decode("utf-8")
#     stderr = proc.stderr.decode("utf-8")
    
#     caller_funcname = inspect.currentframe().f_back.f_code.co_name
#     logger.debug(f"({caller_funcname}) CMD return code: {rc}")
    
#     if not rc == 0:
#         logger.error(stdout)
#         logger.error(stderr)
#         sys.exit(1)
    
#     return {"rc": rc, "stdout": stdout, "stderr": stderr}


## ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ##
async def get_cmd_output_async(cmd: str) -> dict:
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        shell=True
    )

    stdout_b, stderr_b = await proc.communicate()

    stdout = stdout_b.decode("utf-8")
    stderr = stderr_b.decode("utf-8")
    
    return {"rc": proc.returncode, "stdout": stdout, "stderr": stderr}


## ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ##
# def log_output_size(filename: str, caller_funcname: str, description: str, logger: logging.Logger) -> None:
#     filename = os.path.basename(filename)
#     try:
#         size_bytes = os.stat(filename).st_size
#         size = f"{int(size_bytes / 1024)} kB" if size_bytes >= 1024 else f"{size_bytes} B"
#         logger.info(f"({caller_funcname}) {description} ({size}): {filename}")
#     except Exception as error:
#         logger.error(str(error))
#         sys.exit(1)


## ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ##
def get_output_report(path: str, message: str, logger: logging.Logger, caller_funcname: str = "") -> Union[str, None]:
    try:
        size_bytes = os.stat(path).st_size
        size = f"{int(size_bytes / 1024)} kB" if size_bytes >= 1024 else f"{size_bytes} B"
        output = f"{message} ({size}): {path}"
        output = f"({caller_funcname}) " + output if caller_funcname else output
    except Exception as error:
        logger.error(f"{repr(error)}: {path}")
        output = ""
    
    return output


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
