import json
import factory
import tempfile
from test_plus.test import TestCase

from django.core.files.uploadedfile import SimpleUploadedFile

from studio.forms import AddAI, ImportAI
from studio.tests.factories import AIImportJSON


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
        self.form = ImportAI({}, {
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
        self.form = ImportAI({}, {})

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
        self.form = AddAI(self.data)
        self.assertTrue(
            self.form.is_valid(),
            'All fields submitted, form is valid'
        )

    def test_missing_name(self):
        """
        A valid form should have a name field
        """
        del self.data['name']
        self.form = ImportAI(self.data)

        self.assertFalse(
            self.form.is_valid(),
            'A valid form should have a name field'
        )

    def test_missing_description(self):
        """
        A valid form should have a description field
        """
        del self.data['description']
        self.form = ImportAI(self.data)

        self.assertFalse(
            self.form.is_valid(),
            'A valid form should have a description field'
        )

    def test_name_format(self):
        """
        A valid name is consisting of letters, numbers, underscores or hyphens
        """

        self.data['name'] = '!@#$%^&*()+'
        self.form = AddAI(self.data)

        self.assertFalse(
            self.form.is_valid(),
            'A valid name is consisting of letters, numbers, underscores or hyphens'
        )
