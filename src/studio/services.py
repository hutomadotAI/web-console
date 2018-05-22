import logging
import urllib

from constance import config
from django.conf import settings
from app.services import fetch_api

from redis.exceptions import ResponseError, ConnectionError

logger = logging.getLogger(__name__)

try:
    API_LOGS_TIMEOUT = config.API_LOGS_TIMEOUT
    API_FACEBOOK_TIMEOUT = config.API_FACEBOOK_TIMEOUT
    API_CHAT_TIMEOUT = config.API_CHAT_TIMEOUT
except (ConnectionError, ResponseError) as e:
    logger.warning('Django constance failed to use Redis, falling back to Settings')
    API_LOGS_TIMEOUT = settings.API_LOGS_TIMEOUT
    API_FACEBOOK_TIMEOUT = settings.API_FACEBOOK_TIMEOUT
    API_CHAT_TIMEOUT = settings.API_CHAT_TIMEOUT


def delete_ai(token, aiid):
    """Deletes a particular AI"""
    return fetch_api('/ai/{aiid}', token=token, aiid=aiid, method='delete')


def delete_entity(token, entity_name):
    """Delete an entity"""
    return fetch_api(
        '/entity?entity_name={entity_name}',
        token=token,
        entity_name=entity_name,
        method='delete'
    )


def delete_intent(token, aiid, intent_name):
    """Delete an Intent"""
    return fetch_api(
        '/intent/{aiid}?intent_name={intent_name}',
        token=token,
        aiid=aiid,
        intent_name=intent_name,
        method='delete'
    )


def get_ai(token, aiid):
    """Returns a particular AI data"""
    return fetch_api('/ui/ai/{aiid}', token=token, aiid=aiid)


def get_ai_details(token, aiid):
    """Returns a particular AI detailed data"""
    return fetch_api('/ui/ai/{aiid}/details', token=token, aiid=aiid)


def get_ai_export(token, aiid):
    """Returns an AI export JSON data"""
    return fetch_api('/ai/{aiid}/export', token=token, aiid=aiid)


def get_ai_list(token):
    """Returns a list of all bots created by a user"""
    return fetch_api('/ai', token=token)


def get_ai_skill(token, aiid):
    """Get skills linked with an AI"""
    return fetch_api('/ai/{aiid}/bots', token=token, aiid=aiid)


def get_ai_training(token, aiid):
    """Get training content of an AI"""
    return fetch_api('/ai/{aiid}/training/materials', token=token, aiid=aiid)


def get_entities_list(token):
    """Returns a list of all entities for a user"""
    return fetch_api('/entities', token=token)


def get_entity(token, entity_name):
    """Returns a particular entity data"""
    return fetch_api(
        '/entity?entity_name={entity_name}',
        token=token,
        entity_name=entity_name
    )


def get_intent_list(token, aiid):
    """Returns a list of all intents for a particular AI"""
    return fetch_api('/intents/{aiid}', token=token, aiid=aiid)


def get_intent(token, aiid, intent_name):
    """Returns a particular intent data"""
    return fetch_api(
        '/intent/{aiid}?intent_name={intent_name}',
        token=token,
        aiid=aiid,
        intent_name=intent_name
    )


def get_facebook_connect_state(token, aiid):
    """Reads the facebook connection status for this aiid"""
    return fetch_api(
        '/ai/{aiid}/facebook',
        token=token,
        aiid=aiid,
        timeout=API_FACEBOOK_TIMEOUT
    )


def get_facebook_customisations(token, aiid):
    """load customisations for the page"""
    return fetch_api(
        '/ai/{aiid}/facebook/custom',
        token=token,
        aiid=aiid,
        timeout=API_FACEBOOK_TIMEOUT
    )


def get_insights_chart(token, aiid, metric, fromDate, toDate):
    """get chart data for the specified dates"""
    return fetch_api(
        '/insights/{aiid}/graph/{metric}?from={fromDate}&to={toDate}',
        token=token,
        aiid=aiid,
        metric=metric,
        fromDate=fromDate,
        toDate=toDate,
        timeout=API_LOGS_TIMEOUT,
    )


def get_insights_chatlogs(token, aiid, fromDate, toDate):
    """Gets chat logs for the specified dates"""
    return fetch_api(
        '/insights/{aiid}/chatlogs?format=csv&from={fromDate}&to={toDate}',
        token=token,
        aiid=aiid,
        fromDate=fromDate,
        toDate=toDate,
        timeout=API_LOGS_TIMEOUT,
        raw=True
    )


