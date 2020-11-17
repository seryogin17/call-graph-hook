#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import subprocess
import os
import sys
import shutil
from callgraph.utilities import get_colored_logger


## ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ##
def callgraph(args):
    """
    Create a call graph of modules and save it in a user-defined format
    """

    logger = get_colored_logger('pre-commit-callgraph.py', log_dir="./logs")

    # Check if pyan module is installed
    if not shutil.which("pyan"):
        sys.stderr.write("""Missing dependencies: pyan
Run the following command to install pyan:
pip install git+https://github.com/seryogin17/pyan.git""")
        sys.exit(1)
    
    # Check if path to callgrpah .config.json file is passed
    if not len(args):
        logger.error("Missing path to callgraph.config.json file as an argument\n")
        sys.exit(1)

    # Load the data from .config.json file
    path_config = args[0]
    with open(path_config, "r") as json_file:
        config = json.load(json_file)
        logger.debug(f'Config file is loaded successfully: {path_config}')

    # Create a list of all python modules if 'files' field is empty,
    # otherwise use the list from the config and check its existance
    if not len(config['files']):
        names = []
        for file in os.listdir(config['input_directory']):
            if file.endswith(".py"):
                names.append(os.path.join(config['input_directory'], file))
                logger.debug(f'List of file names is appended with {file}')
    else:
        names = config['files']
        names = [os.path.join(config['input_directory'], x) for x in names]
        for name in names:
            if not os.path.isfile(name):
                logger.error(f"File '{name}' does not exist\n")
                sys.exit(1)

    # Generate a call graph with default output json format
    cmd = f"pyan {' '.join(names)} --dot --colored --no-defines --grouped | dot -Tjson -Granksep=1.5 > {config['input_directory']}/callgraph.json"
    subprocess.run(cmd, shell=True)
    logger.debug('Generated a call graph with default json output format')

    # Save prefered output format
    # Generate a call graph and save with prefered output format, if it exists
    fmt = config['output_format'].lower()
    if len(fmt):
        cmd = f"pyan {' '.join(names)} --dot --colored --no-defines --grouped | dot -T{fmt} -Granksep=1.5 > {config['input_directory']}/callgraph.{fmt}"
        subprocess.run(cmd, shell=True)
        logger.debug(f'Generated a call graph with prefered {fmt} output format')

    cmd = f"git add {config['input_directory']}/callgraph.*"
    subprocess.run(cmd, shell=True)
    logger.debug(f"Added {config['input_directory']}/callgraph.* files to repo")


## ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ##
if __name__ == "__main__":
    callgraph(sys.argv[1:])
