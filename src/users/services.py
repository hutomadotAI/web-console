import logging
import requests

import urllib.parse # used for encoding new user creation

from django.conf import settings

from app.services import set_headers

logger = logging.getLogger(__name__)


def get_user_token(api_admin_token, user_id):
    """
    Returns a user API Authentication Token
    """

    path = '/admin/%s/devToken/' % user_id
    url = settings.API_URL + path

    logger.debug(url)

    response = requests.get(
        url,
        headers=set_headers(api_admin_token),
        timeout=settings.API_TIMEOUT,
        verify=not settings.DEBUG
    )

    logger.debug(response)

    return response.json()


def post_user(api_admin_token, user_data):
    """Create a user"""

    path = '/admin/?email={0}&username={1}&first_name={2}&last_name={3}'
    url = settings.API_URL + path.format(
        urllib.parse.quote_plus(user_data.email),
        urllib.parse.quote_plus(user_data.username),
        urllib.parse.quote_plus(user_data.first_name),
        urllib.parse.quote_plus(user_data.last_name)
    )

    logger.debug([url, api_admin_token])

    response = requests.post(
        url,
        headers=set_headers(api_admin_token),
        timeout=settings.API_TIMEOUT,
        data={
            'email': user_data.email,
            'username': user_data.username,
            'first_name': user_data.first_name,
            'last_name': user_data.last_name,
        },
        verify=not settings.DEBUG
    )

    logger.debug(response)

    response = response.json()

    logger.debug(response)

    return response


def get_info(token, dev_id):
    """Request a developer info"""

    path = '/developer/%s' % dev_id
    url = settings.API_URL + path

    logger.debug(url)

    response = requests.get(
        url,
        headers=set_headers(token),
        timeout=settings.API_TIMEOUT,
        verify=not settings.DEBUG
    )

    logger.debug(response)

    return response.json()


def post_info(token, dev_id, info_data):
    """Save developer info"""

    path = '/developer/%s' % dev_id
    url = settings.API_URL + path

    logger.debug(url)

    response = requests.post(
        url,
        headers=set_headers(token),
        timeout=settings.API_TIMEOUT,
        data=info_data,
        verify=not settings.DEBUG
    )

    logger.debug(response)

    return response.json()
