import logging
import pytz

from django import forms
from django.conf import settings
from django.core.validators import RegexValidator
from django.utils.translation import ugettext_lazy as _

from app.validators import MaxSelectedValidator

from studio.services import (
    post_ai,
    post_import_ai,
    post_ai_skill,
    post_training,
    put_training_start
)
from botstore.services import get_purchased

logger = logging.getLogger(__name__)


class SkillsMultiple(forms.widgets.CheckboxSelectMultiple):
    """Custom form widget for skill cards"""

    template_name = 'forms/widgets/skills.html'
    option_template_name = 'forms/widgets/skill.html'

    def get_context(self, name, value, attrs):
        """
        Provide “MEDIA_URL” as Context processors aren't run for widgets
        """
        context = super(SkillsMultiple, self).get_context(name, value, attrs)
        context['MEDIA_URL'] = settings.MEDIA_URL
        return context


class AddAIForm(forms.Form):
    TIMEZONES = [(tz, tz) for tz in pytz.common_timezones]
    VOICES = (
        (0, _('Female')),
        (1, _('Male'))
    )
    NAME_PATTERN = '[-a-zA-Z0-9_ ]+'

    name = forms.CharField(
        help_text=_('Consisting of letters, numbers, spaces, underscores or hyphens.'),
        label=_('Name'),
        max_length=50,
        validators=[RegexValidator(regex=NAME_PATTERN)],
        widget=forms.TextInput(attrs={
            'pattern': NAME_PATTERN,
            'placeholder': _('My bot'),
            'title': _('Enter a valid “Name” consisting of letters, numbers, spaces, underscores or hyphens.')
        })
    )

    description = forms.CharField(
        label=_('Description'),
        max_length=250,
        widget=forms.TextInput(attrs={'placeholder': _('Something about the bot')})
    )

    voice = forms.ChoiceField(
        label=_('Voice'),
        choices=VOICES,
        widget=forms.Select()
    )

    timezone = forms.ChoiceField(
        label=_('Timezone'),
        choices=TIMEZONES,
        widget=forms.Select()
    )

    def save(self, *args, **kwargs):
        return post_ai(kwargs['token'], self.cleaned_data)


class ImportAIForm(forms.Form):

    ai_data = forms.FileField(
        label=_('Exported Bot JSON file'),
        widget=forms.FileInput(attrs={'placeholder': 'YourBotConfig.json'})
    )

    def save(self, *args, **kwargs):
        data = self.cleaned_data['ai_data'].read().decode('utf8')
        return post_import_ai(kwargs['token'], data)


class TrainingForm(forms.Form):

    file = forms.FileField(
        label=_('Add training file'),
        widget=forms.FileInput(attrs={
            'placeholder': _('Select a txt file')
        })
    )

    def save(self, *args, **kwargs):
        """Upload a file and start a new training"""

        file = self.cleaned_data['file']
        ai = post_training(kwargs['token'], kwargs['aiid'], file)

        if ai['status']['code'] in [200, 201]:
            return put_training_start(kwargs['token'], kwargs['aiid'])
        else:
            return ai


class SkillsForm(forms.Form):
    """
    List all purchased skills which can be linked with a bot, link up to
    5 skills
    """

    skills = forms.MultipleChoiceField(
        label='',
        required=False,
        validators=[MaxSelectedValidator(5)],
        widget=SkillsMultiple()
    )

    def __init__(self, *args, **kwargs):
        """Get initial choices for the form"""

        self.token = kwargs.pop('token', None)
        self.aiid = kwargs.pop('aiid', None)
        skills = [
            (skill['botId'], skill) for skill in get_purchased(self.token)
        ]
        super(SkillsForm, self).__init__(*args, **kwargs)
        self.fields['skills'].choices = skills

    def save(self, *args, **kwargs):
        return post_ai_skill(self.token, self.aiid, self.cleaned_data)
