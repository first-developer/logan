from unittest import TestCase
from logan import Agent
from logan import LoganConfigFileNotExistsError
from logan import LoganLoadConfigError
import os.path


class TestAgent(TestCase):

    def setUp(self):
        self.agent                       = None

        self.LOGAN_ROOT                  = os.path.join("..", "fixtures")
        self.BAD_DEFAULT_CONFIG_FILEPATH = os.path.join(self.LOGAN_ROOT, "loganrc_bad.default")
        self.DEFAULT_CONFIG_FILEPATH     = os.path.join(self.LOGAN_ROOT, "loganrc.default")
        self.USER_CONFIG_FILEPATH        = os.path.join(self.LOGAN_ROOT, "loganrc")

        self.LOGAN_TEST_ACTION           = "create:file"
        self.LOGAN_TEST_COMMAND          = "create:file filename.txt"
        self.LOGAN_TEST_COMMAND_WITH_CTX = "goto:server:aws windrs04"
        self.LOGAN_TEST_EMPTY_COMMAND    = ":: anything"
        self.LOGAN_TEST_BAD_COMMAND      = "restart server wwinf9301"

        self.LOGAN_CACHE_KEY             = "logan.cache"

    def test_initialize_logan_agent(self):
        """ Tests creation of a new Logan agent """

        self.agent = Agent()
        self.assertIsInstance(self.agent, Agent, "This is not a logan Agent.")


    def test_initialize_logan_agent_with_config_file_path(self):
        """ Tests creation of a new Logan agent by providing a config file path"""

        self.agent = Agent(self.LOGAN_ROOT)

        self.assertEqual(self.agent.default_config_file_path, self.DEFAULT_CONFIG_FILEPATH)
        self.assertEqual(self.agent.user_config_file_path,    self.USER_CONFIG_FILEPATH)


    def test_should_raise_when_the_default_config_file_doesnt_exist(self):
        """ Loads default config file path  and return a config object """
        self.agent = Agent()

        self.failUnlessRaises(LoganConfigFileNotExistsError, self.agent.load_default_config)


    def test_should_raise_when_the_config_file_is_not_well_formatted(self):
        """ Loads default config object """

        # Initialize the agent by changing the default config file location
        self.agent = Agent(self.LOGAN_ROOT)

        # Change the default config file path with the bad one
        self.agent.default_config_file_path = self.BAD_DEFAULT_CONFIG_FILEPATH

        self.failUnlessRaises(LoganLoadConfigError, self.agent.load_default_config)


    def test_should_return_default_configuration_when_requested(self):
        """ Loads default config object """

        # Initialize the agent by changing the default config file location
        self.agent = Agent(self.LOGAN_ROOT)

        # Try to load the default config object
        default_config = self.agent.load_default_config()

        self.assertIsNotNone(default_config, "Failed to load the default configuration")


    def test_should_contains_at_least_one_default_command(self):
        """ Checks if the excerpt config is in the default configuration file """

        # Initialize the agent by changing the default config file location
        self.agent = Agent(self.LOGAN_ROOT)

        # Try to load the default config object
        default_config = self.agent.load_default_config()

        self.assertIsNotNone(default_config.get("actions").get(self.LOGAN_TEST_ACTION))


    def test_should_returns_user_configuration(self):
        """ Loads user configuration """

        # Initialize the agent by changing the default config file location
        self.agent = Agent(self.LOGAN_ROOT)

        user_config = self.agent.load_user_config()

        self.assertIsNotNone(user_config, "Failed to load the user configuration")


    def test_return_the_right_path_depending_on_the_logan_specific_filename(self):
        """ Return the path for every logan specific filename """

        # Initialize the agent by changing the default config file location
        self.agent = Agent(self.LOGAN_ROOT)

        agent = self.agent

        self.assertEqual(agent.get_path("loganrc.default"),
                         self.DEFAULT_CONFIG_FILEPATH, "loganrc.default file not found")
        self.assertEqual(agent.get_path("loganrc"),
                         self.USER_CONFIG_FILEPATH, "loganrc file not found")


    def test_user_config_should_override_default_configuration(self):
        """ Override default configuration with user configuration """

        # Initialize the agent by changing the default config file location
        self.agent = Agent(self.LOGAN_ROOT)

        default_config      = self.agent.load_default_config()
        user_config         = self.agent.load_user_config()
        overridden_config   = self.agent.load_config()

        default_create_file_action_options      = default_config.get("actions").get(self.LOGAN_TEST_ACTION)
        user_create_file_action_options         = user_config.get("actions").get(self.LOGAN_TEST_ACTION)
        overridden_create_file_action_options   = user_config.get("actions").get(self.LOGAN_TEST_ACTION)

        # Check if we get something from the overriding
        self.assertIsNotNone(overridden_config, "Empty - Failed to override default configuration")

        # Make sure that the default option is different from user option
        self.assertNotEqual(default_create_file_action_options.get("path"),
                user_create_file_action_options.get("path"))

        # Checks if the path option of the self.LOGAN_TEST_ACTION has been overridden
        self.assertEqual(overridden_create_file_action_options.get("path"),
                user_create_file_action_options.get("path"))


    def test_checks_actions_syntax(self):
        """ Validates a command and user actions and make sure the syntax is correct
        """

        # Initialize the agent by changing the default config file location
        self.agent = Agent(self.LOGAN_ROOT)

        # Testing that a simple good command passed
        syntax_ok = self.agent.check_action_syntax(self.LOGAN_TEST_COMMAND)
        self.assertTrue(syntax_ok, "This simple command must be good")

        # Testing that a right command with a specified context passed
        syntax_ok = self.agent.check_action_syntax(self.LOGAN_TEST_COMMAND_WITH_CTX)
        self.assertTrue(syntax_ok, "This command with context must be good")

        # Testing that an empty command or action failed
        syntax_ok = self.agent.check_action_syntax(self.LOGAN_TEST_EMPTY_COMMAND)
        self.assertFalse(syntax_ok, "This empty command must be not valid")

        # Testing that a bad formatted command or action failed
        syntax_ok = self.agent.check_action_syntax(self.LOGAN_TEST_BAD_COMMAND)
        self.assertFalse(syntax_ok, "This bad command must be not valid")


    def test_extract_action_inputs_from_user_command(self):
        """ Retrieves actions inputs from command enter by the user

            It makes assumption that the command has been validated
            by the Agent before the extraction
        """

        # Initialize the agent by changing the default config file location
        self.agent = Agent(self.LOGAN_ROOT)

        # Tries to extract actions inputs from good, empty and bad command
        action_inputs    = self.agent.extract_action_inputs_from_command(self.LOGAN_TEST_COMMAND)

        # Shouldn't get 'None' as a result
        self.assertIsNotNone(action_inputs,
                             "No action inputs found from the command '%s'" % self.LOGAN_TEST_COMMAND )


    def test_should_be_able_to_save_config_object_in_cache(self):
        """ Checks whether the config object exist in cache
        """

        # Initialize the agent by changing the default config file location
        self.agent = Agent(self.LOGAN_ROOT)

        # Get the config object to save
        config = self.agent.load_config()

        # Try to save the config object in the cache
        saved = self.agent.add_to_cache(config)

        self.assertTrue(saved, "Failed to saved the config object")


    def test_should_be_able_to_get_config_object_from_cache(self):
        """ Get the config object from cache
        """

        # Initialize the agent by changing the default config file location
        self.agent = Agent(self.LOGAN_ROOT)

        # Get the config object to save
        config = self.agent.get_config_from_cache()

        self.assertIsNotNone(config, "Failed to get the cached config object")


    def test_check_the_presence_of_the_config_in_cache(self):
        """ Checks if the config is store in the cache
        """

        # Initialize the agent by changing the default config file location
        self.agent = Agent(self.LOGAN_ROOT)

        checked = self.agent.check_cache(self.LOGAN_CACHE_KEY)

        self.assertTrue(checked, "Actions config object isn't in the cache")


    def test_should_be_able_to_found_action_from_key(self):
        """ Test find an action by providing its key name
        """

        # Initialize the agent by changing the default config file location
        self.agent = Agent(self.LOGAN_ROOT)

        action = self.agent.find_action(self.LOGAN_TEST_ACTION)