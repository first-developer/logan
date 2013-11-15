# ==========================================================
#    LOGAN AGENT
# ==========================================================

from os    import  path
from exceptions import  LoganConfigFileNotExistsError, \
                        LoganLoadConfigError, ActionAttributesMissingError
from logan.action import Action


class Agent(object):

    # Default config file that contains default configuration
    LOGAN_DEFAULT_ROOT_DIR             = path.join(path.expanduser("~"), ".logan")
    LOGAN_DEFAULT_CONFIG_FILENAME      = "loganrc.default"
    LOGAN_DEFAULT_USER_CONFIG_FILENAME = "loganrc"


    def __init__(self, logan_dir_path=None):

        # Setting configuration file
        self.set_paths(logan_dir_path)



    def set_paths(self, dir_path):
        """ Set all paths used in Logan internals """

        # setting the root directory qhere to find Logan contents
        self.root_dir = dir_path if dir_path else self.LOGAN_DEFAULT_ROOT_DIR

        # setting the config file path
        self.default_config_file_path   =  path.join(self.root_dir, self.LOGAN_DEFAULT_CONFIG_FILENAME)
        self.user_config_file_path      =  path.join(self.root_dir, self.LOGAN_DEFAULT_USER_CONFIG_FILENAME)



    def get_default_config(self):
        """ Loads configuration from the default config file

            This object represent the python object load from
            the default config file path (~/.logan/loganrc.default)
            The file is formatted using YAML syntax

            Returns:
                A dict mapping all config entries from the config

                Example:
                For this file config content
                --
                logan:
                    options: null
                --

                We get this python Dict
                --
                {
                    "logan":
                        "options": None
                }
        """

        default_config_file = self.get_config_from_filepath( self.default_config_file_path )

        return default_config_file



    def get_config_from_filepath(self, file_path):
        """ Loads config python Dict from a given file_path


            Raises:
                LoganLoadConfigError:           Error occurred  when it
                                                fails to read from the file
                LoganConfigFileNotExistsError:  Error occurred when the file
                                                linked to the given file path
                                                doesn't exist
        """

        from os     import path
        from yaml   import load
        from yaml   import YAMLError

        config_file = None
        config      = None

        # Check if the file exist before trying to read it
        if path.exists(file_path):
            with open(file_path) as config_file:
                config_content = config_file.read()
                try:
                    config = load(config_content)
                except YAMLError as e:
                    raise LoganLoadConfigError("Agent.get_default_config() : Logan was not able to load config from default config file")

                config_file.close()

            return config
        else:
            raise LoganConfigFileNotExistsError("Agent.get_default_config() : Logan was not able to open the default config file")



    def get_user_config(self):
        """ Get user configuration
        """

        user_config = self.get_config_from_filepath( self.user_config_file_path )

        return user_config



    def get_path(self, file_name=None):

        path = self.root_dir

        #if file_name is None:
        #    raise LoganPathNotFound("Logan was not able to find the path of the given filename")

        if file_name == self.LOGAN_DEFAULT_CONFIG_FILENAME:
            path = self.default_config_file_path

        elif file_name == self.LOGAN_DEFAULT_USER_CONFIG_FILENAME:
            path = self.user_config_file_path

        return path



    def get_config(self):
        """ Returns the final logan config, result of the merging of default and user config  """

        default_config  = self.get_default_config()
        user_config     = self.get_user_config()

        return self.dict_merge(default_config, user_config)


    def dict_merge(self, a, b):
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
                    result[k] = self.dict_merge(result[k], v)
            else:
                result[k] = deepcopy(v)
        return result


    def check_action_syntax(self, action):
        """ Checks whether or not a given command is valid

            That is to say, it is related to a correct action
            and match the correct syntax for a logan action
            Something like <verb:object[:context]> <params>

            Example: create:file logan.txt

            Returns:
                A boolean depending on whether or not the
                command is valid
        """

        return bool( self.validates_action(action) )


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


    def get_actions_inputs_from_command(self, command):
        """ Get action inputs from the given command

            Raises:
                ActionAttributesMissingError: An error occurred when there are missing
                                                params for the action

        """

        # Try to get action's attributes from command
        action_verb, action_object, action_context, action_params = \
                self.get_action_inputs_from_command(command)


        # Check if the required attributes have been retrieved
        if not(action_verb or action_object or action_params):
            self.raise_missing_attributes_error()

        # Setting action attributes
        self.action_verb    = action_verb
        self.action_object  = action_object
        self.action_context = action_context
        self.action_params  = action_params


    def get_action_inputs_from_command(self, command):
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



