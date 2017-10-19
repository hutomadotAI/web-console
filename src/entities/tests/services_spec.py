import factory

from unittest.mock import Mock, patch
from test_plus.test import TestCase

from entities.services import get_entity, get_entities
from entities.tests.factories import EntityFactory, EntitiesFactory


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

