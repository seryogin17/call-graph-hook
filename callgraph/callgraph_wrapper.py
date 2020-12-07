#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import subprocess
import os
import re
import sys
import shutil
from glob import glob

from callgraph.utilities import get_colored_logger


## ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ##
def callgraph(args):
    """
    Create a call graph of modules and save it in a user-defined format
    """

    logger = get_colored_logger("callgraph-wrapper.py", log_dir="./logs")

    # Check if pyan module is installed
    if not shutil.which("pyan"):
        result = subprocess.run("pip install git+https://github.com/seryogin17/pyan.git", shell=True)
        if not result.returncode:
            logger.debug("Installed missing dependency: pyan")
        else:
            logger.error("Failed to install missing dependency: pyan")
            sys.exit(1)

    # Check if graphviz module is installed
    if not shutil.which("dot"):
        logger.error("missing dependency: graphviz")
        sys.exit(1)
        result = subprocess.run("conda install graphviz", shell=True)
        if not result.returncode:
            logger.debug("Installed missing dependency: graphviz")
        else:
            logger.error("Failed to install missing dependency: graphviz")
            sys.exit(1)

    # Check if path to callgrpah .config.json file is passed
    if not len(args):
        logger.error("Missing path to callgraph.config.json file as an argument\n")
        sys.exit(1)

    # Load the data from .config.json file
    path_config = args[0]
    with open(path_config, "r") as json_file:
        config = json.load(json_file)
        logger.debug(f"Configuration file is loaded successfully: {path_config}")

    # Create a list of all python modules if "files" field is empty,
    # otherwise use the list from the config and check its existance
    if not len(config["files"]):
        names = []
        for file_name in os.listdir(config["input_directory"]):
            if file_name.endswith(".py"):
                names.append(os.path.join(config["input_directory"], file_name))
                logger.debug(f"List of file names is appended with {file_name}")
    else:
        names = config["files"]
        names = [os.path.join(config["input_directory"], x) for x in names]
        for file_name in names:
            if os.path.isfile(file_name):
                logger.debug(f"List of file names is appended with {file_name}")
            else:
                logger.error(f"File \"{name}\" does not exist\n")
                sys.exit(1)

    # Back up previous callgraphs before creating the new ones
    for file_name in os.listdir(config["input_directory"]):
        if re.findall(r"(?<=callgraph\.)\w+$", file_name):
            shutil.move(file_name, file_name+".bak")

    # Generate a call graph with default output json format
    # Set flags to break command execution if at least one of its part fails
    cmd = f"set -euo pipefail; pyan {' '.join(names)} --dot --colored --no-defines --grouped | dot -Tjson -Granksep=1.5 > {config['input_directory']}/callgraph.json"

    # Set bash as an executable and save the result of the command
    result = subprocess.run(cmd, shell=True, executable=shutil.which("bash"))
    # Check the command exit code
    if not result.returncode:
        logger.debug("Generated a call graph with default json output format")
    else:
        logger.error("Failed to generate a call graph with default json output format\n")
        sys.exit(1)

    # Save prefered output format
    # Generate a call graph and save with prefered output format, if it exists
    fmt = config["output_format"].lower()
    if len(fmt):
        cmd = f"set -euo pipefail; pyan {' '.join(names)} --dot --colored --no-defines --grouped | dot -T{fmt} -Granksep=1.5 > {config['input_directory']}/callgraph.{fmt}"
        result = subprocess.run(cmd, shell=True, executable=shutil.which("bash"))
        if not result.returncode:
            logger.debug(f"Generated a call graph with prefered {fmt} output format")
        else:
            logger.error(f"Failed to generate a call graph with prefered {fmt} output format\n")
            sys.exit(1)

    cmd = f"git add {config['input_directory']}/callgraph.json"
    result = subprocess.run(cmd, shell=True)
    if not result.returncode:
        logger.debug(f"Added {config['input_directory']}/callgraph.json to the repo")
    else:
        logger.error(f"Failed to add {config['input_directory']}/callgraph.json to the repo")

## ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ##
if __name__ == "__main__":
    callgraph(sys.argv[1:])
