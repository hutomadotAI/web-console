import json
import logging
import pytz

from django import forms, template
from django.utils.translation import ugettext_lazy as trans
from django.core.validators import RegexValidator

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit

from studio.services import post_ai, post_import_ai

logger = logging.getLogger(__name__)


class AddAI(forms.Form):
    TIMEZONES = [(tz, tz) for tz in pytz.common_timezones]
    VOICES = (
        (0, trans('Female')),
        (1, trans('Male'))
    )
    NAME_PATTERN = '[-a-zA-Z0-9_ ]+'

    name = forms.CharField(
        help_text=trans('Consisting of letters, numbers, spaces, underscores or hyphens.'),
        label=trans('Name'),
        max_length=50,
        validators=[RegexValidator(regex=NAME_PATTERN)],
        widget=forms.TextInput(attrs={
            'pattern': NAME_PATTERN,
            'placeholder': trans('My bot'),
            'title': trans('Enter a valid “Name” consisting of letters, numbers, spaces, underscores or hyphens.')
        })
    )

    description = forms.CharField(
        label=trans('Description'),
        max_length=250,
        widget=forms.TextInput(attrs={'placeholder': trans('Something about the bot')})
    )

    voice = forms.ChoiceField(
        label=trans('Voice'),
        choices=VOICES,
        widget=forms.Select()
    )

    timezone = forms.ChoiceField(
        label=trans('Timezone'),
        choices=TIMEZONES,
        widget=forms.Select()
    )

    def save(self, *args, **kwargs):
        return post_ai(kwargs['user'], self.cleaned_data)


class ImportAI(forms.Form):

    ai_data = forms.FileField(
        label=trans('Exported Bot JSON file'),
        widget=forms.FileInput(attrs={'placeholder': 'YourBotConfig.json'})
    )

    def save(self, *args, **kwargs):

        logger.warning(kwargs['user'])

        data = self.cleaned_data['ai_data'].read().decode('utf8')

        return post_import_ai(kwargs['user'], data)
