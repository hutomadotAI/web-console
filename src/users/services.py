import logging

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


def post_user(api_admin_token):
    """Create a user"""
    return fetch_api('/admin/', token=api_admin_token, method='post')


def post_info(token, dev_id, info_data):
    """Save developer info"""
    return fetch_api(
        '/developer/{dev_id}',
        token=token,
        dev_id=dev_id,
        data=info_data,
        method='post'
    )
