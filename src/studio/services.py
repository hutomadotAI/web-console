import logging
import urllib

import requests

from django.conf import settings
from django.http import Http404
from django.utils.translation import ugettext_lazy as _

from app.services import set_headers

logger = logging.getLogger(__name__)


def get_ai(token, aiid):
    """Returns a particular AI data"""

    path = '/ai/%s'
    url = settings.API_URL + path % aiid

    logger.debug(url)

    response = requests.get(
        url,
        headers=set_headers(token),
        timeout=settings.API_TIMEOUT
    )

    logger.debug(response)

    if response.status_code in [401, 403, 404]:
        # We don't reveal if AI exist
        raise Http404(_('AI id %s doesn’t exist') % aiid)

    return response.json()


def delete_ai(token, aiid):
    """Returns a particular AI data"""

    path = '/ai/%s'
    url = settings.API_URL + path % aiid

    logger.debug(url)

    response = requests.delete(
        url,
        headers=set_headers(token),
        timeout=settings.API_TIMEOUT
    )

    logger.debug(response)

    if response.status_code in [401, 403, 404]:
        # We don't reveal if AI exist
        raise Http404(_('AI id %s doesn’t exist') % aiid)

    return response.json()


def get_ai_export(token, aiid):
    """Returns an AI export JSON data"""

    path = '/ai/%s/export'
    url = settings.API_URL + path % aiid

    logger.debug(url)

    response = requests.get(
        url,
        headers=set_headers(token),
        timeout=settings.API_TIMEOUT
    )

    logger.debug(response)

    if response.status_code in [401, 403, 404]:
        # We don't reveal if AI exist
        raise Http404(_('AI id %s doesn’t exist') % aiid)

    return response.json()


def get_ai_list(token):
    """Returns a list of all bots created by a user"""

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


def post_ai(token, ai_data, aiid=''):
    """Creates or updates an AI instance"""

    ai_default = {
        'voice': 1,
        'is_private': False,
        'personality': 0,
        'confidence': 0.4,
        'locale': 'en-US',
    }

    path = '/ai/%s'
    url = settings.API_URL + path % aiid

    logger.debug([url, ai_data])

    response = requests.post(
        url,
        headers=set_headers(token),
        timeout=settings.API_TIMEOUT,
        data={**ai_default, **ai_data}
    )

    logger.debug(response)

    return response.json()


def post_import_ai(token, ai_data):
    """Creates a new AI instance based on provided JSON file"""

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

    return response.json()


def post_ai_skill(token, aiid, skills_data):
    """Updates skills linked with an AI"""

    path = '/ai/%s/bots?bot_list=%s'
    url = settings.API_URL + path % (
        aiid,
        ','.join(skills_data['skills'])
    )

    logger.debug(url)

    headers = set_headers(token)

    response = requests.post(
        url,
        headers=headers,
        timeout=settings.API_TIMEOUT,
        data=skills_data
    )

    logger.debug(response)

    return response.json()


def post_training(token, aiid, training_file):
    """Updates bot Training file"""

    path = '/ai/%s/training?source_type=0'
    url = settings.API_URL + path % aiid

    logger.debug(url)

    response = requests.post(
        url,
        headers=set_headers(token),
        timeout=settings.API_TIMEOUT,
        files={
            'file': training_file
        }
    )

    logger.debug(response)

    return response.json()


def put_training_update(token, aiid):
    """Update AI training"""

    path = '/ai/%s/training/update'
    url = settings.API_URL + path % aiid

    logger.debug(url)

    response = requests.put(
        url,
        headers=set_headers(token),
        timeout=settings.API_TIMEOUT,
    )

    logger.debug(response)

    return response.json()


def put_training_start(token, aiid):
    """Start AI training"""

    path = '/ai/%s/training/start'
    url = settings.API_URL + path % aiid

    logger.debug(url)

    response = requests.put(
        url,
        headers=set_headers(token),
        timeout=settings.API_TIMEOUT,
    )

    logger.debug(response)

    return response.json()


