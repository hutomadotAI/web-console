import json
import logging
import requests
import urllib

from django.contrib.auth.models import AnonymousUser, User

from django.conf import settings

from app.services import set_headers

logger = logging.getLogger(__name__)


def get_categories(token=False, start=0, offset=8):
    """
    Returnes a list of categories, with a list bots in each of them
    """

    path = '/ui/botstore/per_category?startFrom={0}&pageSize={1}'
    url = settings.API_URL + path.format(
        start,
        offset
    )

    logger.debug(url)

    responsJSON = requests.get(
        url,
        headers=set_headers(token),
        timeout=settings.API_TIMEOUT,
        verify=not settings.DEBUG
    ).json()

    categories = responsJSON['categories']

    logger.debug(categories)

    return responsJSON['categories']


def get_bots(category, token=False, start=0, offset=24):
    """
    Returnes a list lof bots filterd by category
    """

    path = '/ui/botstore?filter={0}&startFrom={1}&pageSize={2}'
    url = settings.API_URL + path.format(
        urllib.parse.quote_plus('category=\'%s\'' % category),
        start,
        offset
    )

    logger.debug(url)

    responsJSON = requests.get(
        url,
        headers=set_headers(token),
        timeout=settings.API_TIMEOUT,
        verify=not settings.DEBUG
    ).json()

    bots = responsJSON['items']

    logger.debug(bots)

    return bots


def get_bot(pk, token=False):
    """
    Returnes detils about a single bot
    """

    path = '/ui/botstore/%s'
    url = settings.API_URL + path % (pk)

    logger.debug(url)

    responsJSON = requests.get(
        url,
        headers=set_headers(token),
        timeout=settings.API_TIMEOUT,
        verify=not settings.DEBUG
    ).json()

    bot = responsJSON['item']

    logger.debug(bot)

    return bot


def get_purchased(token):
    """
    """

    path = '/botstore/purchased'
    url = settings.API_URL + path

    logger.debug(url)

    response = requests.get(
        url,
        headers=set_headers(token),
        timeout=settings.API_TIMEOUT,
        verify=not settings.DEBUG
    )

    logger.debug(response)

    skills = response.json()

    logger.debug(skills)

    return skills['bots']


def post_bot(token, aiid, bot_data, **kwargs):
    """Publish a bot"""

    path = '/botstore'
    url = settings.API_URL + path

    defaults = {
        'publishing_type': 1,
        'aiid': aiid,
    }

    logger.debug(url)

    respons = requests.post(
        url,
        headers=set_headers(token),
        timeout=settings.API_TIMEOUT,
        data={**defaults, **bot_data},
        verify=not settings.DEBUG
    )

    logger.debug(respons)

    return respons.json()


def post_icon(token, bot_id, icon_file, **kwargs):
    """Publish a bot"""

    path = '/botstore/%d/icon'
    url = settings.API_URL + path % bot_id

    logger.debug(url)

    respons = requests.post(
        url,
        headers=set_headers(token),
        timeout=settings.API_TIMEOUT,
        files={
            'file': icon_file
        },
        verify=not settings.DEBUG
    )

    logger.debug(respons.json())

    return respons.json()


def post_purchase(token, bot_id):
    """Purchase a bot"""

    path = '/botstore/purchase/%s'
    url = settings.API_URL + path % bot_id

    logger.debug(url)

    respons = requests.post(
        url,
        headers=set_headers(token),
        timeout=settings.API_TIMEOUT,
        verify=not settings.DEBUG
    )

    logger.debug(respons.json())

    return respons.json()
