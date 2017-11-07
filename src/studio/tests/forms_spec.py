import json
import factory
import tempfile

from test_plus.test import TestCase
from unittest.mock import Mock, patch

from django.core.files.uploadedfile import SimpleUploadedFile

from studio.forms import (
    AddAIForm,
    ImportAIForm,
    TrainingForm,
    SkillsForm,
    EntityForm,
    EntityFormset,
    IntentForm,
)
from studio.tests.factories import (
    AIImportJSON,
    EntityFactory,
    EntityFormsetFactory,
    IntentFactory,
)
from botstore.tests.factories import MetadataFactory


class TestImportAIForm(TestCase):

    def test_a_valid_import_json(self):
        """
        Provide a valid AI JSON import file
        """
        data = factory.build(dict, FACTORY_CLASS=AIImportJSON)
        json_file = tempfile.NamedTemporaryFile()
        json_file.write(json.dumps(data).encode('gbk'))

        # First seek to a non zero offset.
        json_file.seek(2)
        self.form = ImportAIForm({}, {
            'ai_data': SimpleUploadedFile('ai.json', json_file.read())
        })

        self.assertTrue(
            self.form.is_valid(),
            'All fields submitted, form is valid'
        )

    def test_missing_file(self):
        """
        A valid form should have a JSON file
        """
        self.form = ImportAIForm({}, {})

        self.assertFalse(
            self.form.is_valid(),
            'A valid form should have a JSON file'
        )


class TestAddAIForm(TestCase):

    def setUp(self):
        """
        Provide data
        """
        self.data = {
            'name': 'AI name',
            'description': 'AI description',
            'voice': 0,
            'timezone': 'Europe/London'
        }

    def test_a_valid_form(self):
        """
        Provide a valid AI JSON import file
        """
        self.form = AddAIForm(self.data)
        self.assertTrue(
            self.form.is_valid(),
            'All fields submitted, form is valid'
        )

    def test_missing_name(self):
        """
        A valid form should have a name field
        """
        del self.data['name']
        self.form = AddAIForm(self.data)

        self.assertFalse(
            self.form.is_valid(),
            'A valid form should have a name field'
        )

    def test_missing_description(self):
        """
        A valid form should have a description field
        """
        del self.data['description']
        self.form = AddAIForm(self.data)

        self.assertFalse(
            self.form.is_valid(),
            'A valid form should have a description field'
        )

    def test_name_format(self):
        """
        A valid name is consisting of letters, numbers, underscores or hyphens
        """

        self.data['name'] = '!@#$%^&*()+'
        self.form = AddAIForm(self.data)

        self.assertFalse(
            self.form.is_valid(),
            'A valid name is consisting of letters, numbers, underscores or hyphens'
        )


class TestSkillsForm(TestCase):

    def setUp(self):
        """Provide purchased bots"""

        self.purchased = [
            factory.build(
                dict,
                FACTORY_CLASS=MetadataFactory,
                botId=index
            ) for index in range(1, 6)
        ]

    @patch('studio.forms.get_purchased')
    def test_no_linked_skills(self, mock_get_purchased):
        """Should pass, empty list is allowed"""

        mock_get_purchased.return_value = self.purchased
        form = SkillsForm({'skills': []})

        self.assertTrue(
            form.is_valid(),
            'Empty list is allowed"'
        )

    @patch('studio.forms.get_purchased')
    def test_one_linked_skill(self, mock_get_purchased):
        """Should pass, only one skill is allowed"""

        mock_get_purchased.return_value = self.purchased
        form = SkillsForm({'skills': [1]})

        self.assertTrue(
            form.is_valid(),
            'Only one skill is allowed'
        )

    @patch('studio.forms.get_purchased')
    def test_tree_linked_skill(self, mock_get_purchased):
        """Should pass, multiple skills are allowed"""

        mock_get_purchased.return_value = self.purchased
        form = SkillsForm({'skills': [1, 2, 3]})

        self.assertTrue(
            form.is_valid(),
            'Multiple skills are allowed'
        )

    @patch('studio.forms.get_purchased')
    def test_six_linked_skill(self, mock_get_purchased):
        """Should fail, no more than 5 skills"""

        mock_get_purchased.return_value = self.purchased
        form = SkillsForm({'skills': [1, 2, 3, 4, 5, 6]})

        self.assertFalse(
            form.is_valid(),
            'No more than 5 skills'
        )

    @patch('studio.forms.get_purchased')
    def test_linked_skill_out_of_choice(self, mock_get_purchased):
        """Should fail, skill ID out of choice"""

        mock_get_purchased.return_value = self.purchased
        form = SkillsForm({'skills': [123]})

        self.assertFalse(
            form.is_valid(),
            'Skill ID out of choice'
        )


