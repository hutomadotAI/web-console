from unittest.mock import Mock, patch
from test_plus.test import TestCase

from users.tests.factories import AnonymousUserFactory, UserFactory
from studio.services import get_ai_list
from studio.tests.factories import AiFactory


class TestAi(TestCase):

    def setUp(self):
        """
        Allow to fake reCaptcha Success
        """
        self.user = UserFactory()

    @patch('botstore.services.requests.get')
    def test_anonymous(self, mock_get):
        """
        Anonymous user shouldn't get a list
        """
        user = AnonymousUserFactory()

        # Configure the mock to return a response with an OK status code.
        mock_get.return_value.ok = False
        mock_get.return_value.status_code = 401
        bot_details = get_ai_list(user)

        self.assertIsNone(bot_details)

    @patch('botstore.services.requests.get')
    def test_registered(self, mock_get):
        """
        Registered user can get AIs list
        """

        # Configure the mock to return a response with an OK status code.
        mock_get.return_value.ok = True
        mock_get.return_value.status_code = 200
        bot_details = get_ai_list(self.user)

        self.assertIsNotNone(bot_details)
