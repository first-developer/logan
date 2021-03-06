# ==========================================================
#    LOGAN AGENT
# ==========================================================

from os import path
from utils import dict_merge, load_file, FileTypes
import shelve
from exceptions import  LoganConfigFileNotExistsError, \
                        LoganLoadConfigError, \
                        LoganActionAttrsMissingError,\
                        LoganActionPathMissingError
import say

class Agent(object):

    # Default config file that contains default configuration
    LOGAN_DEFAULT_ROOT_DIR             = path.join(path.expanduser("~"), ".logan")
    LOGAN_DEFAULT_CONFIG_FILENAME      = "loganrc.default"
    LOGAN_DEFAULT_USER_CONFIG_FILENAME = "loganrc"
    LOGAN_DEFAULT_ACTIONS_DIR_NAME     = "actions"

    # the pattern that validates an action
    LOGAN_ACTION_PATTERN   = r'(\w+):(\w+):?(\w+)? *(.*)'

    # Cache file path
    LOGAN_CACHE_KEY = 'logan.cache'

    # Output template
    LOGAN_OUTPUT_TEMPLATE = """

\033[1;30mAction\t:\033[0;30m \033[1;36m{} \033[0;30m

\033[1;30mRetcode\t:\033[0;30m {}

\033[1;30mErrors\t: \033[0;30m
\033[0;31m
{}\033[0;30m
\033[1;30mOutput\t:\033[0;30m
\033[0;32m
{}
\033[0;30m
"""

    # ------------------------------------------------------------------------------

    def __init__(self, logan_dir_path=None):

        # Setting configuration file
        self.set_paths(logan_dir_path)

    # ------------------------------------------------------------------------------

    def set_paths(self, dir_path):
        """ Set all paths used in Logan internals """

        # setting the root directory qhere to find Logan contents
        self.root_dir = dir_path if dir_path else self.LOGAN_DEFAULT_ROOT_DIR

        # setting the config file path
        self.default_config_file_path   = path.join(self.root_dir, self.LOGAN_DEFAULT_CONFIG_FILENAME)
        self.user_config_file_path      = path.join(self.root_dir, self.LOGAN_DEFAULT_USER_CONFIG_FILENAME)

        # setting cache path
        self.logan_cache_path           = path.join(self.root_dir, self.LOGAN_CACHE_KEY)

        # Setting actions path
        self.logan_actions_path         = path.join(self.root_dir, self.LOGAN_DEFAULT_ACTIONS_DIR_NAME)

    # ------------------------------------------------------------------------------

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

    # ------------------------------------------------------------------------------

    @classmethod
    def load_config_file(cls, file_path):
        """ Alias to allow reading config file from outside
        """

        return cls.get_config_from_filepath(file_path)

    # ------------------------------------------------------------------------------

    def get_config_from_filepath(self, file_path):
        """ Loads config python Dict from a given file_path
        """

        return load_file(file_path, type=FileTypes.YAML)

    # ------------------------------------------------------------------------------

    def load_user_config(self):
        """ Get user configuration
        """

        user_config = self.get_config_from_filepath( self.user_config_file_path )

        return user_config

    # ------------------------------------------------------------------------------

    def get_path(self, file_name=None):

        path = self.root_dir

        #if file_name is None:
        #    raise LoganPathNotFound("Logan was not able to find the path of the given filename")

        if file_name == self.LOGAN_DEFAULT_CONFIG_FILENAME:
            path = self.default_config_file_path

        elif file_name == self.LOGAN_DEFAULT_USER_CONFIG_FILENAME:
            path = self.user_config_file_path

        return path

    # ------------------------------------------------------------------------------

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
            config = dict_merge(default_config, user_config) or {}

            # Save the config to the cache
            cached = self.add_to_cache(config)

            if not cached:
                print "Failed to cache config file"

        return config

    # ------------------------------------------------------------------------------

    def check_action_command_syntax(self, command):
        """ Checks whether or not a given command is valid

            That is to say, it is related to a correct action
            and match the correct syntax for a logan action
            Something like <verb:object[:context]> <params>

            Example: create:file logan.txt

            Returns:
                A boolean depending on whether or not the
                command is valid
        """

        return bool( self.validates_action_command(command) )

    # ------------------------------------------------------------------------------

    def raise_missing_attributes_error(self):
        """ Fires the error related to missing attributes case

            Raises:
                ActionAttributesMissingError: An error occurred when there are missing
                                                params for the action
        """
        raise LoganActionAttrsMissingError("""Attributes needed!
                You must provides ACTION_VERB, ACTION_OBJECT, ACTION_CONTEXT,
                ACTION_PARAMS as params
                """)

    # ------------------------------------------------------------------------------

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
        self.command        = command
        self.action_verb    = action_verb
        self.action_object  = action_object
        self.action_context = action_context
        self.action_params  = action_params

    # ------------------------------------------------------------------------------

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

        return self.validates_action_command(command).groups(None)

    # ------------------------------------------------------------------------------

    def validates_action_command(self, action):
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

    # ------------------------------------------------------------------------------

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

    # ------------------------------------------------------------------------------

    def get_cache(self):
        """ Gets a cache instance

            Returns:
                A cache object
        """
        return shelve.open(self.logan_cache_path)

    # ------------------------------------------------------------------------------

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

    # ------------------------------------------------------------------------------

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

    # ------------------------------------------------------------------------------

    def find_action_by_key(self, key=None):
        """ Find the action with the given 'key' as an action key

            It also checks that the action found for the given 'key'
            has the same context as the one inside the configuration

            Args:
                key: A given action key

            Returns:
                Dict containing all information about the action
                that as the given 'key' as an action key
        """

        config  = self.load_config()
        actions = config.get("actions")

        action_found = actions.get(key)

        # Check if the action found has the same context of the one in the configuration
        if action_found and (action_found.get("context") != self.action_context):
            return


        return action_found

    # ------------------------------------------------------------------------------

    def find_action(self):
        """ Gets the action that the user wants to perform
        """

        user_action = "{}:{}".format(self.action_verb, self.action_object)

        return self.find_action_by_key(user_action)

    # ------------------------------------------------------------------------------

    def performs(self, action):
        """ Executes command related to the given action

            Args:
                action: Dict gathering all action attributes useful to
                        run the command related to it.

                        The Dict looks like this :
                        action = {
                            "scope": "create"
                            "context": "null"
                            "path": "/bin/cp"
                        }

            Returns:
                Dict as the result of action performing. It is structure
                like this:
                output = {
                    "out" : "...",
                    "err" : "...",
                    "code": 0/1
                }
        """

        import subprocess

        command = self.build_command_from_action(action)

        process = subprocess.Popen(command, shell=False, stderr=subprocess.PIPE, stdout=subprocess.PIPE)

        out, err = process.communicate()

        return {
            "out" : out,
            "err" : err,
            "code": process.returncode
        }

    # ------------------------------------------------------------------------------

    # TODO: Write test for this method
    def build_command_from_action(self, action):
        """ Build the process command that will be executed.

            It also used

            Args:
                action: Use this Dict to get access to action attributes

            Returns:
                Tuple as [command, options_and_params]
                Ex: ["ls", "-ltr dr*"]
        """

        context_path     = action.get("context") or ""
        action_file_path = action.get("path")    or ""

        action_path = path.join(self.logan_actions_path,
                                context_path,
                                action_file_path)

        # Checks if the action path is correct file
        if not path.isfile(action_path):
            print "Agent.build_command_from_action : checks the action path : %s" % action_path
            raise LoganActionPathMissingError("Logan action path [%s] not found" % action_path)

        return [
            action_path,
            self.action_params
        ]

    # ------------------------------------------------------------------------------

    def show_output(self):
        """ Show result from command execution
        """

        action_cmd  = self.command
        output      = self.output.get("out")
        errors      = self.output.get("err")
        return_code = self.output.get("code")

        print self.LOGAN_OUTPUT_TEMPLATE.format(action_cmd, return_code, errors, output)

    # ------------------------------------------------------------------------------

    def process(self, command):
        """ Executes the command entered by the user
        """

        # 1. Check command syntax
        syntax_ok = self.check_action_command_syntax(command)

        if syntax_ok:

            # 2.1 Extract action inputs from command
            self.get_actions_inputs_from_command(command)

            # 2.2 Load config
            cached_config = self.load_config()

            # 3. Find the action to perform
            action = self.find_action()

            # 4. Perform action
            self.output = self.performs(action)

            # 5. show output
            self.show_output()

        else:
            # TODO: Writes 'Show_help' method
            print "Wrong syntax : Unable to run the command"