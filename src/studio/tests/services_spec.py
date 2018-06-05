import factory

from unittest.mock import patch
from test_plus.test import TestCase

from studio.services import get_ai_list, post_import_ai
from studio.tests.factories import (
    AiFactory,
    AIImportJSON,
    NameExistsFactory,
    SuccessFactory,
    UnauthorizedFactory
)


class TestAIList(TestCase):

    def setUp(self):
        """Provide a user token"""
        self.token = 'token'

    @patch('studio.services.fetch_api')
    def test_anonymous(self, mock_get):
        """Anonymous user shouldn't get a list"""

        # Configure the mock
        mock_get.return_value = factory.build(
            dict,
            FACTORY_CLASS=UnauthorizedFactory
        )

        response = get_ai_list(self.token)

        self.assertEqual(response['status']['code'], 401)

    @patch('studio.services.fetch_api')
    def test_registered(self, mock_get):
        """Registered user can get AIs list"""

        # Configure the mock
        mock_get.return_value = {
            'ai_list': [],
            'status': {
                'code': 200
            }
        }
        response = get_ai_list(self.token)

        self.assertEqual(response['status']['code'], 200)


class TestImportAI(TestCase):

    def setUp(self):
        """Provide a user token"""
        self.token = 'token'
        self.created = {
            **factory.build(dict, FACTORY_CLASS=AiFactory),
            **factory.build(dict, FACTORY_CLASS=SuccessFactory)
        }

    @patch('studio.services.fetch_api')
    def test_anonymous(self, mock_get):
        """Anonymous user shouldn't be able to POST"""

        # Configure the mock
        mock_get.return_value = factory.build(
            dict,
            FACTORY_CLASS=UnauthorizedFactory
        )

        response = post_import_ai(False, {})

        self.assertEqual(response['status']['code'], 401)

    @patch('studio.services.fetch_api')
    def test_registered(self, mock_get):
        """Registered user can POST an Import JSON"""

        # Configure the mock
        mock_get.return_value = factory.build(
            dict,
            FACTORY_CLASS=SuccessFactory
        )

        response = post_import_ai(self.token, {})

        self.assertEqual(response['status']['code'], 201)

    @patch('studio.services.fetch_api')
    def test_import_success(self, mock_get):
        """If the bot is created we return 201 and bot info with AIID."""

        # Configure the mock
        mock_get.return_value = self.created

        response = post_import_ai(self.token, factory.build(
            dict,
            FACTORY_CLASS=AIImportJSON)
        )

        self.assertEqual(response['status']['code'], 201)
        self.assertEqual(self.created['aiid'], response['aiid'])

    @patch('studio.services.fetch_api')
    def test_import_existing_name(self, mock_get):
        """
        If a bot with the same name exists, API returns information about it
        """

        # Configure the mock
        mock_get.return_value = factory.build(
            dict,
            FACTORY_CLASS=NameExistsFactory
        )

        response = post_import_ai(self.token, factory.build(
            dict,
            FACTORY_CLASS=AIImportJSON)
        )

        self.assertEqual(response['status']['code'], 400)
        self.assertEqual(
            response['status']['info'],
            'A bot with that name already exists'
        )
