import factory

from unittest.mock import Mock, patch
from test_plus.test import TestCase

from users.tests.factories import AnonymousUserFactory, UserFactory

from studio.services import get_ai_list, post_ai, post_import_ai, get_entity, get_entities, save_entity
from studio.tests.factories import (
    AiFactory,
    AIImportJSON,
    EntitiesFactory,
    EntityFactory,
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
        mock_get.return_value.json.return_value = factory.build(
            dict,
            FACTORY_CLASS=UnauthorizedFactory
        )

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
        mock_get.return_value.json.return_value = factory.build(
            dict,
            FACTORY_CLASS=SuccessFactory
        )

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

        response = post_import_ai(self.user, factory.build(
            dict,
            FACTORY_CLASS=AIImportJSON)
        )

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
        mock_get.return_value.json.return_value = factory.build(
            dict,
            FACTORY_CLASS=NameExistsFactory
        )

        response = post_import_ai(self.user, factory.build(
            dict,
            FACTORY_CLASS=AIImportJSON)
        )

        self.assertEqual(response['status']['code'], 400)
        self.assertEqual(
            response['status']['info'],
            'A bot with that name already exists'
        )

class TestGetEntity(TestCase):

    def setUp(self):
        """
        Allow to fake reCaptcha Success
        """
        self.token = 'token'

    @patch('entities.services.requests.get')
    def test_get_entity(self, mock_get):
        """
        Response contains entity details dictionary
        """
        response = {
            'item': factory.build(dict, FACTORY_CLASS=EntityFactory),
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
        entity_details = get_entity("entity_name", self.token)

        # If the request is sent successfully, then I expect a response to be
        # returned.
        self.assertDictEqual(entity_details, response['item'])


class TestGetEntities(TestCase):
    def setUp(self):
        """
        Allow to fake reCaptcha Success
        """
        self.token = 'token'

    @patch('entities.services.requests.get')
    def test_get_entities(self, mock_get):
        """
        Response contains bot details dictionary
        """
        response = {
            'item': factory.build(dict, FACTORY_CLASS=EntitiesFactory),
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
        entities = get_entities(self.token)

        # If the request is sent successfully, then I expect a response to be
        # returned.
        self.assertDictEqual(entities, response['item'])


class TestUpdateEntity(TestCase):
    def setUp(self):
        """
        Allow to fake reCaptcha Success
        """
        self.token = 'token'

    @patch('entities.services.requests.post')
    def test_get_entities(self, mock_get):
        """
        Response contains bot details dictionary
        """
        response = {
            'item': factory.build(dict, FACTORY_CLASS=EntitiesFactory),
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
        entities = save_entity("entityname", ["value1" "value2"], self.token)

        # If the request is sent successfully, then I expect a response to be
        # returned.
        self.assertDictEqual(entities, response['item'])
