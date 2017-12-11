"""A command that will migrate users from legacy user table """
import logging
import os

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from allauth.account.models import EmailAddress
from allauth.utils import generate_unique_username

from django.db.models.signals import post_save, pre_save

from users.hashers import PBKDF2WrappedSHA256PasswordHasher
from users.models import Profile
from legacy.models import Users
from users.signals import create_API_user, create_profile

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'A command that will migrate users from legacy user table'

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)

    def handle(self, *args, **options):
        logger.info("Migrating legacy users from old DB")

        hasher = PBKDF2WrappedSHA256PasswordHasher()

        for legacy_user in Users.objects.all():

            logger.info(legacy_user)

            # Disable pre_save and post_save signal
            pre_save.disconnect(
                create_API_user,
                sender=User
            )

            post_save.disconnect(
                create_profile,
                sender=User
            )

            # Update password if not a new user from Django, whom doesn't
            # have password_salt
            if legacy_user.password_salt:
                legacy_user.password = hasher.encode_sha256_hash(
                    legacy_user.password,
                    legacy_user.password_salt
                )

                logger.info(legacy_user.password)

            # Create if doesn't exist, we match by email
            new_user, created = User.objects.get_or_create(
                email=legacy_user.email,
                defaults={
                    'password': legacy_user.password,
                    'is_superuser': legacy_user.internal,
                    'username': generate_unique_username([
                        legacy_user.first_name,
                        legacy_user.last_name,
                        legacy_user.email
                    ]),
                    'first_name': legacy_user.first_name,
                    'last_name': legacy_user.last_name,
                    'email': legacy_user.email,
                    'is_staff': legacy_user.internal,
                    'is_active': legacy_user.valid,
                    'date_joined': legacy_user.created,
                }
            )

            if created:
                # Create an Email entry for each user, if it's an internal one
                # automatically verify the email
                EmailAddress.objects.create(
                    email=legacy_user.email,
                    primary=True,
                    verified=new_user.is_staff,
                    user=new_user
                )

                # Create an Profile entry with corresponding dev_id
                Profile.objects.create(
                    user=new_user,
                    dev_id=legacy_user.dev_id
                )

            logger.info(
                '{0} is {1}'.format(
                    new_user,
                    'new' if created else 'existing'
                )
            )

            # Enable back pre_save and post_save signal
            pre_save.connect(
                create_API_user,
                sender=User
            )

            post_save.connect(
                create_profile,
                sender=User
            )
