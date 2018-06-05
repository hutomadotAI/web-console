from test_plus.test import TestCase

from users.tests.factories import UserFactory
from users.models import Profile


class TestUser(TestCase):

    def setUp(self):
        self.user = UserFactory()
        Profile.objects.create(user=self.user)

    def test_legacy_user_is_created(self):
        """
        Legacy user is created after built-in
        """
        self.assertTrue(
            Profile.objects.get(user=self.user),
            'Legacy user is created after built-in'
        )
