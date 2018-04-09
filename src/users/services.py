import logging

import urllib.parse     # used for encoding new user creation

from app.services import fetch_api

logger = logging.getLogger(__name__)


def get_user_token(api_admin_token, user_id):
    """Returns a user API Authentication Token"""
    return fetch_api(
        '/admin/{user_id}/devToken/', token=api_admin_token, user_id=user_id
    )


def get_info(token, dev_id):
    """Request a developer info"""
    return fetch_api('/developer/{dev_id}', token=token, dev_id=dev_id)


def post_user(api_admin_token, user_data):
    """Create a user"""
    return fetch_api(
        '/admin/?email={email}&username={username}&first_name={first_name}&last_name={last_name}',
        token=api_admin_token,
        email=urllib.parse.quote_plus(user_data.email),
        username=urllib.parse.quote_plus(user_data.username),
        first_name=urllib.parse.quote_plus(user_data.first_name),
        last_name=urllib.parse.quote_plus(user_data.last_name),
        method='post'
    )


def post_info(token, dev_id, info_data):
    """Save developer info"""
    return fetch_api(
        '/developer/{dev_id}',
        token=token,
        dev_id=dev_id,
        data=info_data,
        method='post'
    )
