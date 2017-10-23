import logging

from django import forms, template
from django.utils.translation import ugettext_lazy as _

from captcha.fields import ReCaptchaField

logger = logging.getLogger(__name__)


class SignupForm(forms.Form):

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
        widget=forms.TextInput(attrs={'type': 'email', 'placeholder': 'j.doe@company.com'})
    )
    password = forms.CharField(
        label=_('Password'),
        widget=forms.PasswordInput(attrs={'placeholder': _('Minimum 8 characters')})
    )

    # This sorcery is needed for overwriting default Placholders
    email = forms.EmailField()
    password1 = forms.CharField()

    agree = forms.BooleanField(
        required=True,
        label=label.render(),
        widget=forms.CheckboxInput
    )
    captcha = ReCaptchaField(label='', attrs={
        'theme': 'dark',
    })

    def __init__(self, *args, **kwargs):

        # Part 2 of sorcery needed to overwriting default Placholders
        super(SignupForm, self).__init__(*args, **kwargs)
        self.fields['email'] = self.fields['emailAddress']
        self.fields['password1'] = self.fields['password']
        del self.fields['password'], self.fields['emailAddress']

    def signup(self, request, user):
        user.save()
