import logging
import uuid

from django.db import models
from django.contrib.auth.models import User

logger = logging.getLogger(__name__)


class Profile(models.Model):
    """
    connector model to not break db structure, Django application is using
    built-in User model, legacy users are moved in a migration. New instance
    is created after registration.

    user — Relation between legacy and built-in model
    dev_id — Users UUID, use `CharField` instead of built-in UUID to keep
            dashed UUID string.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
    )
    dev_id = models.CharField(
        default=uuid.uuid4,
        max_length=36,
        unique=True
    )

    def __str__(self):
        """
        Returns a string representation of this `Users`.

        This string is used when a `Users` object is printed in the console.
        """
        return 'Profile: %s' % (self.dev_id)
