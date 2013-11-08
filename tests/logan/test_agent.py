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


    # HELPERS
    # =======

    def setupLogan(self):
        pass


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

        self.failUnlessRaises(LoganConfigFileNotExistsError, self.agent.get_default_config)


    def test_should_raise_when_the_config_file_is_not_well_formatted(self):
        """ Loads default config object """

        # Initialize the agent by changing the default config file location
        self.agent = Agent(self.LOGAN_ROOT)

        # Change the default config file path with the bad one
        self.agent.default_config_file_path = self.BAD_DEFAULT_CONFIG_FILEPATH

        self.failUnlessRaises(LoganLoadConfigError, self.agent.get_default_config)


    def test_should_return_default_configuration_when_requested(self):
        """ Loads default config object """

        # Initialize the agent by changing the default config file location
        self.agent = Agent(self.LOGAN_ROOT)

        # Try to load the default config object
        default_config = self.agent.get_default_config()

        self.assertIsNotNone(default_config, "Failed to load the default configuration")


    def test_should_contains_at_least_one_default_command(self):
        """ Checks if the excerpt config is in the default configuration file """

        # Initialize the agent by changing the default config file location
        self.agent = Agent(self.LOGAN_ROOT)

        # Try to load the default config object
        default_config = self.agent.get_default_config()

        self.assertIsNotNone(default_config.get("actions").get(self.LOGAN_TEST_ACTION))


    def test_shouldReturnsUserConfiguration(self):
        """ Loads user configuration """

        # Initialize the agent by changing the default config file location
        self.agent = Agent(self.LOGAN_ROOT)

        user_config = self.agent.get_user_config()

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

        default_config      = self.agent.get_default_config()
        user_config         = self.agent.get_user_config()
        overridden_config   = self.agent.get_config()

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


    def test_validates_user_command_as_a_right_user_actions(self):
        """ Validates a command and user actions and make sure the syntax is correct
        """

        # Initialize the agent by changing the default config file location
        self.agent = Agent(self.LOGAN_ROOT)

        # Testing that a simple good command passed
        isValid = self.agent.is_action_valid(self.LOGAN_TEST_COMMAND)
        self.assertTrue(isValid, "This simple command must be good")

        # Testing that a right command with a specified context passed
        isValid = self.agent.is_action_valid(self.LOGAN_TEST_COMMAND_WITH_CTX)
        self.assertTrue(isValid, "This command with context must be good")

        # Testing that an empty command or action failed
        isValid = self.agent.is_action_valid(self.LOGAN_TEST_EMPTY_COMMAND)
        self.assertFalse(isValid, "This empty command must be not valid")

        # Testing that a bad formatted command or action failed
        isValid = self.agent.is_action_valid(self.LOGAN_TEST_BAD_COMMAND)
        self.assertFalse(isValid, "This bad command must be not valid")




