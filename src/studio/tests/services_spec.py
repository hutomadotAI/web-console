import factory

from unittest.mock import Mock, patch
from test_plus.test import TestCase

from users.tests.factories import AnonymousUserFactory, UserFactory

from studio.services import get_ai_list, post_ai, post_import_ai
from studio.tests.factories import (
    AiFactory,
    AIImportJSON,
    NameExistsFactory,
    SuccessFactory,
    UnauthorizedFactory
)


class TestAI(TestCase):

    def setUp(self):
        """
        Provide a user
        """
        self.user = UserFactory()

    @patch('studio.services.requests.get')
    def test_anonymous(self, mock_get):
        """
        Anonymous user shouldn't get a list
        """
        user = AnonymousUserFactory()

        # Configure the mock
        mock_get.return_value.ok = False
        mock_get.return_value.status_code = 401
        bot_details = get_ai_list(user)

        self.assertIsNone(bot_details)

    @patch('studio.services.requests.get')
    def test_registered(self, mock_get):
        """
        Registered user can get AIs list
        """

        # Configure the mock
        mock_get.return_value.ok = True
        mock_get.return_value.status_code = 200
        bot_details = get_ai_list(self.user)

        self.assertIsNotNone(bot_details)


class TestImportAI(TestCase):

    def setUp(self):
        """
        Provide a user
        """
        self.user = UserFactory()
        self.created = {
            **factory.build(dict, FACTORY_CLASS=AiFactory),
            **factory.build(dict, FACTORY_CLASS=SuccessFactory)
        }

    @patch('studio.services.requests.post')
    def test_anonymous(self, mock_get):
        """
        Anonymous user shouldn't be able to POST
        """
        user = AnonymousUserFactory()

        # Configure the mock
        mock_get.return_value.ok = False
        mock_get.return_value.status_code = 401
        mock_get.return_value.json.return_value = factory.build(dict, FACTORY_CLASS=UnauthorizedFactory)

        response = post_import_ai(user, {})

        self.assertEqual(response['status']['code'], 401)

    @patch('studio.services.requests.post')
    def test_registered(self, mock_get):
        """
        Registered user can POST an Import JSON
        """

        # Configure the mock
        mock_get.return_value.ok = True
        mock_get.return_value.status_code = 201
        mock_get.return_value.json.return_value = factory.build(dict, FACTORY_CLASS=SuccessFactory)

        response = post_import_ai(self.user, {})

        self.assertEqual(response['status']['code'], 201)

    @patch('studio.services.requests.post')
    def test_import_success(self, mock_get):
        """
        If the bot is created we return 201 and bot info with AIID.
        """

        # Configure the mock
        mock_get.return_value.ok = True
        mock_get.return_value.status_code = 201
        mock_get.return_value.json.return_value = self.created

        response = post_import_ai(self.user, factory.build(dict, FACTORY_CLASS=AIImportJSON))

        self.assertEqual(response['status']['code'], 201)
        self.assertEqual(self.created['aiid'], response['aiid'])

    @patch('studio.services.requests.post')
    def test_import_existing_name(self, mock_get):
        """
        If a bot with the same name exists, API returns information about it
        """

        # Configure the mock
        mock_get.return_value.ok = True
        mock_get.return_value.status_code = 400
        mock_get.return_value.json.return_value = factory.build(dict, FACTORY_CLASS=NameExistsFactory)

        response = post_import_ai(self.user, factory.build(dict, FACTORY_CLASS=AIImportJSON))

        self.assertEqual(response['status']['code'], 400)
        self.assertEqual(response['status']['info'], 'A bot with that name already exists')
