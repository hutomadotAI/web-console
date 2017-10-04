from datetime import datetime, timedelta
import jwt
import logging
import uuid

from django.conf import settings
from django.db import models
from django.contrib.auth.models import User

logger = logging.getLogger(__name__)


class Users(models.Model):
    """
    connector model to not break db structure, Django application is using
    built-in User model, legacy users are moved in a migration. New instance
    is created after registration.

    user — Relation between legacy and built-in model
    plan_id — Users plan default to Free
    dev_id — Users UUID, use `CharField` instead of built-in UUID to keep
            dashed UUID string.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
    )
    plan_id = models.IntegerField(default=1)
    dev_id = models.CharField(
        default=uuid.uuid4,
        editable=False,
        max_length=50,
        unique=True
    )

    # To be moved
    dev_token = models.CharField(max_length=250)

    # To be dropped
    username = models.CharField(blank=True, max_length=50, null=True)
    email = models.CharField(blank=True, max_length=100, null=True)
    password = models.CharField(blank=True, max_length=64, null=True)
    password_salt = models.CharField(blank=True, max_length=250, null=True)
    first_name = models.CharField(blank=True, max_length=30, null=True)
    created = models.DateTimeField(blank=True, null=True)
    attempt = models.CharField(blank=True, max_length=15, null=True)
    last_name = models.CharField(blank=True, max_length=30, null=True)
    valid = models.IntegerField(blank=True, null=True)
    internal = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'users'

    def __str__(self):
        """
        Returns a string representation of this `Users`.

        This string is used when a `Users` object is printed in the console.
        """
        return 'Users (legacy): %s' % (self.username)

    @property
    def token(self):
        """
        Allows us to get a user's token by calling `user.token` instead of
        `user.generate_jwt_token().

        The `@property` decorator above makes this possible. `token` is called
        a “dynamic property”.
        """
        return self._generate_jwt_token()

    def _generate_jwt_token(self):
        """
        Generates a JSON Web Token that stores this user's ID and has an expiry
        date set to 60 days into the future.
        """

        dt = datetime.now() + settings.JWT_EXPIRATION_DELTA

        token = jwt.encode({
            'sub':  str(self.dev_id),
            'ROLE': 'ROLE_FREE',
            'exp': int(dt.strftime('%s'))
        }, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

        return token.decode('utf-8')
