import logging
import requests
import urllib

from django.contrib.auth.models import AnonymousUser, User

from django.conf import settings

from app.services import set_headers

logger = logging.getLogger(__name__)


def get_entities(token=False):
    """
    Returns a list of the users entities.
    """

    path = '/entities'
    url = settings.API_URL + path

    logger.debug(url)

    responseJSON = requests.get(
        url,
        headers=set_headers(token),
        timeout=settings.API_TIMEOUT
    ).json()

    entities = responseJSON['entities']

    logger.debug(entities)

    return entities

def get_entity(entityName, token=False):
    """
    Get a specific entity.
    :param token: The user token.
    :return: The entity JSON.
    """

    path = '/entity?entity_name={0}'
    url = settings.API_URL + path.format(entityName)

    logger.debug(url)

    entity = requests.get(
        url,
        headers=set_headers(token),
        timeout=settings.API_TIMEOUT
    ).json()

    logger.debug(entity)

    return entity


def save_entity(entityName, entityValues, token=False):
    """
    Save a specific entity.
    :param entityName: The name of the entity.
    :param entityValues: The values in the entity.
    :param token: The user token.
    :return:
    """
    path = '/entity?entity_name={0}'
    url = settings.API_URL + path.format(entityName)

    logger.debug(url)
    data = {
        "entity_name": entityName,
        "entity_values": entityValues
    }

    response = requests.post(
        url,
        headers=set_headers(token),
        timeout=settings.API_TIMEOUT,
        json=data
    )

    logger.debug(response)
