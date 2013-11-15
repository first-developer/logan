from logan.exceptions import ActionAttributesMissingError


class Action(object):

    def __init__(self, command=None):

        if not command:
            self.raise_missing_attributes_error()

        # Settings action attributes retrieves from command
        self.set_attributes_from_command(command)


    def raise_missing_attributes_error(self):
        """ Fires the error related to missing attributes case

            Raises:
                ActionAttributesMissingError: An error occurred when there are missing
                                                params for the action
        """
        raise ActionAttributesMissingError("""Attributes needed!
                You must provides ACTION_VERB, ACTION_OBJECT, ACTION_CONTEXT,
                ACTION_PARAMS as params
                """)


    def set_attributes_from_command(self, command):
        """ Sets action attributes from the given command

            Raises:
                ActionAttributesMissingError: An error occurred when there are missing
                                                params for the action

        """

        # Try to get action's attributes from command
        action_verb, action_object, action_context, action_params = \
                self.get_attributes_from_command(command)


        # Check if the required attributes have been retrieved
        if not(action_verb or action_object or action_params):
            self.raise_missing_attributes_error()

        # Setting action attributes
        self._action_verb    = action_verb
        self._action_object  = action_object
        self._action_context = action_context
        self._action_params  = action_params


    def get_attributes_from_command(self, command):
        """ Fetches all action attributes contains in the command

            It returns the result from the action validation process
            We made the assumption that it's the responsibility of the
            logan agent to validate the command. Therefore the command
            is considered correct

            Args:
                command: Command passed by the logan agent in order
                        to be executed

            Returns:
                @see validates_action
        """

        return self.validates_action(command).groups(None)


    def get_attr(self, attr_name):
        return self.__getattribute__("_action_" + attr_name)


    @staticmethod
    def validates_action(action):
        """ Checks whether or not a given action is valid.

            That is to say, this action matches the correct
            syntax for a logan action: <verb>:<object>[:<context>] <params>

            Example: create:file logan.txt

            Args:
                action: the string representing the action command to execute
                        by the logan agent

            Returns:
                None or a tuple containing action attributes depending whether
                or not the the action is valid

        """
        import re

        # the pattern that validates an action
        LOGAN_ACTION_PATTERN   = r'(\w+):(\w+):?(\w+)? *(.*)'

        valid_action = re.search(LOGAN_ACTION_PATTERN, action)

        return valid_action

