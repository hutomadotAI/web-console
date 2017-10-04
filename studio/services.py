import logging
import requests

from django.conf import settings

from app.services import set_headers

logger = logging.getLogger(__name__)


def get_ai_list(user):
    """
    Returnes a list of all bots created by a user
    """

    path = '/ai'
    url = settings.API_URL + path

    logger.debug(url)

    respons = requests.get(
        url,
        headers=set_headers(user),
        timeout=settings.API_TIMEOUT
    )

    if respons.status_code == 200:
        responsJSON = respons.json()
        ai_list = responsJSON['ai_list']
    else:
        ai_list = None

    logger.debug(ai_list)

    return ai_list
