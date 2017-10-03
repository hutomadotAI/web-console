import logging
import requests
import urllib

from django.conf import settings

from users.models import Users

logger = logging.getLogger(__name__)


def get_headers(user):
    if user.is_anonymous():
        headers = {}
    else:
        legacy_user = Users.objects.get(user=user)
        headers = {
            'Authorization': 'Bearer %s' % legacy_user.token
        }
    return headers


def get_categories(user, start=0, offset=8):
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
        headers=get_headers(user),
        timeout=settings.API_TIMEOUT
    ).json()

    categories = responsJSON['categories']

    logger.debug(categories)

    return responsJSON['categories']


def get_bots(user, category, start=0, offset=24):
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
        headers=get_headers(user),
        timeout=settings.API_TIMEOUT
    ).json()

    bots = responsJSON['items']

    logger.debug(bots)

    return bots


def get_bot(user, pk):
    """
    Returnes detils about a single bot
    """

    path = '/ui/botstore/%d'
    url = settings.API_URL + path % (pk)

    logger.debug(url)

    responsJSON = requests.get(
        url,
        headers=get_headers(user),
        timeout=settings.API_TIMEOUT
    ).json()

    bot = responsJSON['item']

    logger.debug(bot)

    return bot
