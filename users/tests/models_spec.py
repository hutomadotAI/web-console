from test_plus.test import TestCase

from users.tests.factories import UserFactory
from users.models import Users


class TestUser(TestCase):

    def setUp(self):
        self.user = UserFactory()

    def test_legacy_user_is_created(self):
        """
        Legacy user is created after built-in
        """
        self.assertTrue(
            Users.objects.get(user=self.user),
            'Legacy user is created after built-in'
        )
