"""
UTILS : Helpers used to solves common problems

Repository and issue-tracker: https://github.com/first-developer/logan
Licensed under terms of MIT license (see LICENSE)
Copyright (c) 2013 first-developer <lionel.firstdeveloper@gmail.com>
"""


from exceptions import LoganLoadFileError,\
                        LoganFileNotExistsError
from os import path


# ================
# CLASSES
# ================

class ReturnCodes():

    FAIL = 1
    OK   = 0

# ------------------------------------------------------------------------------

class FileTypes():

    YAML        = "yaml"
    JSON        = "json"
    PLAIN_TEXT  = "text"


# ================
# HELPERS
# ================

def dict_merge(a, b):
    """
    @author: Ross McFarland
    @refernce: http://www.xormedia.com/recursively-merge-dictionaries-in-python/

    Recursively merges dict's. not just simple a['key'] = b['key'], if
    both a and bhave a key who's value is a dict then dict_merge is called
    on both values and the result stored in the returned dictionary.
    """

    from copy import deepcopy

    if not isinstance(b, dict):
        return b
    result = deepcopy(a)
    for k, v in b.iteritems():
        if k in result and isinstance(result[k], dict):
                result[k] = dict_merge(result[k], v)
        else:
            result[k] = deepcopy(v)
    return result

# ------------------------------------------------------------------------------

def random_string_in(collection):
    """ Return a random text in the given collection

        Args:
            collection: List of string. Eg: ["text 1", ...]

        Returns:
            String randomly selected
    """
    from random import randint

    random_index = randint(0, len(collection)-1)

    return collection[random_index]

# ------------------------------------------------------------------------------

def load_file(path, type=None):

    type = type or FileTypes.PLAIN_TEXT

    # Switch like
    return {
        FileTypes.YAML      : load_yaml_file(path),
        FileTypes.PLAIN_TEXT: load_text_file(path)
    }[type]

# ------------------------------------------------------------------------------

def load_yaml_file(file_path):
    """ Loads data from a YAML file located a the given path

            Args:
                file_path: The file path from where we want to get the content

            Returns:
                data: Dict load from the file

            Raises:
                LoganLoadFileError:         Error occurred  when it
                                            fails to read from the file
                LoganFileNotExistsError:    Error occurred when the file
                                            linked to the given file path
                                            doesn't exist
    """

    from yaml import load
    from yaml import YAMLError

    data = None

    # Check if the file exist before trying to read it
    if path.exists(file_path):
        with open(file_path) as file:
            data_content = file.read()
            try:
                data = load(data_content)
            except YAMLError as e:
                raise LoganLoadFileError("Logan : Unable to load file from %s" % file_path)

            file.close()

        return data
    else:
        raise LoganFileNotExistsError("Logan : Unable to open the file specified at %s " % file_path)

# ------------------------------------------------------------------------------

def load_text_file(file_path):
    """ Loads data from a plain text file located a the given path

            Args:
                file_path: The file path from where we want to get the content

            Returns:
                data: Dict load from the file

            Raises:
                LoganLoadFileError:         Error occurred  when it
                                            fails to read from the file
                LoganFileNotExistsError:    Error occurred when the file
                                            linked to the given file path
                                            doesn't exist
    """

    # Check if the file exist before trying to read it
    if path.exists(file_path):
        with open(file_path) as file:
            data = file.read()
            file.close()

        return data
    else:
        raise LoganFileNotExistsError("Logan : Unable to open the file specified at %s " % file_path)
