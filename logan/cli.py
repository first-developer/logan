"""
CLI : Used the gather with command line interface logic

Repository and issue-tracker: https://github.com/first-developer/logan
Licensed under terms of MIT license (see LICENSE)
Copyright (c) 2013 first-developer <lionel.firstdeveloper@gmail.com>
"""

from . import __usage__ as __doc__
from . import __version__
from lib.docopt import docopt
from utils import random_string_in, ReturnCodes as return_codes
from subprocess import check_call as exec_cmd
from os import path
import sys



# ROOT_DIR = "/"
__LOGAN_MODULE_PATH     = path.dirname(__file__)                            # '/logan'
__LOGAN_ROOT__          = path.dirname(__LOGAN_MODULE_PATH)                 # '/'
__LOGAN_BIN__           = "python {}".format(__LOGAN_MODULE_PATH)           # 'python /logan
__LOGAN_LOG_FILE_PATH__ = path.join(__LOGAN_ROOT__, "logs", "logan.log")    # /logan/logs/logan.log



def show_help():
    """ Show 'help' to the user when he enters a wrong action command
    """

    print __doc__

# ------------------------------------------------------------------------------

def apologize():
    """
    """

    messages = [
        "I don't know how to do this :(. Sorry",
        "Hum... I forgot how to process this action",
        "OMG! I'm drunk!"
    ]
    return random_string_in(messages)

# ------------------------------------------------------------------------------

def sh(arguments, output=None):
    """ Helper that run logan command from the terminal

        Eg: running exec_cmd("create:file file.txt") will execute the unix command
            'python /logan create:file file.txt' equivalent to the logan command
            'logan create:file file.txt'.

        Args:
            cmd: command as string. Eg: 'create:file file.txt'
    """

    args = arguments["command"] # Extract the command from 'arguments'

    # Build command args array in the scope of logan cli.
    # Eg: For a command 'create:file file.txt'
    #       => ['python /logan', 'create:file', 'file.txt']
    command = [__LOGAN_BIN__]
    command.extend(args.split())

    return_code = try_execute_or_apologize(command, output)

    return return_code

# ------------------------------------------------------------------------------

def try_execute_or_apologize(command, output):
    """ Tries to execute the given command and use the given
        output to show the result of the execution.

        Args:
            command: The one the user entered.
            output:  Something that holds the result of the command execution.
    """

    try:
        return_code = exec_cmd(command, shell=True, stdout=output, stderr=output)

    # TODO: Deals with other return codes from different use cases
    except Exception as e:
        print "[LOGAN] : {}".format(apologize())
        return_code = return_codes.FAIL

    return return_code

# ------------------------------------------------------------------------------

def parse(command=None):
    """ Execute the command from user inputs

        It uses 'sys.argv' to take inputs from user
    """

    arguments = docopt(__doc__, version=__version__)

    print(arguments)

    return arguments

# ------------------------------------------------------------------------------

def run(command=None, output=None):
    """ Handles user command inputs
    """

    # Just for testing purposes :p
    # In real use case, the command will be get from
    # standard inputs
    if command:
        command = sys.argv

    arguments = parse(command)

    # Tries to execute user's entered command
    return_code = sh(arguments, output)

    # Exit with the return code, result of the command execution
    exit(return_code)

# ------------------------------------------------------------------------------