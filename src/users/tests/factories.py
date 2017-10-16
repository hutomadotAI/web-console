import factory

from django.contrib.auth.models import AnonymousUser, User
from django.db.models.signals import pre_save, post_save
from django.contrib.auth.signals import user_logged_in, user_logged_out

from users.models import Profile
from users.signals import create_API_user, create_profile


class AnonymousUserFactory(factory.Factory):
    """
    Simple factory for Anonymous users
    """
    class Meta:
        model = AnonymousUser


class ProfileFactory(factory.Factory):
    """
    Create an Profile instance
    """
    class Meta:
        model = Profile

    user = None


@factory.django.mute_signals(pre_save, post_save)
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
        factory=ProfileFactory,
        factory_related_name='user'
    )
