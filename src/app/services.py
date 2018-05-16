import logging
from requests import Request, Session, packages
from constance import config

from django.conf import settings
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from redis.exceptions import ResponseError, ConnectionError

from django.http import Http404
from django.utils.translation import ugettext_lazy as _

logger = logging.getLogger(__name__)
packages.urllib3.disable_warnings(InsecureRequestWarning)

try:
    TIMEOUT = config.API_DEFAULT_TIMEOUT
except (ConnectionError, ResponseError) as e:
    logger.warning('Django constance failed to use Redis, falling back to Settings')
    TIMEOUT = settings.API_DEFAULT_TIMEOUT

VERIFY = not settings.DEBUG


def set_headers(token):
    """Add required Authentication headers"""

    headers = {
        'Authorization': 'Bearer {token}'.format(token=token)
    } if token else {}
    return headers


def fetch_api(path, token, method='GET', data={}, json={}, files={}, headers={}, params={}, timeout=TIMEOUT, verify=VERIFY, **kwargs):

    url = settings.API_URL + path.format(**kwargs)
    headers = {**headers, **set_headers(token)}

    session = Session()
    request = Request(
        method, url, data=data, json=json, files=files, headers=headers, params=params
    )
    response = session.send(request.prepare(), timeout=timeout, verify=verify)

    to_curl(response.request)
    logger.debug(response)

    if response.status_code in [401, 403, 404]:
        # We don't reveal if Resource exists
        raise Http404(_('Resource doesn’t exist'))

    if kwargs.get('raw'):
        return response
    else:
        return response.json()


def to_curl(request):
    """Log a CURL command for better debuging"""

    command = "curl --request {method} --header {headers} --data '{data}' '{uri}' {insecure}"

    method = request.method
    uri = request.url
    data = request.body
    headers = ['"{0}: {1}"'.format(k, v) for k, v in request.headers.items()]
    headers = ' --header '.join(headers)
    insecure = '--insecure' if settings.DEBUG else ''

    logger.debug(command.format(
        method=method,
        headers=headers,
        data=data,
        uri=uri,
        insecure=insecure
    ))
