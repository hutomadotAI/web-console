import logging
import requests
import urllib

from django.contrib.auth.models import AnonymousUser, User

from django.conf import settings

from app.services import set_headers

logger = logging.getLogger(__name__)


