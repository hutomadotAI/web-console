"""Extend createsuperuser so that we can use it in automated way
Inspired by https://stackoverflow.com/a/42491469/694641 and
https://stackoverflow.com/q/39744593/694641"""
import logging
import os

from django.contrib.auth.management.commands import createsuperuser
from django.core.management import CommandError
from django.contrib.auth.models import User


logger = logging.getLogger(__name__)

class Command(createsuperuser.Command):
    help = 'Create a superuser, and read the password from environment'

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument(
            '--password', dest='password', default=None,
            help='Specifies the password for the superuser.',
        )

    def handle(self, *args, **options):
        username = options.get('username')
        database = options.get('database')
        password = os.environ.get('DJANGO_SU_PASSWORD', 'superuser')

        if password and not username:
            raise CommandError("--username is required as we are auto-setting password")

        if User.objects.filter(username=username).exists():
            logger.info("superuser %s exists, skipping creation", username)
            return
        logger.info(
            "CreateSuperUserCommand - creating user %s with password as read from environment DJANGO_SU_PASSWORD",
            username)

        super(Command, self).handle(*args, **options)

        if password:
            user = self.UserModel._default_manager.db_manager(database).get(username=username)
            user.set_password(password)
            user.save()
