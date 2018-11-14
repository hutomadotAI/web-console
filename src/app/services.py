import logging

from constance import config
from django.conf import settings
from django.core.cache import cache
from django.http import Http404
from django.utils.translation import ugettext_lazy as _
from json import JSONDecodeError
from requests import Request, Session, packages
from requests.packages.urllib3.exceptions import InsecureRequestWarning

logger = logging.getLogger(__name__)
packages.urllib3.disable_warnings(InsecureRequestWarning)

VERIFY = not settings.DEBUG

LEVELS = {
    2: logging.INFO,
    3: logging.INFO,
    4: logging.ERROR,
    5: logging.ERROR
}


class ResponseFormatError(Exception):
    pass


def set_headers(token):
    """Add required Authentication headers"""

    headers = {
        'Authorization': 'Bearer {token}'.format(token=token)
    } if token else {}
    return headers


def fetch_api(
    path, token, method='GET', data={}, json={}, files={}, headers={}, params={},
    timeout=0, verify=VERIFY, **kwargs
):
    """
    Fetches data from the API using token (if provided),logs request and
    response data, if in debug mode also logs CURL command
    """

    url = settings.API_URL + path.format(**kwargs)
    headers = {**headers, **set_headers(token)}

    timeout = timeout or config.API_DEFAULT_TIMEOUT

    session = Session()
    request = Request(
        method, url, data=data, json=json, files=files, headers=headers, params=params
    )
    response = session.send(request.prepare(), timeout=timeout, verify=verify)

    level = LEVELS.get(int(response.status_code / 100), logging.ERROR)

    extra = {
        'request_dev_id': cache.get(token, None),
        'request_method': method,
        'request_url': url,
        'response_status_code': response.status_code,
        'response_time_in_seconds': response.elapsed.total_seconds()
    }

    if settings.DEBUG:
        # Print curl for debug purpose
        to_curl(response.request, level)

    if settings.API_RESPONSE_BODY_LOGS:
        if kwargs.get('raw'):
            extra['response_raw'] = response
        else:
            extra['response_json'] = response.json()

    message = ('API responded with %(response_status_code)s in %(response_time_in_seconds)s for '
               '%(request_method)s request %(request_url)s')

    logger.log(level, message, extra, extra=extra)

    logger.info(
        '[METRIC][CONSOLE.API_REQUEST.RESPONSE] DURATION:%(response_time_in_seconds)s '
        'STATUS:%(response_status_code)s',
        extra,
        extra=extra
    )

    if response.status_code in [401, 403, 404]:
        # We don't reveal if Resource exists
        raise Http404(_('Resource doesn’t exist'))

    if kwargs.get('raw'):
        return response
    else:
        try:
            json_response = response.json()
            status = json_response.get('status')
            if not status or not status.get('code') or not status.get('info'):
                raise ResponseFormatError('API response is missing missing mandatory properties')
            else:
                return json_response
        except (AttributeError, JSONDecodeError) as error:
            raise ResponseFormatError('API response should be a JSON response')


def to_curl(request, level):
    """Log a CURL command for better debugging"""

    command = "curl --request {method} --header {headers} --data '{data}' '{uri}' {insecure}"

    method = request.method
    uri = request.url
    data = request.body
    headers = ['"{0}: {1}"'.format(k, v) for k, v in request.headers.items()]
    headers = ' --header '.join(headers)
    insecure = '--insecure' if settings.DEBUG else ''

    logger.log(level, command.format(
        method=method,
        headers=headers,
        data=data,
        uri=uri,
        insecure=insecure
    ))
