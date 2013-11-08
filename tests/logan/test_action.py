from unittest.case import TestCase
from logan import Action
from logan.exceptions import ActionAttributesMissingError


class TestAction(TestCase):


    def setUp(self):

        self.action = None

        self.ACTION_COMMAND             = "create:file filename.txt"
        self.ACTION_ACTION_WITH_CONTEXT = "create:file:linux filename.txt"
        self.NO_ACTION_PARAMS  = None


    def test_raises_when_trying_to_create_action_without_any_params(self):
        """ Raises and error when you try to create an action by
            providing no action attributes as parameters
        """

        self.failUnlessRaises(ActionAttributesMissingError, Action)


    def test_should_set_action_attributes_from_command_without_context(self):
        """ Validates the setting of action's attributes from a command without
            a provided context
        """

        # Without action context
        # The initialization process set action attributes
        self.action = Action(self.ACTION_COMMAND)

        # Check if attributes have been correctly set
        self.assertEqual(self.action.get_attr("verb")  , "create"      , "VERB doesn't match")
        self.assertEqual(self.action.get_attr("object"), "file"        , "FILE doesn't match")
        self.assertEqual(self.action.get_attr("params"), "filename.txt", "PARAMS doesn't match")