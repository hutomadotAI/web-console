import logging

from django.http import JsonResponse

logger = logging.getLogger(__name__)


def json_login_required(function):
    """Authentication decorator for JSON requests"""

    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated:
            return function(request, *args, **kwargs)
        else:
            return JsonResponse(
                {'message': 'Requires authentication'}, status=401
            )

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap
