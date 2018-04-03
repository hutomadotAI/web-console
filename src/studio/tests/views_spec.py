import factory

from unittest.mock import patch

from django.urls import reverse
from django.contrib.auth.signals import user_logged_in

from test_plus.test import TestCase

from studio.tests.factories import AiFactory, AIDetails

from users.models import Profile
from users.tests.factories import UserFactory


class TestSummaryView(TestCase):

    @factory.django.mute_signals(user_logged_in)
    def setUp(self):
        """Create a user to test response as registered user"""

        self.user = UserFactory()
        Profile.objects.create(user=self.user)

        self.client.force_login(self.user)
        session = self.client.session
        session['token'] = 'token'
        session.save()

    def test_summary_anonymous(self):
        """For anonymous user summary should redirect to login"""

        self.client.logout()
        response = self.client.get(reverse('studio:summary'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            reverse('account_login') + '?next=/summary'
        )

    @patch('studio.views.get_ai_list')
    def test_summary_registred(self, mock_get):
        """If user is logged in he can access summary"""

        # We mock ai_list
        mock_get.return_value = {'ai_list': []}
        response = self.client.get(reverse('studio:summary'))
        self.assertEqual(response.status_code, 200)

    @patch('studio.views.get_ai_list')
    def test_summary_no_ais(self, mock_get):
        """
        If user have no AIs instead of AIs list there should be a training
        video
        """

        # We mock ai_list
        mock_get.return_value = {'ai_list': []}
        response = self.client.get(reverse('studio:summary'))
        self.assertContains(
            response,
            'Welcome to Hu:toma AI - make your knowledge conversational'
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

        # We mock ai_list
        mock_get.return_value = {
            'ai_list': [
                factory.build(dict, FACTORY_CLASS=AiFactory)
            ]
        }

        response = self.client.get(reverse('studio:summary'))
        self.assertContains(
            response,
            'Welcome to Hu:toma AI - make your knowledge conversational'
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

        # We mock ai_list
        mock_get.return_value = {
            'ai_list': [
                factory.build(
                    dict,
                    FACTORY_CLASS=AiFactory,
                    ai_status='ai_training_complete'
                )
            ]
        }
        response = self.client.get(reverse('studio:summary'))
        self.assertContains(response, 'Completed')

    @patch('studio.views.get_ai_list')
    def test_ai_undefined(self, mock_get):
        """
        Label should reflect AIs training status
        """

        # We mock ai_list
        mock_get.return_value = {
            'ai_list': [
                factory.build(
                    dict,
                    FACTORY_CLASS=AiFactory,
                    ai_status='ai_undefined'
                )
            ]
        }
        response = self.client.get(reverse('studio:summary'))
        self.assertContains(response, 'Not Started')

    @patch('studio.views.get_ai_list')
    def test_ai_training_queued(self, mock_get):
        """
        Label should reflect AIs training status
        """

        # We mock ai_list
        mock_get.return_value = {
            'ai_list': [
                factory.build(
                    dict,
                    FACTORY_CLASS=AiFactory,
                    ai_status='ai_training_queued'
                )
            ]
        }
        response = self.client.get(reverse('studio:summary'))
        self.assertContains(response, 'Queued')

    @patch('studio.views.get_ai_list')
    def test_ai_training(self, mock_get):
        """
        Label should reflect AIs training status
        """

        # We mock ai_list
        mock_get.return_value = {
            'ai_list': [
                factory.build(
                    dict,
                    FACTORY_CLASS=AiFactory,
                    ai_status='ai_training'
                )
            ]
        }
        response = self.client.get(reverse('studio:summary'))
        self.assertContains(response, 'In Progress')

    @patch('studio.views.get_ai_list')
    def test_ai_training_stopped(self, mock_get):
        """
        Label should reflect AIs training status
        """

        # We mock ai_list
        mock_get.return_value = {
            'ai_list': [
                factory.build(
                    dict,
                    FACTORY_CLASS=AiFactory,
                    ai_status='ai_training_stopped'
                )
            ]
        }
        response = self.client.get(reverse('studio:summary'))
        self.assertContains(response, 'Stopped')

    @patch('studio.views.get_ai_list')
    def test_ai_error(self, mock_get):
        """Label should reflect AIs training status"""

        # We mock ai_list
        mock_get.return_value = {
            'ai_list': [
                factory.build(
                    dict,
                    FACTORY_CLASS=AiFactory,
                    ai_status='ai_error'
                )
            ]
        }
        response = self.client.get(reverse('studio:summary'))
        self.assertContains(response, 'Error')

    @patch('studio.views.get_ai_list')
    def test_ai_error(self, mock_get):
        """
        Label should reflect AIs training status
        """

        # We mock ai_list
        mock_get.return_value = {
            'ai_list': [
                factory.build(
                    dict,
                    FACTORY_CLASS=AiFactory,
                    ai_status='ai_error'
                )
            ]
        }
        response = self.client.get(reverse('studio:summary'))
        self.assertContains(response, 'Error')

    @patch('studio.views.get_ai_list')
    def test_published(self, mock_get):
        """
        A published AI should have a proper button label
        """

        # We mock ai_list
        mock_get.return_value = {
            'ai_list': [
                factory.build(
                    dict,
                    FACTORY_CLASS=AiFactory,
                    publishing_state='PUBLISHED'
                )
            ]
        }
        response = self.client.get(reverse('studio:summary'))
        self.assertContains(response, 'Published')

    @patch('studio.views.get_ai_list')
    def test_submitted(self, mock_get):
        """
        A published AI should have a proper button label
        """

        # We mock ai_list
        mock_get.return_value = {
            'ai_list': [
                factory.build(
                    dict,
                    FACTORY_CLASS=AiFactory,
                    publishing_state='SUBMITTED'
                )
            ]
        }
        response = self.client.get(reverse('studio:summary'))
        self.assertContains(response, 'Request Sent')

    @patch('studio.views.get_ai_list')
    def test_publish_ready(self, mock_get):
        """
        A trained AI with no linked skills can be published
        """

        # We mock ai_list
        mock_get.return_value = {
            'ai_list': [
                factory.build(
                    dict,
                    FACTORY_CLASS=AiFactory,
                    ai_status='ai_training_complete',
                    linked_bots=[],
                )
            ]
        }
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

        # We mock ai_list
        mock_get.return_value = {
            'ai_list': [
                factory.build(
                    dict,
                    FACTORY_CLASS=AiFactory,
                    ai_status='ai_training_complete',
                    linked_bots=[
                        1
                    ]
                )
            ]
        }

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

        # We mock ai_list
        mock_get.return_value = {
            'ai_list': [
                factory.build(
                    dict,
                    FACTORY_CLASS=AiFactory,
                )
            ]
        }
        response = self.client.get(reverse('studio:summary'))
        self.assertContains(
            response,
            'The bot needs to be fully trained before being published.'
        )


class TestAICreateView(TestCase):

    @factory.django.mute_signals(user_logged_in)
    def setUp(self):
        """Create a user to test response as registered user"""

        self.user = UserFactory()
        Profile.objects.create(user=self.user)

        self.client.force_login(self.user)
        session = self.client.session
        session['token'] = 'token'
        session.save()

    def test_ai_create_anonymous(self):
        """Anonymous can't access create view"""

        self.client.logout()
        response = self.client.get(reverse('studio:add_bot'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            reverse('account_login') + '?next=/bots/add'
        )

    def test_ai_create_registred(self):
        """Logged-in users can access create view"""

        # We mock ai_list
        response = self.client.get(reverse('studio:add_bot'))
        self.assertEqual(response.status_code, 200)


class TestTrainingView(TestCase):
    @factory.django.mute_signals(user_logged_in)
    def setUp(self):
        """Create a user to test response as registered user"""

        self.user = UserFactory()
        self.ai = factory.build(dict, FACTORY_CLASS=AiFactory)
        self.ai_details = factory.build(dict, FACTORY_CLASS=AIDetails)
        Profile.objects.create(user=self.user)

        self.client.force_login(self.user)
        session = self.client.session
        session['token'] = 'token'
        session.save()

    def test_anonymous(self):
        """Anonymous can't access update training"""

        self.client.logout()
        response = self.client.get(reverse(
            'studio:training',
            kwargs={'aiid': self.ai['aiid']}
        ))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            reverse('account_login') + '?next=/bots/edit/%s/training' % self.ai['aiid']
        )

    @patch('botstore.templatetags.botstore_tags.get_categories')
    @patch('studio.views.get_ai')
    @patch('studio.views.get_ai_training')
    @patch('studio.views.get_ai_details')
    def test_registred(
        self, mock_get_ai_details, mock_get_ai_training, mock_get_ai, mock_get_categories
    ):

        mock_get_ai.return_value = self.ai
        mock_get_categories.return_value = []
        mock_get_ai_training.return_value = {}
        mock_get_ai_details.return_value = self.ai_details

        response = self.client.get(reverse(
            'studio:training',
            kwargs={
                'aiid': self.ai['aiid']
            }
        ))
        self.assertEqual(response.status_code, 200)

    @patch('botstore.templatetags.botstore_tags.get_categories')
    @patch('studio.views.get_ai')
    @patch('studio.views.get_ai_training')
    @patch('studio.views.get_ai_details')
    def test_help_message(
        self, mock_get_ai_details, mock_get_ai_training, mock_get_ai, mock_get_categories
    ):

        mock_get_ai.return_value = self.ai
        mock_get_categories.return_value = []
        mock_get_ai_training.return_value = {}
        mock_get_ai_details.return_value = self.ai_details

        response = self.client.get(reverse(
            'studio:training',
            kwargs={
                'aiid': self.ai['aiid']
            }
        ))

        self.assertContains(response, 'Check <a data-toggle="modal" data-target="#sampleTrainingFile">training file example</a> or watch our <a data-toggle="modal" data-target="#TRAINING_VIDEO_TUTORIAL">training video tutorial</a>')


class TestEntitiesView(TestCase):
    @factory.django.mute_signals(user_logged_in)
    def setUp(self):
        """Create a user to test response as registered user"""

        self.user = UserFactory()
        self.ai = factory.build(dict, FACTORY_CLASS=AiFactory)
        self.ai_details = factory.build(dict, FACTORY_CLASS=AIDetails)
        Profile.objects.create(user=self.user)

        self.client.force_login(self.user)
        session = self.client.session
        session['token'] = 'token'
        session.save()

    def test_anonymous(self):
        """Anonymous can't access update enities"""

        self.client.logout()
        response = self.client.get(reverse(
            'studio:entities',
            kwargs={'aiid': self.ai['aiid']}
        ))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            reverse('account_login') + '?next=/bots/edit/%s/entities' % self.ai['aiid']
        )

    @patch('botstore.templatetags.botstore_tags.get_categories')
    @patch('studio.views.get_entities_list')
    @patch('studio.views.get_ai')
    @patch('studio.views.get_ai_details')
    def test_registred(
        self, mock_get_ai_details, mock_get_ai, mock_get_entities_list, mock_get_categories
    ):

        mock_get_ai.return_value = self.ai
        mock_get_ai_details.return_value = self.ai_details
        mock_get_entities_list.return_value.json.return_value = []
        mock_get_categories.return_value = []

        response = self.client.get(reverse(
            'studio:entities',
            kwargs={'aiid': self.ai['aiid']}
        ))
        self.assertEqual(response.status_code, 200)


class TestAIDetailView(TestCase):

    @factory.django.mute_signals(user_logged_in)
    def setUp(self):
        """Create a user to test response as registered user"""

        self.user = UserFactory()
        self.ai = factory.build(dict, FACTORY_CLASS=AiFactory)
        self.ai_details = factory.build(dict, FACTORY_CLASS=AIDetails)
        Profile.objects.create(user=self.user)

        self.client.force_login(self.user)
        session = self.client.session
        session['token'] = 'token'
        session.save()

    def test_anonymous(self):
        """Anonymous can't access bot summary"""

        self.client.logout()
        response = self.client.get(reverse(
            'studio:edit_bot',
            kwargs={'aiid': self.ai['aiid']}
        ))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            reverse('account_login') + '?next=/bots/edit/%s' % self.ai['aiid']
        )

    @patch('botstore.templatetags.botstore_tags.get_categories')
    @patch('studio.views.get_ai')
    @patch('studio.views.get_ai_details')
    def test_registred(
        self, mock_get_ai_details, mock_get_ai, mock_get_categories
    ):
        """Should pass and show bot summary page"""

        mock_get_ai.return_value = self.ai
        mock_get_ai_details.return_value = self.ai_details
        mock_get_categories.return_value = []

        response = self.client.get(reverse(
            'studio:edit_bot',
            kwargs={'aiid': self.ai['aiid']}
        ))

        self.assertEqual(response.status_code, 200)

    @patch('botstore.templatetags.botstore_tags.get_categories')
    @patch('studio.views.get_ai')
    @patch('studio.views.get_ai_details')
    def test_is_chatable(
        self, mock_get_ai_details, mock_get_ai, mock_get_categories
    ):
        """Should pass empty bot isn't chatable"""

        mock_get_ai.return_value = self.ai
        mock_get_ai_details.return_value = self.ai_details
        mock_get_categories.return_value = []

        response = self.client.get(reverse(
            'studio:edit_bot',
            kwargs={'aiid': self.ai['aiid']}
        ))

        self.assertNotContains(response, 'chatable')
        self.assertContains(response, 'To start chatting with your bot either upload a training file, add a skill, or add an intent')

    @patch('botstore.templatetags.botstore_tags.get_categories')
    @patch('studio.views.get_ai')
    @patch('studio.views.get_ai_details')
    def test_new_bot(
        self, mock_get_ai_details, mock_get_ai, mock_get_categories
    ):
        """Should pass and show a info messages"""

        mock_get_ai.return_value = self.ai
        mock_get_ai_details.return_value = self.ai_details
        mock_get_categories.return_value = []

        response = self.client.get(reverse(
            'studio:edit_bot',
            kwargs={'aiid': self.ai['aiid']}
        ))

        self.assertContains(response, 'Simply upload historical conversations or conversation samples between your users.')
        self.assertContains(response, 'An Intent is a way to flag completion of a specific task during a conversation.')
        self.assertContains(response, 'Think of bot skills as Lego pieces that you can mix and match together to build your own AI.')

    @patch('botstore.templatetags.botstore_tags.get_categories')
    @patch('studio.views.get_ai')
    @patch('studio.views.get_ai_details')
    def test_with_training_file(
        self, mock_get_ai_details, mock_get_ai, mock_get_categories
    ):
        """
        Should pass and show content of the training file and no info messages
        """

        mock_get_ai.return_value = self.ai
        mock_get_ai_details.return_value = self.ai_details
        mock_get_categories.return_value = []

        mock_get_ai_details.return_value['training_file'] = 'This is my training file'

        response = self.client.get(reverse(
            'studio:edit_bot',
            kwargs={'aiid': self.ai['aiid']}
        ))

        self.assertContains(response, 'This is my training file')
        self.assertNotContains(response, 'Simply upload historical conversations or conversation samples between your users.')

    @patch('botstore.templatetags.botstore_tags.get_categories')
    @patch('studio.views.get_ai')
    @patch('studio.views.get_ai_details')
    def test_intents(
        self, mock_get_ai_details, mock_get_ai, mock_get_categories
    ):
        """Should pass and show intents list and no info messages"""

        mock_get_ai.return_value = self.ai
        mock_get_ai_details.return_value = self.ai_details
        mock_get_categories.return_value = []

        mock_get_ai_details.return_value['intents'] = [
            'intent_1', 'intent_2', 'intent_3', 'intent_4', 'intent_5', 'intent_6'
        ]

        response = self.client.get(reverse(
            'studio:edit_bot',
            kwargs={'aiid': self.ai['aiid']}
        ))

        self.assertContains(response, 'intent_1')
        self.assertContains(response, 'intent_2')
        self.assertContains(response, 'intent_3')
        self.assertContains(response, 'intent_4')
        self.assertContains(response, 'intent_5')
        self.assertNotContains(response, 'intent_6')
        self.assertNotContains(response, 'An Intent is a way to flag completion of a specific task during a conversation.')

    @patch('botstore.templatetags.botstore_tags.get_categories')
    @patch('studio.views.get_ai')
    @patch('studio.views.get_ai_details')
    def test_skills(
        self, mock_get_ai_details, mock_get_ai, mock_get_categories
    ):
        """Should pass and show skills list"""

        mock_get_ai.return_value = self.ai
        mock_get_ai_details.return_value = self.ai_details
        mock_get_categories.return_value = []

        mock_get_ai_details.return_value['skills'] = [
            {'name': 'bot 1'},
            {'name': 'bot 2'},
            {'name': 'bot 3'},
            {'name': 'bot 4'},
            {'name': 'bot 5'},
            {'name': 'bot 6'},
        ]

        response = self.client.get(reverse(
            'studio:edit_bot',
            kwargs={'aiid': self.ai['aiid']}
        ))

        self.assertContains(response, 'bot 1')
        self.assertContains(response, 'bot 2')
        self.assertContains(response, 'bot 3')
        self.assertContains(response, 'bot 4')
        self.assertContains(response, 'bot 5')
        self.assertNotContains(response, 'bot 6')
        self.assertNotContains(response, 'Think of bot skills as Lego pieces that you can mix and match together to build your own AI.')


class TestAIUpdateView(TestCase):
    @factory.django.mute_signals(user_logged_in)
    def setUp(self):
        """Create a user to test response as registered user"""

        self.user = UserFactory()
        self.ai = factory.build(dict, FACTORY_CLASS=AiFactory)
        self.ai_details = factory.build(dict, FACTORY_CLASS=AIDetails)
        Profile.objects.create(user=self.user)

        self.client.force_login(self.user)
        session = self.client.session
        session['token'] = 'token'
        session.save()

    def test_anonymous(self):
        """Anonymous can't access update settings"""

        self.client.logout()
        response = self.client.get(reverse(
            'studio:settings',
            kwargs={'aiid': self.ai['aiid']}
        ))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            reverse('account_login') + '?next=/bots/edit/%s/settings' % self.ai['aiid']
        )

    @patch('botstore.templatetags.botstore_tags.get_categories')
    @patch('studio.views.get_ai')
    @patch('studio.views.get_ai_details')
    def test_registred(self, mock_get_ai_details, mock_get_ai, mock_get_categories):

        mock_get_ai.return_value = self.ai
        mock_get_ai_details.return_value = self.ai_details
        mock_get_categories.return_value = []

        response = self.client.get(reverse(
            'studio:settings',
            kwargs={'aiid': self.ai['aiid']}
        ))
        self.assertEqual(response.status_code, 200)


