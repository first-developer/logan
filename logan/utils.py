"""
UTILS : Helpers used to solves common problems

Repository and issue-tracker: https://github.com/first-developer/logan
Licensed under terms of MIT license (see LICENSE)
Copyright (c) 2013 first-developer <lionel.firstdeveloper@gmail.com>
"""


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


class ReturnCodes():

    FAIL = 1
    OK   = 0