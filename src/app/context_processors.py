from django.conf import settings


def tag_manager(request):
    """Add Google tag manager Environment to all the templates"""

    return {
        'tag_manager_id': settings.TAG_MANAGER_ID,
        'tag_manager_environment': settings.TAG_MANAGER_ENVIRONMENT,
    }
