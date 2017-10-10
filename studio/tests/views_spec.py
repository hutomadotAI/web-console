import factory

from unittest.mock import patch

from django.urls import reverse

from test_plus.test import TestCase

from users.tests.factories import UserFactory
from studio.tests.factories import AiFactory


class TestSummaryView(TestCase):

    def setUp(self):
        """
        Create a user to test response as registered user
        """
        self.user = UserFactory()

    def test_summary_anonymous(self):
        """
        For anonymous user summary should redirect to login
        """
        response = self.client.get(reverse('studio:summary'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            reverse('account_login') + '?next=/summary'
        )

    @patch('studio.views.get_ai_list')
    def test_summary_registred(self, mock_get):
        """
        If user is logged in he can access summary
        """
        self.client.force_login(self.user)

        # We mock ai_list
        mock_get.return_value.json.return_value = []
        response = self.client.get(reverse('studio:summary'))
        self.assertEqual(response.status_code, 200)

    @patch('studio.views.get_ai_list')
    def test_summary_no_ais(self, mock_get):
        """
        If user have no AIs instead of AIs list there should be a training
        video
        """
        self.client.force_login(self.user)

        # We mock ai_list
        mock_get.return_value = []
        response = self.client.get(reverse('studio:summary'))
        self.assertContains(
            response,
            'Welcome to Hu:toma.ai — the marketplace for your bots'
        )
        self.assertContains(
            response,
            'Video Tutorial: Create Your First Bot'
        )
        self.assertNotContains(response, 'Your Bots')

    @patch('studio.views.get_ai_list')
    def test_summary_ais(self, mock_get):
        """
        If user have AIs there should be a list of AIs, as well as there
        shouldn't be the training video
        """
        self.client.force_login(self.user)

        # We mock ai_list
        mock_get.return_value = [
            factory.build(dict, FACTORY_CLASS=AiFactory)
        ]
        response = self.client.get(reverse('studio:summary'))
        self.assertContains(
            response,
            'Welcome to Hu:toma.ai — the marketplace for your bots'
        )
        self.assertNotContains(
            response,
            'Video Tutorial: Create Your First Bot'
        )
        self.assertContains(response, 'Your Bots')

    @patch('studio.views.get_ai_list')
    def test_ai_training_complete(self, mock_get):
        """
        Label should reflect AIs training status
        """
        self.client.force_login(self.user)

        # We mock ai_list
        mock_get.return_value = [
            factory.build(
                dict,
                FACTORY_CLASS=AiFactory,
                ai_status='ai_training_complete'
            )
        ]
        response = self.client.get(reverse('studio:summary'))
        self.assertContains(response, 'Completed')

    @patch('studio.views.get_ai_list')
    def test_ai_undefined(self, mock_get):
        """
        Label should reflect AIs training status
        """
        self.client.force_login(self.user)

        # We mock ai_list
        mock_get.return_value = [
            factory.build(
                dict,
                FACTORY_CLASS=AiFactory,
                ai_status='ai_undefined'
            )
        ]
        response = self.client.get(reverse('studio:summary'))
        self.assertContains(response, 'Not Started')

    @patch('studio.views.get_ai_list')
    def test_ai_training_queued(self, mock_get):
        """
        Label should reflect AIs training status
        """
        self.client.force_login(self.user)

        # We mock ai_list
        mock_get.return_value = [
            factory.build(
                dict,
                FACTORY_CLASS=AiFactory,
                ai_status='ai_training_queued'
            )
        ]
        response = self.client.get(reverse('studio:summary'))
        self.assertContains(response, 'Queued')

    @patch('studio.views.get_ai_list')
    def test_ai_training(self, mock_get):
        """
        Label should reflect AIs training status
        """
        self.client.force_login(self.user)

        # We mock ai_list
        mock_get.return_value = [
            factory.build(
                dict,
                FACTORY_CLASS=AiFactory,
                ai_status='ai_training'
            )
        ]
        response = self.client.get(reverse('studio:summary'))
        self.assertContains(response, 'In Progress')

    @patch('studio.views.get_ai_list')
    def test_ai_training_stopped(self, mock_get):
        """
        Label should reflect AIs training status
        """
        self.client.force_login(self.user)

        # We mock ai_list
        mock_get.return_value = [
            factory.build(
                dict,
                FACTORY_CLASS=AiFactory,
                ai_status='ai_training_stopped'
            )
        ]
        response = self.client.get(reverse('studio:summary'))
        self.assertContains(response, 'Stopped')

    @patch('studio.views.get_ai_list')
    def test_ai_error(self, mock_get):
        """
        Label should reflect AIs training status
        """
        self.client.force_login(self.user)

        # We mock ai_list
        mock_get.return_value = [
            factory.build(
                dict,
                FACTORY_CLASS=AiFactory,
                ai_status='ai_error'
            )
        ]
        response = self.client.get(reverse('studio:summary'))
        self.assertContains(response, 'Error')

    @patch('studio.views.get_ai_list')
    def test_ai_error(self, mock_get):
        """
        Label should reflect AIs training status
        """
        self.client.force_login(self.user)

        # We mock ai_list
        mock_get.return_value = [
            factory.build(
                dict,
                FACTORY_CLASS=AiFactory,
                ai_status='ai_error'
            )
        ]
        response = self.client.get(reverse('studio:summary'))
        self.assertContains(response, 'Error')

    @patch('studio.views.get_ai_list')
    def test_published(self, mock_get):
        """
        A published AI should have a proper button label
        """
        self.client.force_login(self.user)

        # We mock ai_list
        mock_get.return_value = [
            factory.build(
                dict,
                FACTORY_CLASS=AiFactory,
                publishing_state='PUBLISHED'
            )
        ]
        response = self.client.get(reverse('studio:summary'))
        self.assertContains(response, 'Published')

    @patch('studio.views.get_ai_list')
    def test_submitted(self, mock_get):
        """
        A published AI should have a proper button label
        """
        self.client.force_login(self.user)

        # We mock ai_list
        mock_get.return_value = [
            factory.build(
                dict,
                FACTORY_CLASS=AiFactory,
                publishing_state='SUBMITTED'
            )
        ]
        response = self.client.get(reverse('studio:summary'))
        self.assertContains(response, 'Request Sent')

    @patch('studio.views.get_ai_list')
    def test_publish_ready(self, mock_get):
        """
        A trained AI with no linked skills can be published
        """
        self.client.force_login(self.user)

        # We mock ai_list
        mock_get.return_value = [
            factory.build(
                dict,
                FACTORY_CLASS=AiFactory,
                ai_status='ai_training_complete',
                linked_bots=[],
            )
        ]
        response = self.client.get(reverse('studio:summary'))
        self.assertNotContains(
            response,
            'The bot needs to be fully trained before being published.'
        )
        self.assertNotContains(
            response,
            'We do not currently support publishing bots with linked skills. Please remove them if you’d like your bot to be published.'
        )

    @patch('studio.views.get_ai_list')
    def test_publish_linked_bots(self, mock_get):
        """
        A trained AI with linked skills can't be published
        """
        self.client.force_login(self.user)

        # We mock ai_list
        mock_get.return_value = [
            factory.build(
                dict,
                FACTORY_CLASS=AiFactory,
                ai_status='ai_training_complete',
                linked_bots=[
                    1
                ]
            )
        ]

        response = self.client.get(reverse('studio:summary'))
        self.assertContains(
            response,
            'We do not currently support publishing bots with linked skills. Please remove them if you’d like your bot to be published.'
        )

    @patch('studio.views.get_ai_list')
    def test_publish_not_ready(self, mock_get):
        """
        An untrained AI can't be publish
        """
        self.client.force_login(self.user)

        # We mock ai_list
        mock_get.return_value = [
            factory.build(
                dict,
                FACTORY_CLASS=AiFactory,
            )
        ]
        response = self.client.get(reverse('studio:summary'))
        self.assertContains(
            response,
            'The bot needs to be fully trained before being published.'
        )


class TestAICreateView(TestCase):
    def setUp(self):
        """
        Create a user to test response as registered user
        """
        self.user = UserFactory()

    def test_summary_anonymous(self):
        """
        Anonymous can't access create view
        """
        response = self.client.get(reverse('studio:add_bot'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            reverse('account_login') + '?next=/bots/add'
        )

    def test_summary_registred(self):
        """
        Logged-in users can access create view
        """
        self.client.force_login(self.user)

        # We mock ai_list
        response = self.client.get(reverse('studio:add_bot'))
        self.assertEqual(response.status_code, 200)
