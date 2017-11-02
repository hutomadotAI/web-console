import logging
import requests

from django.conf import settings
from django.http import Http404

from app.services import set_headers

logger = logging.getLogger(__name__)


def get_ai(token, aiid):
    """
    Returns a particular AI data
    """

    path = '/ai/%s'
    url = settings.API_URL + path % aiid

    logger.debug(url)

    response = requests.get(
        url,
        headers=set_headers(token),
        timeout=settings.API_TIMEOUT
    )

    logger.debug(response)

    if response.status_code in [401, 403, 404]:
        """
        We don't revile if AI exists
        """
        raise Http404('AI id %s doesn’t exists' % aiid)

    ai = response.json()

    #
    ai['training'] = {
        'status': ai['ai_status'],
        'progress': 100 * (
            ai['phase_1_progress'] * 0.5 + ai['phase_2_progress'] * 1.5
            ) / 2
    }

    logger.debug(ai)

    return ai


def get_ai_list(token):
    """
    Returns a list of all bots created by a user
    """

    path = '/ai'
    url = settings.API_URL + path

    logger.debug(url)

    response = requests.get(
        url,
        headers=set_headers(token),
        timeout=settings.API_TIMEOUT
    )

    if response.status_code == 200:
        responseJSON = response.json()
        ai_list = responseJSON['ai_list']
    else:
        ai_list = None

    logger.debug(ai_list)

    return ai_list


def post_ai(token, ai_data):
    """
    Post an AI instance
    """

    ai_default = {
        'is_private': False,
        'personality': 0,
        'confidence': 0.4,
        'locale': 'en-US',
    }

    path = '/ai'
    url = settings.API_URL + path

    logger.debug(url)

    response = requests.post(
        url,
        headers=set_headers(token),
        timeout=settings.API_TIMEOUT,
        data={**ai_default, **ai_data}
    )

    logger.debug(response)

    ai = response.json()

    logger.debug(ai)

    return ai


def post_import_ai(token, ai_data):
    """
    Post an AI import JSON
    """

    path = '/ai/import'
    url = settings.API_URL + path

    logger.debug(url)

    headers = set_headers(token)
    headers['Content-type'] = 'application/json'

    response = requests.post(
        url,
        headers=headers,
        timeout=settings.API_TIMEOUT,
        data=ai_data
    )

    logger.debug(response)

    ai = response.json()

    logger.debug(ai)

    return ai


def post_ai_skill(token, aiid, skills_data):
    """
    Post skills linked with an AI
    """

    path = '/ai/%s/bots?bot_list=%s'
    url = settings.API_URL + path % (
        aiid,
        ','.join(skills_data['skills'])
    )

    logger.debug(url)

    headers = set_headers(token)

    response = requests.post(
        url,
        headers=headers,
        timeout=settings.API_TIMEOUT,
        data=skills_data
    )

    logger.debug(response)

    skills = response.json()

    logger.debug(skills)

    return skills


def post_training(token, aiid, training_file):
    """
    Post skills linked with an AI
    """

    path = '/ai/%s/training?source_type=0'
    url = settings.API_URL + path % aiid

    logger.debug(url)

    response = requests.post(
        url,
        headers=set_headers(token),
        timeout=settings.API_TIMEOUT,
        files={
            'file': training_file
        }
    )

    logger.debug(response)

    ai = response.json()

    logger.debug(ai)

    return ai


def put_training_start(token, aiid):
    """
    Start an AI training
    """

    path = '/ai/%s/training/start'
    url = settings.API_URL + path % aiid

    logger.debug(url)

    response = requests.put(
        url,
        headers=set_headers(token),
        timeout=settings.API_TIMEOUT,
    )

    logger.debug(response)

    ai = response.json()

    logger.debug(ai)

    return ai

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


def delete_entity(entityName, token=False):
    """
    Delete a specific entity.
    :param entityName: The name of the entity.
    :param entityValues: The values in the entity.
    :param token: The user token.
    :return:
    """
    path = '/entity?entity_name={0}'
    url = settings.API_URL + path.format(entityName)

    logger.debug(url)

    response = requests.delete(
        url,
        headers=set_headers(token),
        timeout=settings.API_TIMEOUT
    )

    logger.debug(response)