class TestSkillsUpdateView(TestCase):

    @factory.django.mute_signals(user_logged_in)
    def setUp(self):
        """Create a user to test response as registered user"""

        self.user = UserFactory()
        self.ai = factory.build(dict, FACTORY_CLASS=AiFactory)
        self.ai_details = factory.build(dict, FACTORY_CLASS=AIDetails)
        Profile.objects.create(user=self.user)

        self.client.force_login(self.user)
        session = self.client.session
        session['token'] = 'token'
        session.save()

    def test_anonymous(self):
        """Anonymous can't access update skills"""

        self.client.logout()
        response = self.client.get(reverse(
            'studio:skills',
            kwargs={
                'aiid': self.ai['aiid']
            }
        ))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            reverse('account_login') + '?next=/bots/edit/%s/skills' % self.ai['aiid']
        )

    @patch('botstore.templatetags.botstore_tags.get_categories')
    @patch('studio.forms.get_purchased')
    @patch('studio.views.get_ai')
    @patch('studio.views.get_ai_details')
    def test_registred(self, mock_get_ai_details, mock_get_ai, mock_get_purchased, mock_get_categories):
        """
        Logged-in users can access update skills. We need to mock `get_aiid`
        and `get_purchased` skill to build the form. `get_categories` is mocked
        cause `Embed` is calling it using Navigation template
        """

        # We mock API calls
        mock_get_ai.return_value = self.ai
        mock_get_ai_details.return_value = self.ai_details
        mock_get_purchased.return_value.json.return_value = [
            factory.build(dict, FACTORY_CLASS=AiFactory),
            factory.build(dict, FACTORY_CLASS=AiFactory),
            factory.build(dict, FACTORY_CLASS=AiFactory)
        ]
        mock_get_categories.return_value = []

        response = self.client.get(reverse(
            'studio:skills',
            kwargs={
                'aiid': self.ai['aiid']
            }
        ))
        self.assertEqual(response.status_code, 200)


