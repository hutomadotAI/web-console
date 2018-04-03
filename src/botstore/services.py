import logging
import urllib

from app.services import fetch_api

logger = logging.getLogger(__name__)


def get_categories(token=False, start=0, offset=8):
    """Returns a list of categories, with a list bots in each of them"""
    return fetch_api(
        '/ui/botstore/per_category?startFrom={start}&pageSize={offset}',
        token=token,
        start=start,
        offset=offset
    )


def get_bots(category, token=False, start=0, offset=24):
    """Returns a list of bots, filtered by category"""
    return fetch_api(
        '/ui/botstore?filter={filter}&startFrom={start}&pageSize={offset}',
        token=token,
        filter=urllib.parse.quote_plus(
            'category=\'{category}\''.format(category=category)
        ),
        start=start,
        offset=offset
    )


def get_bot(bot_id, token=False):
    """Returns details about a single bot"""
    return fetch_api('/ui/botstore/{bot_id:d}', token=token, bot_id=bot_id)


def get_purchased(token):
    """Returns a list of purchased bots"""
    return fetch_api('/botstore/purchased', token=token)


def post_bot(token, aiid, bot_data):
    """Publish a bot"""
    defaults = {
        'publishing_type': 1,
        'aiid': aiid,
    }

    return fetch_api(
        '/botstore',
        token=token,
        data={**defaults, **bot_data},
        method='post'
    )


def post_icon(token, bot_id, icon_file):
    """Publish a bot"""
    return fetch_api(
        '/botstore/{bot_id:d}/icon',
        token=token,
        files={'file': icon_file},
        method='post'
    )


def post_purchase(token, bot_id):
    """Purchase a bot"""
    return fetch_api(
        '/botstore/purchase/{bot_id:d}',
        token=token,
        bot_id=bot_id,
        method='post'
    )
