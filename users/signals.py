import logging

from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.db.models.signals import post_save
from django.dispatch import receiver

from users.models import Users

logger = logging.getLogger('users')


@receiver(user_logged_in)
def user_logged_in(sender, user, request, **kwargs):
    """
    User performed a loggin
    """
    if user:

        logger.info(
            'User {0} has logged in'.format(user)
        )


@receiver(user_logged_out)
def user_logged_out(sender, user, request, **kwargs):
    """
    User performed a logout
    """
    if user:

        logger.info(
            'User {0} has logged out'.format(user)
        )


@receiver(post_save, sender=User)
def update_legacy_tables(sender, instance, created, **kwargs):
    """
    Updates legacy `user` and `user_info` tables.
    """
    if created:

        user, created = Users.objects.update_or_create(
            email=instance.email,
            defaults={
                'user': instance
            }
        )

        logger.warning(
            '{0} has been {1}'.format(
                user,
                'created' if created else 'updated'
            )
        )
