import logging
import pytz
import json

from django import forms
from django.conf import settings
from django.core.validators import (
    RegexValidator,
    MaxValueValidator,
    MinValueValidator
)
from django.utils.translation import ugettext_lazy as _

from app.validators import MaxSelectedValidator

from studio.services import (
    delete_ai,
    get_entities_list,
    post_ai,
    post_ai_skill,
    post_entity,
    post_import_ai,
    post_intent,
    post_regenerate_webhook_secret,
    post_training,
    put_training_start,
)
from botstore.services import get_purchased

logger = logging.getLogger(__name__)

NAME_PATTERN = '[-a-zA-Z0-9_ ]+'
SLUG_PATTERN = '^[-a-zA-Z0-9_]+$'


class SkillsMultipleWidget(forms.widgets.CheckboxSelectMultiple):
    """Custom form widget for skill cards"""

    template_name = 'forms/widgets/skills.html'
    option_template_name = 'forms/widgets/skill.html'

    def get_context(self, name, value, attrs):
        """
        Provide “MEDIA_URL” as Context processors aren't run for widgets
        """
        context = super(SkillsMultipleWidget, self).get_context(name, value, attrs)
        context['MEDIA_URL'] = settings.MEDIA_URL
        return context


class EntityForm(forms.Form):

    entity_name = forms.CharField(
        label=_('Name'),
        widget=forms.TextInput(attrs={
            'pattern': SLUG_PATTERN,
            'maxlength': 250,
            'placeholder': _('Entity name'),
            'title': _('Enter a valid “Entity name” consisting of letters, numbers, underscores or hyphens.')
        })
    )

    entity_values = forms.CharField(
        label=_('Values'),
        help_text=_('To create a new value press enter'),
        widget=forms.TextInput(attrs={
            'data-minLength': 1,
            'data-maxlength': 250,
            'data-delimiter': settings.TOKENFIELD_DELIMITER,
            'data-tokenfield': True,
            'class': 'form-control',
            'placeholder': _('Add an entity value'),
        })
    )

    def clean_entity_values(self):
        """Split values"""
        split_list =  self.cleaned_data['entity_values'].split(
            settings.TOKENFIELD_DELIMITER
        )
        stripped_list = [item.strip() for item in split_list]
        return stripped_list

    def save(self, *args, **kwargs):
        return post_entity(self.cleaned_data, **kwargs)


class EntityFormset(forms.Form):
    """Used as base for formset on Intents tab"""

    def __init__(self, *args, **kwargs):
        """Get initial choices for the form"""

        entities = kwargs.pop('entities', [])

        super(EntityFormset, self).__init__(*args, **kwargs)

        self.fields['entity_name'].choices = [
            (entity['entity_name'], entity['entity_name']) for entity in entities
        ]

        # ”The formset is smart enough to ignore extra forms that were not
        # changed.” Make them dummy again and enable requirement checks.
        self.empty_permitted = False

    required = forms.BooleanField(
        label=_('Required'),
        required=False,
    )

    entity_name = forms.ChoiceField(
        label=_('Entity name'),
        widget=forms.Select(attrs={
            'class': 'form-control',
            'required': True,
        })
    )

    n_prompts = forms.IntegerField(
        initial=1,
        label=_('N prompts'),
        validators=[
            MaxValueValidator(16),
            MinValueValidator(1)
        ],
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'max': 16,
            'min': 1,
            'required': True,
            'placeholder': _('ex. 3'),
        })
    )

    label = forms.CharField(
        label=_('Label'),
        validators=[RegexValidator(regex=SLUG_PATTERN)],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'pattern': SLUG_PATTERN,
            'maxlength': 250,
            'required': True,
            'placeholder': _('Unique label'),
            'title': _('Enter a valid “Label” consisting of letters, numbers, underscores or hyphens.')
        })
    )

    prompts = forms.CharField(
        label=_('Prompts'),
        widget=forms.TextInput(attrs={
            'data-minLength': 1,
            'data-maxlength': 250,
            'data-delimiter': settings.TOKENFIELD_DELIMITER,
            'data-tokenfield': True,
            'class': 'form-control',
            'required': True,
            'placeholder': _('Add a user prompt'),
        })
    )

    def clean_prompts(self):
        """Split prompts"""
        return self.cleaned_data['prompts'].split(
            settings.TOKENFIELD_DELIMITER
        )