class TestIntentsView(TestCase):

    @factory.django.mute_signals(user_logged_in)
    def setUp(self):
        """Create a user to test response as registered user"""

        self.user = UserFactory()
        self.ai = factory.build(dict, FACTORY_CLASS=AiFactory)
        self.ai_details = factory.build(dict, FACTORY_CLASS=AIDetails)
        Profile.objects.create(user=self.user)

        self.client.force_login(self.user)
        session = self.client.session
        session['token'] = 'token'
        session.save()

    def test_anonymous(self):
        """Anonymous can't access update intents"""

        self.client.logout()
        response = self.client.get(reverse(
            'studio:intents',
            kwargs={
                'aiid': self.ai['aiid']
            }
        ))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            reverse('account_login') + '?next=/bots/edit/%s/intents' % self.ai['aiid']
        )


    @patch('botstore.templatetags.botstore_tags.get_categories')
    @patch('studio.views.get_entities_list')
    @patch('studio.views.get_ai')
    @patch('studio.views.get_ai_details')
    def test_registred(
        self, mock_get_ai_details, mock_get_ai, mock_get_entities_list, mock_get_categories
    ):
        """
        Logged-in users can access update intents. We need to mock `get_aiid`
        and `get_purchased` skill to build the form. `get_categories` is mocked
        cause `Embed` is calling it using Navigation template
        """

        # We mock API calls
        mock_get_ai.return_value = self.ai
        mock_get_ai_details.return_value = self.ai_details
        mock_get_entities_list.return_value.json.return_value = []
        mock_get_categories.return_value = []

        response = self.client.get(reverse(
            'studio:intents',
            kwargs={
                'aiid': self.ai['aiid']
            }
        ))
        self.assertEqual(response.status_code, 200)

    @patch('botstore.templatetags.botstore_tags.get_categories')
    @patch('studio.views.get_entities_list')
    @patch('studio.views.get_ai')
    @patch('studio.views.get_ai_details')
    def test_intents(
        self, mock_get_ai_details, mock_get_ai, mock_get_entities_list, mock_get_categories
    ):
        """
        Logged-in users can access update intents. We need to mock `get_aiid`
        and `get_purchased` skill to build the form. `get_categories` is mocked
        cause `Embed` is calling it using Navigation template
        """

        # We mock API calls
        mock_get_ai.return_value = self.ai
        mock_get_ai_details.return_value = self.ai_details
        mock_get_entities_list.return_value.json.return_value = []
        mock_get_categories.return_value = []

        mock_get_ai_details.return_value['intents'] = [
            'intent_1', 'intent_2', 'intent_3', 'intent_4', 'intent_5', 'intent_6'
        ]

        response = self.client.get(reverse(
            'studio:intents',
            kwargs={
                'aiid': self.ai['aiid']
            }
        ))

        self.assertContains(response, 'intent_1')
        self.assertContains(response, 'intent_2')
        self.assertContains(response, 'intent_3')
        self.assertContains(response, 'intent_4')
        self.assertContains(response, 'intent_5')
        self.assertContains(response, 'intent_6')
