import factory

from unittest.mock import Mock, patch
from test_plus.test import TestCase

from users.tests.factories import AnonymousUserFactory, UserFactory
from botstore.services import get_bot, get_bots, get_categories
from botstore.tests.factories import BotDetailsFactory


class TestGetBot(TestCase):

    def setUp(self):
        """
        Allow to fake reCaptcha Success
        """
        self.user = UserFactory()

    @patch('botstore.services.requests.get')
    def test_get_bot_anonymous(self, mock_get):
        """
        Anonymous user can get a bot detail card
        """
        user = AnonymousUserFactory()

        # Configure the mock to return a response with an OK status code.
        mock_get.return_value.ok = True
        bot_details = get_bot(user, 1)

        self.assertIsNotNone(bot_details)

    @patch('botstore.services.requests.get')
    def test_get_bot_registered(self, mock_get):
        """
        Registered user can get a bot detail card too
        """

        # Configure the mock to return a response with an OK status code.
        mock_get.return_value.ok = True
        bot_details = get_bot(self.user, 1)

        self.assertIsNotNone(bot_details)

    @patch('botstore.services.requests.get')
    def test_get_bot_data(self, mock_get):
        """
        Response contains bot details dictionary
        """
        response = {
            'item': factory.build(dict, FACTORY_CLASS=BotDetailsFactory),
            'status': {
                'code': 200,
                'info': 'OK'
            }
        }

        # Configure the mock to return a response with an OK status code, and
        # mocked data.
        mock_get.return_value = Mock(ok=True)
        mock_get.return_value.json.return_value = response

        # Call the service, which will send a request to the server.
        bot_details = get_bot(self.user, 1)

        # If the request is sent successfully, then I expect a response to be
        # returned.
        self.assertDictEqual(bot_details, response['item'])


class TestGetBots(TestCase):

    def setUp(self):
        self.user = UserFactory()

    @patch('botstore.services.requests.get')
    def test_get_bots_anonymous(self, mock_get):
        """
        Anonymous user can get a bots list
        """
        user = AnonymousUserFactory()

        # Configure the mock to return a response with an OK status code.
        mock_get.return_value.ok = True
        bot_details = get_bots(user, 'other')

        self.assertIsNotNone(bot_details)

    @patch('botstore.services.requests.get')
    def test_get_bots_registered(self, mock_get):
        """
        Registered user can get a bots list too
        """

        # Configure the mock to return a response with an OK status code.
        mock_get.return_value.ok = True
        bot_details = get_bots(self.user, 'other')

        self.assertIsNotNone(bot_details)

    @patch('botstore.services.requests.get')
    def test_get_bots_data(self, mock_get):
        """
        Response contains a list of bots details
        """
        response = {
            'items': [
                factory.build(dict, FACTORY_CLASS=BotDetailsFactory),
                factory.build(dict, FACTORY_CLASS=BotDetailsFactory),
            ],
            'page_start': 0,
            'total_page': 7,
            'total_results': 7,
            'status': {
                'code': 200,
                'info': 'OK'
            }
        }

        # Configure the mock to return a response with an OK status code, and
        # mocked data.
        mock_get.return_value = Mock(ok=True)
        mock_get.return_value.json.return_value = response

        # Call the service, which will send a request to the server.
        bots_list = get_bots(self.user, 'other')

        # If the request is sent successfully, then I expect a response to be
        # returned.
        self.assertListEqual(bots_list, response['items'])


class TestGetCategories(TestCase):

    def setUp(self):
        self.user = UserFactory()

    @patch('botstore.services.requests.get')
    def test_get_categories_anonymous(self, mock_get):
        """
        Anonymous user can get categories
        """
        user = AnonymousUserFactory()

        # Configure the mock to return a response with an OK status code.
        mock_get.return_value.ok = True
        bot_details = get_categories(user)

        self.assertIsNotNone(bot_details)

    @patch('botstore.services.requests.get')
    def test_get_categories_registered(self, mock_get):
        """
        Registered user can get categories too
        """

        # Configure the mock to return a response with an OK status code.
        mock_get.return_value.ok = True
        bot_details = get_categories(self.user)

        self.assertIsNotNone(bot_details)

    @patch('botstore.services.requests.get')
    def test_get_categories_data(self, mock_get):
        """
        Response contains a categories dictionary of bots lists
        """
        response = {
            'categories': {
                'Social': [
                        factory.build(dict, FACTORY_CLASS=BotDetailsFactory),
                        factory.build(dict, FACTORY_CLASS=BotDetailsFactory),
                ],
            },
            'status': {
                'code': 200,
                'info': 'OK'
            }
        }

        # Configure the mock to return a response with an OK status code, and
        # mocked data.
        mock_get.return_value = Mock(ok=True)
        mock_get.return_value.json.return_value = response

        # Call the service, which will send a request to the server.
        categories = get_categories(self.user)

        # If the request is sent successfully, then I expect a response to be
        # returned.
        self.assertDictEqual(categories, response['categories'])