def put_training_start(token, aiid):
    """Start an AI training"""

    path = '/ai/%s/training/start'
    url = settings.API_URL + path % aiid

    logger.debug(url)

    response = requests.put(
        url,
        headers=set_headers(token),
        timeout=settings.API_TIMEOUT,
    )

    logger.debug(response)

    return response.json()


def post_regenerate_webhook_secret(token, aiid):
    """Generate a new Webhook secret"""

    path = '/ai/%s/regenerate_webhook_secret'
    url = settings.API_URL + path % aiid

    logger.debug(url)

    response = requests.post(
        url,
        headers=set_headers(token),
        timeout=settings.API_TIMEOUT,
    )

    logger.debug(response)

    return response.json()


def get_entities_list(token):
    """Returns a list of all entities for a user"""

    path = '/entities/'
    url = settings.API_URL + path

    logger.debug([url, token])

    response = requests.get(
        url,
        headers=set_headers(token),
        timeout=settings.API_TIMEOUT
    )

    logger.debug(response)

    if response.status_code in [401, 403, 404]:
        # We don't reveal if AI exist
        raise Http404(_('AI doesn’t exist'))

    return response.json()


def get_entity(token, entity_name):
    """Returns a particular entity data"""

    path = '/entity?entity_name=%s'
    url = settings.API_URL + path % entity_name

    logger.debug(url)

    response = requests.get(
        url,
        headers=set_headers(token),
        timeout=settings.API_TIMEOUT
    )

    logger.debug(response)

    if response.status_code in [401, 403, 404]:
        raise Http404(_('entity %s doesn’t exist') % entity_name)

    return response.json()


def post_entity(payload, token, **kwargs):
    """Create or update an entity"""

    path = '/entity?entity_name=%s'
    url = settings.API_URL + path % kwargs.get(
        'entity_name',
        payload.get('entity_name')
    )

    logger.debug([url, payload])

    response = requests.post(
        url,
        headers=set_headers(token),
        timeout=settings.API_TIMEOUT,
        json=payload
    )

    logger.debug(response)

    return response.json()


def delete_entity(token, entity_name):
    """Delete an entity"""

    path = '/entity?entity_name=%s'
    url = settings.API_URL + path % entity_name

    logger.debug(url)

    response = requests.delete(
        url,
        headers=set_headers(token),
        timeout=settings.API_TIMEOUT,
    )

    logger.debug(response)

    return response.json()


def get_intent_list(token, aiid):
    """Returns a list of all intents for a particular AI"""

    path = '/intents/%s'
    url = settings.API_URL + path % aiid

    logger.debug(url)

    response = requests.get(
        url,
        headers=set_headers(token),
        timeout=settings.API_TIMEOUT
    )

    logger.debug(response)

    if response.status_code in [401, 403, 404]:
        # We don't reveal if AI exist
        raise Http404('AI id %s doesn’t exist' % aiid)

    return response.json()


def get_intent(token, aiid, intent_name):
    """Returns a particular intent data"""

    path = '/intent/%s?intent_name=%s'
    url = settings.API_URL + path % (aiid, intent_name)

    logger.debug(url)

    response = requests.get(
        url,
        headers=set_headers(token),
        timeout=settings.API_TIMEOUT
    )

    logger.debug(response)

    if response.status_code in [401, 403, 404]:
        # We don't reveal if AI exist
        raise Http404('AI id %s doesn’t exists' % aiid)

    return response.json()


def post_intent(payload, token, aiid):
    """Create or update an Intent"""

    path = '/intent/%s'
    url = settings.API_URL + path % aiid

    logger.debug([url, payload])

    response = requests.post(
        url,
        headers=set_headers(token),
        timeout=settings.API_TIMEOUT,
        json=payload
    )

    logger.debug(response)

    if response.status_code in [401, 403, 404]:
        # We don't reveal if AI exist
        raise Http404('AI id %s doesn’t exists' % aiid)

    return response.json()


