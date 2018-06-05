import factory

from unittest.mock import patch

from django.urls import reverse
from django.contrib.auth.signals import user_logged_in

from test_plus.test import TestCase

from studio.tests.factories import AiFactory

from users.models import Profile
from users.tests.factories import UserFactory


class TestPublishView(TestCase):

    @factory.django.mute_signals(user_logged_in)
    def setUp(self):
        """Create a user to test response as registered user"""

        self.user = UserFactory()
        Profile.objects.create(user=self.user)

        self.client.force_login(self.user)
        session = self.client.session
        session['token'] = 'token'
        session['dev_id'] = 'dev_id'
        session.save()

    def test_publish_anonymous(self):
        """For anonymous user publish should redirect to login"""

        self.client.logout()

        ai = factory.build(dict, FACTORY_CLASS=AiFactory)
        response = self.client.get(reverse(
            'botstore:publish',
            kwargs={'aiid': ai['aiid']}
        ))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            reverse('account_login') + '?next=/botstore/publish/{aiid}'.format(
                aiid=ai['aiid']
            )
        )

    @patch('users.decorators.get_info')
    def test_publish_no_info(self, mock_get_info):
        """For user without dev info redirect to dev info"""

        ai = factory.build(dict, FACTORY_CLASS=AiFactory)

        mock_get_info.return_value.json.return_value = {
            'status': {
                'code': 404
            }
        }

        response = self.client.get(reverse(
            'botstore:publish',
            kwargs={'aiid': ai['aiid']}
        ))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            reverse('users:info') + '?next=/botstore/publish/{aiid}'.format(
                aiid=ai['aiid']
            )
        )

    @patch('botstore.views.get_ai')
    @patch('botstore.views.get_info')
    @patch('users.decorators.get_info')
    def test_publish_has_info(self, mock_get_info, mock_get_info_2, mock_get_ai):
        """For user with dev info show publish form"""

        ai = factory.build(dict, FACTORY_CLASS=AiFactory)

        mock_get_info.return_value = {'status': {'code': 200}}

        mock_get_ai.return_value.json.return_value = [
            factory.build(dict, FACTORY_CLASS=AiFactory)
        ]

        response = self.client.get(reverse(
            'botstore:publish',
            kwargs={'aiid': ai['aiid']}
        ))

        self.assertEqual(response.status_code, 200)
