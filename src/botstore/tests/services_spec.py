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
        self.token = 'token'

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
        bot_details = get_bot(self.token, 1)

        # If the request is sent successfully, then I expect a response to be
        # returned.
        self.assertDictEqual(bot_details, response['item'])


class TestGetBots(TestCase):

    def setUp(self):
        self.token = 'token'

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
        bots_list = get_bots(self.token, 'other')

        # If the request is sent successfully, then I expect a response to be
        # returned.
        self.assertListEqual(bots_list, response['items'])


class TestGetCategories(TestCase):

    def setUp(self):
        self.token = 'token'

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
        categories = get_categories(self.token)

        # If the request is sent successfully, then I expect a response to be
        # returned.
        self.assertDictEqual(categories, response['categories'])