def delete_intent(token, aiid, intent_name):
    """Delete an Intent"""

    path = '/intent/%s?intent_name=%s'
    url = settings.API_URL + path % (
        aiid,
        intent_name
    )

    logger.debug(url)

    response = requests.delete(
        url,
        headers=set_headers(token),
        timeout=settings.API_TIMEOUT,
    )

    logger.debug(response)

    if response.status_code in [401, 403, 404]:
        # We don't reveal if AI exist
        raise Http404('AI id %s doesn’t exists' % aiid)

    return response.json()


def set_facebook_connect_token(token, aiid, connect_token, redirect_url):
    """ Registers a connect token once the user has completed a
        connect operation on the front-end
    """

    path = '/ai/%s/facebook/connect'
    url = settings.API_URL + path % aiid

    payload = {
        'connect_token': connect_token,
        'redirect_uri': redirect_url
    }

    logger.debug(url)

    response = requests.post(
        url,
        headers=set_headers(token),
        timeout=settings.API_FACEBOOK_TIMEOUT,
        json=payload
    )

    logger.debug(response)

    return response.json()


def get_facebook_connect_state(token, aiid):
    """
    read the facebook connection status for this aiid
    """
    path = '/ai/%s/facebook'
    url = settings.API_URL + path % aiid

    logger.debug(url)

    response = requests.get(
        url,
        headers=set_headers(token),
        timeout=settings.API_TIMEOUT
    )

    logger.debug(response)

    return response.json()


def facebook_action(token, aiid, params):
    """
    take some action on the facebook connection
    """
    query_string = urllib.parse.urlencode(params)
    path = '/ai/%s/facebook?%s'
    url = settings.API_URL + path % (aiid, query_string)

    logger.debug(url)

    response = requests.put(
        url,
        headers=set_headers(token),
        timeout=settings.API_FACEBOOK_TIMEOUT
    )

    logger.debug(response)

    return response.json()


def get_facebook_customisations(token, aiid):
    """
    load customisations for the page
    """
    path = '/ai/%s/facebook/custom'
    url = settings.API_URL + path % aiid

    logger.debug(url)

    response = requests.get(
        url,
        headers=set_headers(token),
        timeout=settings.API_TIMEOUT
    )

    logger.debug(response)

    return response.json()


def set_facebook_customisations(token, aiid, page_greeting, get_started):
    """
    save customisations for the page
    """
    path = '/ai/%s/facebook/custom'
    url = settings.API_URL + path % aiid

    payload = {
        'page_greeting': page_greeting,
        'get_started_payload': get_started
    }

    logger.debug(url)

    response = requests.post(
        url,
        headers=set_headers(token),
        timeout=settings.API_TIMEOUT,
        json=payload
    )

    logger.debug(response)

    return response.json()


def get_insights_chatlogs(token, aiid, fromDate, toDate):
    """
    get chat logs for the specified dates
    """
    path = '/insights/%s/chatlogs?format=csv&from=%s&to=%s'
    url = settings.API_URL + path % (aiid, fromDate, toDate)

    logger.debug(url)

    response = requests.get(
        url,
        headers=set_headers(token),
        timeout=settings.API_LOGS_TIMEOUT
    )

    logger.debug(response)
    return response


def get_insights_chart(token, aiid, fromDate, toDate, data_type):
    """
    get chart data for the specified dates
    """
    path = '/insights/%s/graph/%s?from=%s&to=%s'
    url = settings.API_URL + path % (aiid, data_type, fromDate, toDate)

    logger.debug(url)

    response = requests.get(
        url,
        headers=set_headers(token),
        timeout=settings.API_LOGS_TIMEOUT
    )

    logger.debug(response)

    return response.json()