class TestTrainingForm(TestCase):

    def test_a_valid_training_file(self):
        """Provide a Training file"""

        data = factory.build(dict, FACTORY_CLASS=AIImportJSON)
        training_file = tempfile.NamedTemporaryFile()
        training_file.write(json.dumps(data).encode('gbk'))

        # First seek to a non zero offset.
        training_file.seek(2)
        self.form = TrainingForm({}, {
            'file': SimpleUploadedFile('training.txt', training_file.read())
        })

        print(self.form)

        self.assertTrue(
            self.form.is_valid(),
            'All fields submitted, form is valid'
        )

    def test_missing_file(self):
        """A valid form should have a Training file"""

        self.form = TrainingForm({}, {})

        self.assertFalse(
            self.form.is_valid(),
            'A valid form should have a training file'
        )


class TestIntentForm(TestCase):

    def test_a_valid_intent_without_webhook(self):
        """Provide minimal required data"""

        data = factory.build(dict, FACTORY_CLASS=IntentFactory)

        form = IntentForm(data)

        self.assertTrue(
            form.is_valid(),
            'Even with empty Webhook, form is valid'
        )

    def test_a_valid_intent_with_webhook(self):
        """Test webhook URL"""

        data = factory.build(
            dict,
            FACTORY_CLASS=IntentFactory,
            webhook='http://hutoma.ai'
        )

        form = IntentForm(data)

        self.assertTrue(
            form.is_valid(),
            'Webhook is an URL, form is valid'
        )

    def test_an_invalid_intent_with_webhook(self):
        """Test if Webhook is validated"""

        data = factory.build(
            dict,
            FACTORY_CLASS=IntentFactory,
            webhook='Not an URL'
        )

        form = IntentForm(data)

        self.assertFalse(
            form.is_valid(),
            'Webhook isn’t an URL, form is invalid'
        )

    def test_an_invalid_intent_without_responses(self):
        """Responses are required"""

        data = factory.build(
            dict,
            FACTORY_CLASS=IntentFactory,
            responses=''
        )

        form = IntentForm(data)

        self.assertFalse(
            form.is_valid(),
            'Responses is missing, form is invalid'
        )

    def test_an_invalid_intent_without_user_says(self):
        """Users says is required"""

        data = factory.build(
            dict,
            FACTORY_CLASS=IntentFactory,
            user_says=''
        )

        form = IntentForm(data)

        self.assertFalse(
            form.is_valid(),
            'User say is missing, form is invalid'
        )

    def test_clean_response(self):
        """Responses are converted to a list"""

        data = factory.build(
            dict,
            FACTORY_CLASS=IntentFactory
        )

        form = IntentForm(data)

        form.is_valid()

        self.assertSequenceEqual(
            form.cleaned_data['responses'],
            ['Response 1', 'Response 2', 'Response 3'],
            'Responses needs to be a list'
        )

    def test_clean_user_says(self):
        """User say are converted to a list"""

        data = factory.build(
            dict,
            FACTORY_CLASS=IntentFactory
        )

        form = IntentForm(data)

        form.is_valid()

        self.assertSequenceEqual(
            form.cleaned_data['user_says'],
            ['User say 1', 'User say 2', 'User say 3'],
            'User say needs to be a list'
        )

    def test_clean_empty_webhook(self):
        """Webhook is an object, and not enabled"""

        data = factory.build(
            dict,
            FACTORY_CLASS=IntentFactory
        )

        form = IntentForm(data)

        form.is_valid()

        self.assertEqual(
            form.cleaned_data['webhook'],
            {
                'intent_name': 'Intent_name',
                'endpoint': '',
                'enabled': False
            },
            'Webhook is an object, and not enabled'
        )

    def test_clean_webhook(self):
        """Webhook is an object, and enabled"""

        data = factory.build(
            dict,
            FACTORY_CLASS=IntentFactory,
            webhook='http://hutoma.ai'
        )

        form = IntentForm(data)

        form.is_valid()

        self.assertEqual(
            form.cleaned_data['webhook'],
            {
                'intent_name': 'Intent_name',
                'endpoint': 'http://hutoma.ai',
                'enabled': True
            },
            'Webhook is an object, and enabled'
        )

    def test_intent_name_slug(self):
        """Intent name should be a slug"""

        data = factory.build(
            dict,
            FACTORY_CLASS=IntentFactory,
            intent_name='Not a slug'
        )

        form = IntentForm(data)

        self.assertFalse(
            form.is_valid(),
            'Intent name should be a slug'
        )

        data = factory.build(
            dict,
            FACTORY_CLASS=IntentFactory,
            intent_name='!#@$%^&'
        )

        form = IntentForm(data)

        self.assertFalse(
            form.is_valid(),
            'Intent name should be a slug'
        )


