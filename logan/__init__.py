__author__ = 'First-developer <lionel.firstdeveloper@gmail.com>'

__version__ = '0.1.0'

__copyright__ = """
Logan : A command line interface that helps organize yours script in a semantic way

Repository and issue-tracker: https://github.com/first-developer/logan
Licensed under terms of MIT license (see LICENSE)
Copyright (c) 2013 first-developer <lionel.firstdeveloper@gmail.com>
"""

__usage__="""Logan: Command line organizer

    Usage:
        logan <action> <params>
        logan -h | --help
        logan -v | --version

    Arguments
        <action>        Action is made up with <verb>:<object>:<context>
                            - <verb>    : Define the action you want to perform.
                                            Eg: 'create'
                            - <object>  : Define the action on which the action will be performed.
                                            Eg: 'file'
                            - <context> : Define the term in the action is performed.
                                            Eg: 'windows'

                            Eg: create:file:windows

        <params>        Used in addition to the actual action to precise the action to perform.
                        A parameter could be (--in /tmp --rename filename.txt.bak)
                        Don't use it a lot 'cause it decreases the meaning of the action

    Options
        -h --help       Show you how to use Logan.
        -v --version    Show version.
    """

from agent import Agent
from exceptions import  LoganConfigFileNotExistsError, \
                        LoganLoadConfigError,\
                        LoganLoadFileError,\
                        LoganFileNotExistsError,\
                        LoganActionPathMissingError
from cli import run




if __name__ == '__main__':
    run()