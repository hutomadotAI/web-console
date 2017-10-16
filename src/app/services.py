import logging

logger = logging.getLogger(__name__)


def set_headers(token):
    """
    Add required Authentication headers
    """

    headers = {'Authorization': 'Bearer %s' % token} if token else {}

    logger.debug('header %s set' % headers)

    return headers