class TestEntityFormset(TestCase):

    def test_a_valid_required_entity(self):
        """Provide valid required data"""

        data = factory.build(dict, FACTORY_CLASS=EntityFormsetFactory)

        form = EntityFormset(data, entities=[{'entity_name': 'sys.places'}])

        self.assertTrue(
            form.is_valid(),
            'Provide valid required data, should pass'
        )

    def test_a_valid_not_required_entity(self):
        """Provide valid not required data"""

        data = factory.build(
            dict,
            FACTORY_CLASS=EntityFormsetFactory,
            required=False
        )

        form = EntityFormset(data, entities=[{'entity_name': 'sys.places'}])

        self.assertTrue(
            form.is_valid(),
            'Provide valid not required data, should pass'
        )

    def test_clean_prompts(self):
        """Prompts should be a list"""

        data = factory.build(
            dict,
            FACTORY_CLASS=EntityFormsetFactory
        )

        form = EntityFormset(data)

        form.is_valid()

        self.assertSequenceEqual(
            form.cleaned_data['prompts'],
            ['User prompt 1', 'User prompt 2', 'User prompt 3'],
            'Prompts should be a list, should pass'
        )

    def test_an_invalid_choice(self):
        """Provide an invalid entity name"""

        data = factory.build(
            dict,
            FACTORY_CLASS=EntityFormsetFactory,
            entity_name='something'
        )

        form = EntityFormset(data, entities=[{'entity_name': 'sys.places'}])

        self.assertFalse(
            form.is_valid(),
            'Invalid entity name, should fail'
        )

    def test_an_invalid_prompt_number(self):
        """Provide an invalid number of prompts"""

        data = factory.build(
            dict,
            FACTORY_CLASS=EntityFormsetFactory,
            n_prompts=0
        )

        form = EntityFormset(data, entities=[{'entity_name': 'sys.places'}])

        self.assertFalse(
            form.is_valid(),
            'Invalid entity name, should be greater than 0, should fail'
        )

        data = factory.build(
            dict,
            FACTORY_CLASS=EntityFormsetFactory,
            n_prompts=19
        )

        form = EntityFormset(data, entities=[{'entity_name': 'sys.places'}])

        self.assertFalse(
            form.is_valid(),
            'Invalid entity name, should be lower than 16, should fail'
        )


class TestEntityForm(TestCase):

    def test_a_valid_entity(self):
        """Provide valid data"""

        data = factory.build(dict, FACTORY_CLASS=EntityFactory)

        form = EntityForm(data)

        self.assertTrue(
            form.is_valid(),
            'Provide valid required data, should pass'
        )

    def test_clean_values(self):
        """Prompts should be a list"""

        data = factory.build(dict, FACTORY_CLASS=EntityFactory)

        form = EntityForm(data)

        form.is_valid()

        self.assertSequenceEqual(
            form.cleaned_data['entity_values'],
            ['Value 1', 'Value 2', 'Value 3'],
            'Values should be a list, should pass'
        )
