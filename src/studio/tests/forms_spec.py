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
    SkillsForm
)
from studio.tests.factories import AIImportJSON
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
