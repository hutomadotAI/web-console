import logging

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from users.models import Profile
from users.services import get_user_token, post_user

logger = logging.getLogger(__name__)


@receiver(user_logged_in)
def user_logged_in(sender, user, request, **kwargs):
    """User performed a login, get a token and save it for this session"""

    profile = Profile.objects.get(user=user)

    api_user = get_user_token(
        settings.API_ADMIN_TOKEN,
        profile.dev_id
    )

    request.session['token'] = api_user['dev_token']
    request.session['dev_id'] = profile.dev_id

    logger.info('User {0} has logged in'.format(user))


@receiver(user_logged_out)
def user_logged_out(sender, user, request, **kwargs):
    """User performed a logout"""

    logger.info('User {0} has logged out'.format(user))


@receiver(pre_save, sender=User)
def create_API_user(sender, instance, *args, **kwargs):
    """Try to create a API user do it only on creation time"""

    if instance.pk is None:
        instance.api_user = post_user(
            settings.API_ADMIN_TOKEN,
            instance
        )

        logger.info('create_API_user for %s' % instance.email)


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """Create a profile for a user"""

    if created:
        Profile.objects.create(
            user=instance,
            dev_id=instance.api_user['devid']
        )

        logger.info('Create profile for %s' % instance.email)
