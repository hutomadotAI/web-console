import os
from test_plus.test import TestCase

from users.forms import SignupForm


class TestRegistrationForm(TestCase):

    def setUp(self):
        """
        Allow to fake reCaptcha Success. Feed initial data
        """
        os.environ['RECAPTCHA_TESTING'] = 'True'

        self.form_data = {
            'first_name': 'Joe',
            'last_name': 'Doe',
            'email': 'j.doe@company.com',
            'password1': '12345678',
            'company_website': 'https://hutoma.ai',
            'job_role': 'marketer',
            'use_case': 'other',
            'company_size': '1 to 10',
            'agree': 1,
            'g-recaptcha-response': 'PASSED'
        }

    def test_a_valid_registration(self):
        """
        All the fields in registration form are required, including reCaptcha
        """

        self.form = SignupForm(data=self.form_data)

        self.assertTrue(
            self.form.is_valid(),
            'All fields submitted, form is valid'
        )

    def test_missing_recaptcha(self):
        """
        Form is not valid if reCaptcha is missing
        """

        form_data = self.form_data

        del form_data['g-recaptcha-response']

        self.form = SignupForm(data=self.form_data)

        self.assertFalse(
            self.form.is_valid(),
            'Form is not valid if reCaptcha is missing'
        )

    def test_missing_agreement(self):
        """
        Form is not valid if user didn't agree on Terms of service
        """

        form_data = self.form_data

        form_data['agree'] = 0

        self.form = SignupForm(data=self.form_data)

        self.assertFalse(
            self.form.is_valid(),
            'Form is not valid ToS agreement is required'
        )

    def tearDown(self):
        """
        Disable fake reCaptcha success
        """
        del os.environ['RECAPTCHA_TESTING']
