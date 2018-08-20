from django.conf import settings


def tag_manager(request):
    """Add Google tag manager Environment to all the templates"""

    return {
        'tag_manager_id': settings.TAG_MANAGER_ID,
        'tag_manager_environment': settings.TAG_MANAGER_ENVIRONMENT,
    }


def stackdriver_errors_js(request):
    """Add stackdriver errors js configuration variables"""

    return {
        'CONSOLE_SERVICE': settings.CONSOLE_SERVICE,
        'CONSOLE_VERSION': settings.CONSOLE_VERSION,
        'GCP_PROJECT_ID': settings.GCP_PROJECT_ID,
        'STACKDRIVER_ERRORS_JS_KEY': settings.STACKDRIVER_ERRORS_JS_KEY
    }