class IntentForm(forms.Form):

    intent_name = forms.CharField(
        label=_('Name'),
        max_length=250,
        validators=[RegexValidator(regex=SLUG_PATTERN)],
        widget=forms.TextInput(attrs={
            'pattern': SLUG_PATTERN,
            'placeholder': _('Intent name'),
            'title': _('Enter a valid “Name” consisting of letters, numbers, underscores or hyphens.')
        })
    )

    user_says = forms.CharField(
        label=_('Expressions'),
        help_text=_('Give the bot examples of how a user would express this intent. To create a new expression press enter'),
        widget=forms.TextInput(attrs={
            'data-minLength': 1,
            'data-maxlength': 250,
            'data-delimiter': settings.TOKENFIELD_DELIMITER,
            'data-tokenfield': True,
            'placeholder': _('Add a user expression'),
            'title': _('Enter a valid input consisting of letters, numbers, spaces, underscores or hyphens.')
        })
    )

    responses = forms.CharField(
        label=_('Responses'),
        help_text=_('Give the bot examples of how it should respond to a user’s intent. To create a new response press enter'),
        widget=forms.TextInput(attrs={
            'data-minLength': 1,
            'data-maxlength': 250,
            'data-delimiter': settings.TOKENFIELD_DELIMITER,
            'data-tokenfield': True,
            'placeholder': _('Add a sample bot response'),
        })
    )

    webhook = forms.URLField(
        label=_('WebHook'),
        help_text=_('Provide the WebHook endpoint.'),
        required=False,
        widget=forms.URLInput(attrs={
            'placeholder': _('ex. https://hutoma.ai/webhook_url'),
        })
    )

    def clean_user_says(self):
        """Split expressions"""
        return self.cleaned_data['user_says'].split(
            settings.TOKENFIELD_DELIMITER
        )

    def clean_responses(self):
        """Split expressions"""
        return self.cleaned_data['responses'].split(
            settings.TOKENFIELD_DELIMITER
        )

    def clean_webhook(self):
        """Build webhook object"""
        if not self.cleaned_data.get('intent_name'):
            raise forms.ValidationError('intent_name is required')

        return {
            'intent_name': self.cleaned_data['intent_name'],
            'endpoint': self.cleaned_data['webhook'],
            'enabled': bool(self.cleaned_data['webhook']),
        }

    def save(self, *args, **kwargs):
        """Combine form data with entities coming from formset"""

        # TODO: Remove after we refactor Intent API code
        self.cleaned_data['webhook']['aiid'] = kwargs['aiid']

        # TODO: Rename to entities after we refactor Intent API code
        self.cleaned_data['variables'] = [
            entity for entity in kwargs.pop('variables') if not entity['DELETE']
        ]

        return post_intent(self.cleaned_data, **kwargs)


class AddAIForm(forms.Form):
    TIMEZONES = [(tz, tz) for tz in pytz.common_timezones]

    aiid = forms.CharField(
        label=_('Bot ID'),
        max_length=36,
        required=False,
        widget=forms.TextInput(attrs={
            'readonly': True,
            'title': _('Your bot ID')
        })
    )

    name = forms.CharField(
        help_text=_('Consisting of letters, numbers, spaces, underscores or hyphens.'),
        label=_('Name'),
        max_length=50,
        validators=[RegexValidator(regex=NAME_PATTERN)],
        widget=forms.TextInput(attrs={
            'pattern': NAME_PATTERN,
            'placeholder': _('My bot'),
            'readonly': True,
            'title': _('Enter a valid “Name” consisting of letters, numbers, spaces, underscores or hyphens.')
        })
    )

    description = forms.CharField(
        label=_('Description'),
        max_length=250,
        widget=forms.TextInput(attrs={'placeholder': _('Something about the bot')})
    )

    timezone = forms.ChoiceField(
        initial='Europe/London',
        label=_('Timezone'),
        choices=TIMEZONES,
        widget=forms.Select()
    )

    default_chat_responses = forms.CharField(
        help_text=_('To create a new response press enter'),
        label=_('Default responses for when the bot doesn’t understand the user'),
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'data-minLength': 1,
            'data-maxlength': 250,
            'data-delimiter': settings.TOKENFIELD_DELIMITER,
            'data-tokenfield': True,
            'required': True,
            'placeholder': _('Erm… What?')
        })
    )

    def clean_default_chat_responses(self):
        """Split responses and build a list string"""

        return json.dumps(
            self.cleaned_data['default_chat_responses'].split(
                settings.TOKENFIELD_DELIMITER
            )
        )

    def save(self, *args, **kwargs):
        return post_ai(ai_data=self.cleaned_data, **kwargs)


class ImportAIForm(forms.Form):

    ai_data = forms.FileField(
        label=_('Exported Bot JSON file'),
        widget=forms.FileInput(attrs={
            'accept': '.json, application/json',
            'placeholder': 'YourBotConfig.json'
        })
    )

    def save(self, *args, **kwargs):
        data = self.cleaned_data['ai_data'].read().decode('utf8')
        return post_import_ai(ai_data=data, **kwargs)


class TrainingForm(forms.Form):

    file = forms.FileField(
        label=_('Add training file'),
        widget=forms.FileInput(attrs={
            'accept': '.txt, text/plain',
            'placeholder': _('Select a txt file')
        })
    )

    def save(self, token, aiid):
        """Upload a file and start a new training"""

        file = self.cleaned_data['file']
        training = post_training(token, aiid, file)

        if training['status']['code'] in [200, 201]:
            return put_training_start(token, aiid)
        else:
            return training


class SkillsForm(forms.Form):
    """
    List all purchased skills which can be linked with a bot, link up to
    5 skills
    """

    skills = forms.MultipleChoiceField(
        label='',
        required=False,
        validators=[MaxSelectedValidator(5)],
        widget=SkillsMultipleWidget()
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


class ProxyDeleteAIForm(forms.Form):
    """Used for validation of async calls"""

    action = forms.CharField(
        validators=[RegexValidator(regex='delete')],
        widget=forms.HiddenInput()
    )

    aiid = forms.CharField(
        max_length=36,
        widget=forms.HiddenInput()
    )

    def save(self, *args, **kwargs):
        return delete_ai(kwargs['token'], self.cleaned_data['aiid'])


class ProxyRegenerateWebhookSecretForm(forms.Form):
    """Used for validation of async calls"""

    aiid = forms.CharField(
        max_length=36,
        widget=forms.HiddenInput()
    )

    def save(self, *args, **kwargs):
        return post_regenerate_webhook_secret(
            kwargs['token'],
            self.cleaned_data['aiid']
        )

