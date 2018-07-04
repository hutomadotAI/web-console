import logging

from allauth.account.forms import ResetPasswordForm, SignupForm
from allauth.account.utils import filter_users_by_email

from django import forms, template
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from django_countries import countries

from captcha.fields import ReCaptchaField

from users.services import post_info

logger = logging.getLogger(__name__)


class ResetPasswordForm(ResetPasswordForm):
    def clean_email(self):
        """Don't reveal if the user exist"""
        email = self.cleaned_data.get('email')
        self.users = filter_users_by_email(email)
        return email


class SignupForm(SignupForm):

    label = template.loader.get_template(
        'messages/signup_form_agree_label.txt'
    )
    first_name = forms.CharField(
        max_length=64,
        widget=forms.TextInput(attrs={'placeholder': 'John'})
    )
    last_name = forms.CharField(
        max_length=64,
        widget=forms.TextInput(attrs={'placeholder': 'Doe'})
    )
    emailAddress = forms.EmailField(
        label=_('Email'),
        widget=forms.TextInput(attrs={
            'type': 'email',
            'placeholder': 'j.doe@company.com'
        })
    )
    password = forms.CharField(
        label=_('Password'),
        widget=forms.PasswordInput(attrs={
            'placeholder': _('Minimum 8 characters')
        })
    )

    # This sorcery is needed for overwriting default Placeholders
    email = forms.EmailField()
    password1 = forms.CharField()

    agree = forms.BooleanField(
        required=True,
        label=label.render(),
        widget=forms.CheckboxInput
    )
    if settings.RECAPTCHA_PUBLIC_KEY and settings.RECAPTCHA_PRIVATE_KEY:
        captcha = ReCaptchaField(label='', attrs={
            'theme': 'dark',
        })

    def __init__(self, *args, **kwargs):

        # Part 2 of sorcery needed to overwriting default Placeholders
        super(SignupForm, self).__init__(*args, **kwargs)
        self.fields['email'] = self.fields['emailAddress']
        self.fields['password1'] = self.fields['password']
        del self.fields['password'], self.fields['emailAddress']

    def signup(self, request, user):
        user.save()

    def clean_email(self):
        """
            Checks if white-list domains is enabled, and if so check if email
            domain is on the list
        """
        data = self.cleaned_data['email']
        domains = settings.WHITELISTED_EMAIL_DOMAINS
        if domains and data.split('@')[1].lower() not in domains:
            raise forms.ValidationError(_('Your email domain is not allowed'))
        return data


class DeveloperInfoForm(forms.Form):
    COUNTRIES = [(name, name) for name, name in countries]

    name = forms.CharField(
        label=_('Name'),
        widget=forms.TextInput(attrs={'placeholder': 'John Doe'})
    )

    email = forms.EmailField(
        label=_('Email'),
        widget=forms.EmailInput(attrs={'placeholder': 'j.doe@company.com'})
    )

    address = forms.CharField(
        label=_('Address'),
        widget=forms.TextInput(attrs={'placeholder': ''})
    )

    postCode = forms.CharField(
        label=_('Post Code'),
        widget=forms.TextInput(attrs={'placeholder': 'ex. 00123'})
    )

    city = forms.CharField(
        label=_('City'),
        widget=forms.TextInput(attrs={'placeholder': 'ex. Barcelona'})
    )

    country = forms.ChoiceField(
        label=_('Country'),
        choices=COUNTRIES,
        initial='United Kingdom',
        widget=forms.Select()
    )

    website = forms.URLField(
        label=_('Website'),
        widget=forms.URLInput(attrs={'placeholder': 'ex. https://hutoma.ai'})
    )

    company = forms.CharField(
        label=_('Company'),
        widget=forms.TextInput(attrs={'placeholder': 'ex. Hutoma ltd'})
    )

    def save(self, token, dev_id):
        return post_info(token, dev_id, self.cleaned_data)
