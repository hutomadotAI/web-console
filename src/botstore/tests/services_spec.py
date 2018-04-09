import factory

from unittest.mock import patch
from test_plus.test import TestCase

from botstore.services import get_bot, get_bots, get_categories
from botstore.tests.factories import BotDetailsFactory


class TestGetBot(TestCase):

    def setUp(self):
        self.token = 'token'

    @patch('botstore.services.fetch_api')
    def test_get_bot_data(self, mock_fetch_api):
        """Response contains bot details dictionary"""
        response = {
            'item': factory.build(dict, FACTORY_CLASS=BotDetailsFactory),
            'status': {
                'code': 200,
                'info': 'OK'
            }
        }

        # Configure the mock to return a response with an OK status code, and
        # mocked data.
        mock_fetch_api.return_value = response

        # Call the service, which will send a request to the server.
        bot_details = get_bot(self.token, 1)

        # If the request is sent successfully, then I expect a response to be
        # returned.
        self.assertDictEqual(bot_details, response)


class TestGetBots(TestCase):

    def setUp(self):
        self.token = 'token'

    @patch('botstore.services.fetch_api')
    def test_get_bots_data(self, mock_get):
        """Response contains a list of bots details"""
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
        mock_get.return_value = response

        # Call the service, which will send a request to the server.
        bots_list = get_bots(self.token, 'other')

        # If the request is sent successfully, then I expect a response to be
        # returned.
        self.assertDictEqual(bots_list, response)


class TestGetCategories(TestCase):

    def setUp(self):
        self.token = 'token'

    @patch('botstore.services.fetch_api')
    def test_get_categories_data(self, mock_get):
        """Response contains a categories dictionary of bots lists"""
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
        mock_get.return_value = response

        # Call the service, which will send a request to the server.
        categories = get_categories(self.token)

        # If the request is sent successfully, then I expect a response to be
        # returned.
        self.assertDictEqual(categories, response)
