import logging
import requests

from django.conf import settings

from app.services import set_headers

logger = logging.getLogger(__name__)


def get_ai_list(token):
    """
    Returnes a list of all bots created by a user
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
