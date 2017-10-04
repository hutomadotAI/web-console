import logging

from users.models import Users

logger = logging.getLogger(__name__)


def set_headers(user):
    """
    Add required Authentication headers
    """

    if user.is_anonymous():
        headers = {}
    else:
        legacy_user = Users.objects.get(user=user)
        headers = {
            'Authorization': 'Bearer %s' % legacy_user.token
        }

    logger.debug('header %s set for user %s' % (
        headers,
        user
    ))

    return headers