def post_ai(token, ai_data, aiid=''):
    """Creates or updates an AI instance"""
    ai_default = {
        'voice': 1,
        'is_private': False,
        'personality': 0,
        'confidence': 0.4,
        'locale': 'en-US'
    }

    return fetch_api(
        '/ai/{aiid}',
        token=token,
        aiid=aiid,
        method='post',
        data={**ai_default, **ai_data}
    )


def post_clone_ai(token, ai_data, aiid=''):
    """Creates or updates an AI instance"""
    ai_default = {
        'voice': 1,
        'is_private': False,
        'personality': 0,
        'confidence': 0.4,
        'locale': 'en-US'
    }

    return fetch_api(
        '/ai/{aiid}/clone',
        token=token,
        aiid=aiid,
        method='post',
        data={**ai_default, **ai_data}
    )


def post_import_ai(token, ai_data, aiid=''):
    """Creates a new AI instance based on provided JSON file"""
    return fetch_api(
        '/ai/import',
        token=token,
        method='post',
        headers={'Content-type': 'application/json'},
        data=ai_data
    )


def post_ai_skill(token, aiid, skills_data):
    """Updates skills linked with an AI"""
    return fetch_api(
        '/ai/{aiid}/bots?bot_list={bot_list}',
        token=token,
        aiid=aiid,
        bot_list=','.join(skills_data['skills']),
        method='post',
        headers={'Content-type': 'application/json'},
    )


def post_training(token, aiid, training_file):
    """Updates bot Training file"""
    return fetch_api(
        '/ai/{aiid}/training?source_type=0',
        token=token,
        aiid=aiid,
        files={'file': training_file},
        method='post'
    )


def post_regenerate_webhook_secret(token, aiid):
    """Generate a new Webhook secret"""
    return fetch_api(
        '/ai/{aiid}/regenerate_webhook_secret',
        token=token,
        aiid=aiid,
        method='post'
    )


def post_entity(payload, token, **kwargs):
    """Create or update an entity"""
    return fetch_api(
        '/entity?entity_name={entity_name}',
        token=token,
        entity_name=kwargs.get('entity_name', payload.get('entity_name')),
        json=payload,
        method='post'
    )


def post_intent(payload, token, aiid):
    """Create or update an Intent"""
    return fetch_api(
        '/intent/{aiid}',
        token=token,
        aiid=aiid,
        json=payload,
        method='post'
    )


def post_chat(token, aiid, payload):
    """Send chat message"""
    return fetch_api(
        '/ai/{aiid}/chat',
        token=token,
        aiid=aiid,
        params=payload,
        timeout=API_CHAT_TIMEOUT
    )


def post_facebook_connect_token(token, aiid, payload):
    """
        Registers a connect token once the user has completed a
        connect operation on the front-end
    """
    return fetch_api(
        '/ai/{aiid}/facebook/connect',
        token=token,
        aiid=aiid,
        json=payload,
        timeout=API_FACEBOOK_TIMEOUT,
        method='post'
    )


def post_facebook_customisations(token, aiid, payload):
    """save customisations for the page"""
    return fetch_api(
        '/ai/{aiid}/facebook/custom',
        token=token,
        aiid=aiid,
        json=payload,
        timeout=API_FACEBOOK_TIMEOUT,
        method='post'
    )


def post_handover_reset(token, aiid, chatId, target='ai'):
    """Reset handover status"""
    return fetch_api(
        '/ai/{aiid}/chat/target?chatId={chatId}&target={target}',
        token=token,
        aiid=aiid,
        chatId=chatId,
        target=target,
        timeout=API_FACEBOOK_TIMEOUT,
        method='post'
    )


def put_training_update(token, aiid):
    """Update AI training"""
    return fetch_api(
        '/ai/{aiid}/training/update', token=token, aiid=aiid, method='put'
    )


def put_training_start(token, aiid):
    """Start an AI training"""
    return fetch_api(
        '/ai/{aiid}/training/start', token=token, aiid=aiid, method='put'
    )


def put_facebook_action(token, aiid, params):
    """take some action on the facebook connection"""
    return fetch_api(
        '/ai/{aiid}/facebook?{query_string}',
        token=token,
        aiid=aiid,
        query_string=urllib.parse.urlencode(params),
        timeout=API_FACEBOOK_TIMEOUT,
        method='put'
    )
