import logging
from hashlib import blake2b

from allauth.account.signals import password_changed, password_reset

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.signals import (
    user_logged_in,
    user_logged_out,
    user_login_failed
)
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

    logger.info('User {dev_id} has logged in'.format(
        dev_id=user.profile.dev_id
    ))


@receiver(user_logged_out)
def user_logged_out(sender, user, request, **kwargs):
    """
    User performed a logout, we test for user as test client.logout() is
    sending NoneType instead
    """

    if user:
        logger.info('User {dev_id} has logged out'.format(
            dev_id=user.profile.dev_id
        ))


@receiver(user_login_failed)
def user_login_failed(sender, credentials, request, **kwargs):
    """User failed to log in"""

    logger.info('User {hash} has failed to log in'.format(
        hash=blake2b(
            credentials['email'].encode('utf-8'),
            digest_size=4,
            key=settings.SECRET_KEY
        ).hexdigest()
    ))


@receiver(password_changed)
def password_changed(sender, user, request, **kwargs):
    """User changed password"""

    logger.info('User {dev_id} has changed password'.format(
        dev_id=user.profile.dev_id
    ))


@receiver(password_reset)
def password_reset(sender, user, request, **kwargs):
    """User reset password"""

    logger.info('User {dev_id} has reset password'.format(
        dev_id=user.profile.dev_id
    ))


@receiver(pre_save, sender=User)
def create_API_user(sender, instance, *args, **kwargs):
    """Try to create a API user do it only on creation time"""

    if instance.pk is None:
        instance.api_user = post_user(settings.API_ADMIN_TOKEN)

        logger.info('create_API_user for {dev_id}'.format(
            dev_id=instance.api_user['devid']
        ))


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """Create a profile for a user"""

    if created:
        Profile.objects.create(
            user=instance,
            dev_id=instance.api_user['devid']
        )

        logger.info('Create profile for {dev_id}'.format(
            dev_id=instance.api_user['devid']
        ))
