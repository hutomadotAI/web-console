import factory

from django.contrib.auth.models import AnonymousUser, User
from django.db.models.signals import post_save

from users.models import Users
from users.signals import update_legacy_tables


class AnonymousUserFactory(factory.Factory):
    """
    Simple factory for Anonymous users
    """
    class Meta:
        model = AnonymousUser


class UsersFactory(factory.Factory):
    """
    Create an Legacy Users user instance
    """
    class Meta:
        model = Users

    email = factory.Sequence(lambda n: 'user_%s@hutoma.ai' % n)
    username = factory.Sequence(lambda n: 'user_%s' % n)
    user = None


class UserFactory(factory.django.DjangoModelFactory):
    """
    Create an Django built-in user, relays on signals to create legacy Users
    related instance.
    """
    class Meta:
        model = User

    email = factory.Sequence(lambda n: 'user_%s@hutoma.ai' % n)
    username = factory.Sequence(lambda n: 'user_%s' % n)

    users = factory.RelatedFactory(
        factory=UsersFactory,
        factory_related_name='user',
        username=factory.SelfAttribute('..username'),
        email=factory.SelfAttribute('..email'),
    )
