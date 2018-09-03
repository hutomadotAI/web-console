import logging

from allauth.account.forms import ResetPasswordForm, SignupForm
from allauth.account.utils import filter_users_by_email

from django import forms, template
from django.conf import settings
from django.core.cache import cache
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

    JOB_ROLE = [
        ('', _('Please select one')),
        ('marketer', _('Marketer')),
        ('product manager', _('Product Manager')),
        ('developer', _('Developer')),
        ('business owner', _('Business Owner')),
        ('customer success', _('Customer Success / Support')),
        ('other', _('Other'))
    ]

    COMPANY_SIZE = [
        ('', _('Please select one')),
        ('1 to 10', _('1 to 10')),
        ('10 to 50', _('10 to 50')),
        ('50 to 200', _('50 to 200')),
        ('200 to 1000', _('200 to 1000')),
        ('1000 and more', _('1000 and more'))
    ]

    USE_CASE = [
        ('', _('Please select one')),
        ('automation', _('Automate repetitive customer conversations')),
        ('knowledge base', _('Make internal knowledge easy to access for your team')),
        ('lead generation', _('Convert website visitors into leads or sales')),
        ('working for client', _('Build a conversational experience for a client')),
        ('other', _('Other'))
    ]

    label = template.loader.get_template(
        'messages/signup_form_agree_label.txt'
    )

    email = forms.EmailField(
        label=_('Email'),
        widget=forms.TextInput(attrs={
            'type': 'email',
            'placeholder': 'j.doe@company.com'
        })
    )

    password1 = forms.CharField(
        label=_('Password'),
        help_text=_('Minimum 8 characters'),
        widget=forms.PasswordInput()
    )

    first_name = forms.CharField(
        max_length=64,
        widget=forms.TextInput(attrs={'placeholder': 'John'})
    )

    last_name = forms.CharField(
        max_length=64,
        widget=forms.TextInput(attrs={'placeholder': 'Doe'})
    )

    company_website = forms.URLField(
        label=_('Company website'),
        max_length=128,
        widget=forms.URLInput(attrs={'placeholder': 'ex. https://hutoma.ai'})
    )

    company_size = forms.ChoiceField(
        label=_('Company size'),
        choices=COMPANY_SIZE,
        widget=forms.Select()
    )

    job_role = forms.ChoiceField(
        label=_('Job role'),
        choices=JOB_ROLE,
        widget=forms.Select()
    )

    use_case = forms.ChoiceField(
        label=_('Use case'),
        choices=USE_CASE,
        widget=forms.Select()
    )

    agree = forms.BooleanField(
        required=True,
        label=label.render(),
        widget=forms.CheckboxInput
    )

    if settings.RECAPTCHA_PUBLIC_KEY and settings.RECAPTCHA_PRIVATE_KEY:
        captcha = ReCaptchaField(label='', attrs={
            'theme': 'dark',
        })

    def save(self, request):
        """Cache CRM data so they can be used on registration"""
        user = super(SignupForm, self).save(request)
        crm_data = {
            'company_website': self.cleaned_data['company_website'],
            'job_role': self.cleaned_data['job_role'],
            'use_case': self.cleaned_data['use_case'],
            'company_size': self.cleaned_data['company_size']
        }
        cache_key = settings.CRM_DATA_KEY.format(user_id=user.profile.dev_id)
        timeout = None  # Keep forever
        cache.set(cache_key, crm_data, timeout=timeout)
        return user

    def clean_email(self):
        """
        Checks if white-list domains is enabled, and if so check if email
        domain is on the list
        """
        super(SignupForm, self).clean_email()
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
