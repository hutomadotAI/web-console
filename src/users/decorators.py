import logging

from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from users.services import get_info

logger = logging.getLogger(__name__)


def has_info(function):
    """Check if user has a developer info"""

    def wrap(request, *args, **kwargs):
        info = get_info(request.session['token'], request.session['dev_id'])

        if info['status']['code'] == 200:
            return function(request, *args, **kwargs)
        else:
            messages.warning(request, _('This is your first bot. Before publishing this to our store we need to collect some developer details.'))
            return HttpResponseRedirect(
                '%s?next=%s' % (reverse('users:info'), request.path_info)
            )

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap
