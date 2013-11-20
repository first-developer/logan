# ==========================================================
#    LOGAN AGENT
# ==========================================================

from os import  path
import shelve
from exceptions import  LoganConfigFileNotExistsError, \
                        LoganLoadConfigError, ActionAttributesMissingError
from logan.action import Action


class Agent(object):

    # Default config file that contains default configuration
    LOGAN_DEFAULT_ROOT_DIR             = path.join(path.expanduser("~"), ".logan")
    LOGAN_DEFAULT_CONFIG_FILENAME      = "loganrc.default"
    LOGAN_DEFAULT_USER_CONFIG_FILENAME = "loganrc"

    # the pattern that validates an action
    LOGAN_ACTION_PATTERN   = r'(\w+):(\w+):?(\w+)? *(.*)'

    # Cache file path
    LOGAN_CACHE_KEY = 'logan.cache'



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

        # setting cache
        self.logan_cache_path = path.join(self.root_dir, self.LOGAN_CACHE_KEY)


    def load_default_config(self):
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



    def load_user_config(self):
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



    def load_config(self):
        """ Returns the final logan config, result of the merging of default and user config

            It always return an empty Dict object not None!

            Returns:
                Dict derived from the logan configuration file
        """

        # Try to retrieve config from cache
        config = self.get_config_from_cache() or {}

        if not config:

            default_config = self.load_default_config()
            user_config    = self.load_user_config()

            # Overrides the default config with user one
            config = self.dict_merge(default_config, user_config) or {}

            # Save the config to the cache
            cached = self.add_to_cache(config)

            if not cached:
                print "Failed to cache config file"

        return config


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

            Args:
                command: The given command from which we are trying
                        to extract action inputs

            Raises:
                ActionAttributesMissingError: An error occurred when there are missing
                                                params for the action

        """

        # Try to get action's attributes from command
        action_verb, action_object, action_context, action_params = \
                self.extract_action_inputs_from_command(command)


        # Check if the required attributes have been retrieved
        if not(action_verb or action_object or action_params):
            self.raise_missing_attributes_error()

        # Setting action attributes
        self.action_verb    = action_verb
        self.action_object  = action_object
        self.action_context = action_context
        self.action_params  = action_params


    def extract_action_inputs_from_command(self, command):
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


    def validates_action(self, action):
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

        valid_action = re.search(self.LOGAN_ACTION_PATTERN, action)

        return valid_action


    def add_to_cache(self, config):
        """ Store the config object in cache to avoid reading from a file every time

            Args:
                config: the config object to save

            Returns:
                Boolean: Whether or not he saving process has succeeded
        """

        cache  = None
        cached = True

        try:
            cache = self.get_cache()
            cache[self.LOGAN_CACHE_KEY] = config
            cache.close()
        except Exception as e:
            print "Saving in cache failed"
            cached = False

        return cached


    def get_cache(self):
        """ Gets a cache instance

            Returns:
                A cache object
        """
        return shelve.open(self.logan_cache_path)


    def get_config_from_cache(self):

        cache         = None
        cached_config = None

        try:
            cache = self.get_cache()
            cached_config = cache[self.LOGAN_CACHE_KEY]
            cache.close()
        except Exception as e:
            print "Saving in cache failed"

        return cached_config


    def check_cache(self, key):
        """ Checks whether or not it exist the given 'key'
            in the cache as a object key

             Args:
                key: The one we want to check the presence

            Returns:
                Boolean related to the presence state of this 'key'

        """

        is_present = False

        try:
            cache = self.get_cache()
            is_present = cache.has_key(key)
            cache.close()
        except Exception as e:
            print "Checking presence in cache failed"

        return is_present


    def find_action(self, key):
        """ Find the action with the given 'key' as an action key

            Args:
                key: A given action key

            Returns:
                Dict containing all information about the action
                that as the given 'key' as an action key
        """

        action_found = None

        config  = self.load_config()
        actions = config.get("actions")

        # Returns action related to this key
        return actions.get(key)
