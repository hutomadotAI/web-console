import factory
from io import BytesIO
from PIL import Image

from test_plus.test import TestCase

from django.core.files.uploadedfile import InMemoryUploadedFile

from botstore.forms import PublishForm
from botstore.tests.factories import MetadataFactory


class TestPublishForm(TestCase):

    def setUp(self):
        """Provide an icon file"""

        image = Image.new(mode='RGB', size=(200, 200))
        image_file = BytesIO()
        image.save(image_file, 'JPEG')
        image_file.seek(0)

        self.files = {'icon': InMemoryUploadedFile(
            image_file, 'icon', 'random-name.jpg', 'image/jpeg', 124, None
        )}

    def test_valid_publish_form(self):
        """Provide minimal required data"""

        data = factory.build(dict, FACTORY_CLASS=MetadataFactory)

        form = PublishForm(data, files=self.files)

        self.assertTrue(
            form.is_valid(),
            'All data needed, form is valid'
        )

    def test_invalid_publish_form(self):
        """Check required field"""

        data = factory.build(dict, FACTORY_CLASS=MetadataFactory)

        del data['name']

        form = PublishForm(data, files=self.files)

        self.assertFalse(
            form.is_valid(),
            'Name is required, form is invalid'
        )

        del data['description']

        form = PublishForm(data, files=self.files)

        self.assertFalse(
            form.is_valid(),
            'Description is required, form is invalid'
        )

        del data['longDescription']

        form = PublishForm(data, files=self.files)

        self.assertFalse(
            form.is_valid(),
            'Long description is required, form is invalid'
        )

        del data['sample']

        form = PublishForm(data, files=self.files)

        self.assertFalse(
            form.is_valid(),
            'Sample is required, form is invalid'
        )

        del data['privacyPolicy']

        form = PublishForm(data, files=self.files)

        self.assertFalse(
            form.is_valid(),
            'Privacy policy is required, form is invalid'
        )

    def test_invalid_wrong_policy_url(self):
        """Test if Privacy Policy is validated"""

        data = factory.build(
            dict,
            FACTORY_CLASS=MetadataFactory,
            privacyPolicy='Not an URL'
        )

        form = PublishForm(data, files=self.files)

        self.assertFalse(
            form.is_valid(),
            'Privacy Policy isn’t an URL, form is invalid'
        )

    def test_invalid_wrong_video_url(self):
        """Test if Privacy Policy is validated"""

        data = factory.build(
            dict,
            FACTORY_CLASS=MetadataFactory,
            videoLink='Not an URL'
        )

        form = PublishForm(data, files=self.files)

        self.assertFalse(
            form.is_valid(),
            'Video link isn’t an URL, form is invalid'
        )

    def test_invalid_price(self):
        """Test if Price is validated"""

        data = factory.build(dict, FACTORY_CLASS=MetadataFactory)

        data['price'] = -1

        form = PublishForm(data, files=self.files)

        self.assertFalse(
            form.is_valid(),
            'Price less then zero, form is invalid'
        )

        data['price'] = 100000

        form = PublishForm(data, files=self.files)

        self.assertFalse(
            form.is_valid(),
            'Price more than max, form is invalid'
        )

        data['price'] = 0

        form = PublishForm(data, files=self.files)

        self.assertTrue(
            form.is_valid(),
            'Price is zero, form is valid'
        )

        data['price'] = 42

        form = PublishForm(data, files=self.files)

        self.assertTrue(
            form.is_valid(),
            'Price is less than max, form is valid'
        )
