__author__ = 'First-developer <lionel.firstdeveloper@gmail.com>'

__version__ = '0.1.0'

__copyright__ = """

The MIT License (MIT)

Copyright (c) 2013 first-developer

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction,including without limitation
the rights to use, copy, modify, merge,publish, distribute, sublicense,
and/or sell copies of the Software,and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included
in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.IN NO EVENT SHALL
THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
IN THE SOFTWARE.


"""


LOGAN_USAGE="""Logan: Command line organizer

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




def show_help():
    """ Show 'help' to the user when he enters a wrong action command
    """

    print LOGAN_USAGE





if __name__ == "main":
    
    exit(0)