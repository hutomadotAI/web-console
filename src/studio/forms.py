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

from app.validators import MaxSelectedValidator, MaxSizeValidator

from studio.services import (
    delete_ai,
    post_ai,
    post_ai_skill,
    post_clone_ai,
    post_entity,
    post_import_ai,
    post_intent,
    post_intent_bulk,
    post_regenerate_webhook_secret,
    post_training
)
from botstore.services import get_purchased

logger = logging.getLogger(__name__)

NAME_PATTERN = '[-a-zA-Z0-9_ ]+'
SLUG_PATTERN = '^[-a-zA-Z0-9_]+$'
VARIABLE_PATTERN = '^[-a-zA-Z0-9_\.]+$'

DEFAULT_TOKEN_CHARACTERS_LIMIT = 250
INTENT_TOKEN_CHARACTERS_LIMIT = 1000


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
            'maxlength': 128,
            'placeholder': _('Entity name'),
            'title': _('Enter a valid “Entity name” consisting of letters, '
                       'numbers, underscores or hyphens.')
        })
    )

    entity_values = forms.CharField(
        label=_('Values'),
        help_text=_('To create a new value press enter'),
        widget=forms.TextInput(attrs={
            'data-min-length': 1,
            'data-max-length': DEFAULT_TOKEN_CHARACTERS_LIMIT,
            'data-delimiter': settings.TOKENFIELD_DELIMITER,
            'data-tokenfield': True,
            'class': 'form-control',
            'placeholder': _('Add an entity value'),
        })
    )

    def clean_entity_values(self):
        """Split values"""
        split_list = self.cleaned_data['entity_values'].split(
            settings.TOKENFIELD_DELIMITER
        )
        stripped_list = [item.strip() for item in split_list]
        return stripped_list

    def save(self, *args, **kwargs):
        return post_entity(self.cleaned_data, **kwargs)


class ContextFormset(forms.Form):
    """Used adding context variables on Intents tab"""

    variable = forms.CharField(
        label=_('Variable'),
        validators=[RegexValidator(regex=VARIABLE_PATTERN)],
        widget=forms.TextInput(attrs={
            'pattern': VARIABLE_PATTERN,
            'maxlength': 250,
            'required': True,
            'placeholder': _('ex. variable_1'),
            'title': _('A valid “Variable” consisting of letters, numbers, '
                       'dots, underscores or hyphens.')
        }),
        required=True
    )

    value = forms.CharField(
        label=_('Value'),
        widget=forms.TextInput(attrs={
            'maxlength': 250,
            'required': True,
        }),
        required=True
    )


class ConditionsFormset(forms.Form):
    """Used adding conditions on Intents tab"""

    variable = forms.CharField(
        label=_('Variable'),
        validators=[RegexValidator(regex=VARIABLE_PATTERN)],
        widget=forms.TextInput(attrs={
            'pattern': VARIABLE_PATTERN,
            'maxlength': 250,
            'required': True,
            'placeholder': _('ex. variable_1'),
            'title': _('A valid “Variable” consisting of letters, numbers, '
                       'dots, underscores or hyphens.')
        })
    )

    operator = forms.ChoiceField(
        label='',
        choices=[
            ('SET', _('Set')),
            ('NOT_SET', _('Not Set')),
            ('EQUALS', _('Equals')),
            ('NOT_EQUALS', _('Not Equals')),
            ('SMALLER_THAN', _('Smaller Than')),
            ('SMALLER_THAN_OR_EQUALS', _('Smaller Than or Equals')),
            ('GREATER_THAN', _('Greater Than')),
            ('GREATER_THAN_OR_EQUALS', _('Greater Than or Equals'))
        ],
        widget=forms.Select()
    )

    value = forms.CharField(
        label=_('Value (optional)'),
        widget=forms.TextInput(attrs={
            'maxlength': 250,
            'placeholder': _('ex. true')
        }),
        required=False
    )

    def clean_value(self):
        data = self.cleaned_data['value']
        cleaned_data = super().clean()
        variable = cleaned_data.get('variable')
        operator = cleaned_data.get('operator')
        value = cleaned_data.get('value')

        if operator not in ['SET', 'NOT_SET'] and not value:
            # Only do something if both fields are valid so far.
            raise forms.ValidationError(
                'Variable {variable_name} value is missing '.format(variable_name=variable)
            )

        return data


class FollowUpFormset(forms.Form):
    """Used for adding follow up on Intents tab"""

    intent_to_execute = forms.ChoiceField(
        label=_('Intent'),
        widget=forms.Select(),
        required=True
    )

    def __init__(self, *args, **kwargs):
        """Get initial choices for the form and add conditions formset"""

        intents = kwargs.pop('intents', [])
        current_intent = kwargs.pop('current_intent', {})
        initial = kwargs.get('initial', {})
        conditions = initial.get('conditions', [])

        super(FollowUpFormset, self).__init__(*args, **kwargs)

        self.fields['intent_to_execute'].choices = [
            (intent, intent) for intent in intents
            if not current_intent or not intent == current_intent['intent_name']
        ]

        conditions_formset = forms.formset_factory(
            ConditionsFormset,
            extra=0 if conditions else 1,
            can_delete=True
        )

        self.nested = conditions_formset(
            initial=conditions,
            data=kwargs.get('data'),
            prefix=kwargs.get('prefix')
        )

    def clean(self, *args, **kwargs):
        """Pass nested formset data if instance is not removed"""
        cleaned = super(FollowUpFormset, self).clean(*args, **kwargs)
        cleaned['conditions'] = [] if cleaned['DELETE'] else self.nested.cleaned_data
        return cleaned


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
        initial=True,
        required=False,
    )

    entity_name = forms.ChoiceField(
        label=_('Entity name'),
        widget=forms.Select()
    )

    n_prompts = forms.IntegerField(
        initial=3,
        label=_('N prompts'),
        validators=[
            MaxValueValidator(16),
            MinValueValidator(1)
        ],
        widget=forms.NumberInput(attrs={
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
            'pattern': SLUG_PATTERN,
            'maxlength': 250,
            'required': True,
            'placeholder': _('Unique label'),
            'title': _('Enter a valid “Label” consisting of letters, numbers, '
                       'underscores or hyphens.')
        })
    )

    prompts = forms.CharField(
        label=_('Prompts'),
        widget=forms.TextInput(attrs={
            'data-min-length': 1,
            'data-max-length': DEFAULT_TOKEN_CHARACTERS_LIMIT,
            'data-delimiter': settings.TOKENFIELD_DELIMITER,
            'data-tokenfield': True,
            'required': True,
            'placeholder': _('Add a user prompt'),
        })
    )

    def clean_prompts(self):
        """Split prompts"""
        prompts = self.cleaned_data['prompts'].split(
            settings.TOKENFIELD_DELIMITER
        )
        stripped_list = [item.strip() for item in prompts]
        return stripped_list


class IntentForm(forms.Form):

    intent_name = forms.CharField(
        label=_('Name'),
        max_length=32,
        validators=[RegexValidator(regex=SLUG_PATTERN)],
        widget=forms.TextInput(attrs={
            'pattern': SLUG_PATTERN,
            'maxlength': 32,
            'placeholder': _('Intent name'),
            'title': _('Enter a valid “Name” consisting of letters, numbers, '
                       'underscores or hyphens.')
        })
    )

    user_says = forms.CharField(
        label=_('Human Says <small>optional</small>'),
        help_text=_('To create a new expression press enter'),
        widget=forms.TextInput(attrs={
            'data-max-length': INTENT_TOKEN_CHARACTERS_LIMIT,
            'data-delimiter': settings.TOKENFIELD_DELIMITER,
            'data-tokenfield': True,
            'placeholder': _('Add a user expression'),
            'title': _('Enter a valid input consisting of letters, numbers, '
                       'spaces, underscores or hyphens.')
        }),
        required=False
    )

    responses = forms.CharField(
        label=_('Bot Responds <small>optional</small>'),
        help_text=_('To create a new response press enter'),
        widget=forms.TextInput(attrs={
            'data-max-length': INTENT_TOKEN_CHARACTERS_LIMIT,
            'data-delimiter': settings.TOKENFIELD_DELIMITER,
            'data-tokenfield': True,
            'placeholder': _('Add a sample bot response'),
        }),
        required=False
    )

    conditions_default_response = forms.CharField(
        label=_('Fallback response (optional)'),
        help_text=_('Bot would use it if any of the conditions fails'),
        required=False,
        widget=forms.TextInput(attrs={
            'data-limit': 1,
            'data-min-length': 1,
            'data-max-length': DEFAULT_TOKEN_CHARACTERS_LIMIT,
            'data-delimiter': settings.TOKENFIELD_DELIMITER,
            'data-tokenfield': True,
            'data-min-width': 240,
            'placeholder': _('ex. Please provide a fallback response'),
        })
    )

    webhook = forms.URLField(
        label=_('WebHook (optional)'),
        help_text=_('Provide the WebHook endpoint.'),
        required=False,
        widget=forms.URLInput(attrs={
            'placeholder': _('ex. https://hutoma.ai/webhook_url'),
        })
    )

    reset_context_on_exit = forms.BooleanField(
        label=_('Reset context when the intent is completed'),
        required=False,
        widget=forms.CheckboxInput()
    )

    def clean_user_says(self):
        """Split expressions"""
        user_says = self.cleaned_data['user_says'].split(
            settings.TOKENFIELD_DELIMITER
        )
        stripped_list = [item.strip() for item in user_says]
        return stripped_list

    def clean_responses(self):
        """Split expressions"""
        responses = self.cleaned_data['responses'].split(
            settings.TOKENFIELD_DELIMITER
        )
        stripped_list = [item.strip() for item in responses]
        return stripped_list

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

        self.cleaned_data['webhook']['aiid'] = str(kwargs['aiid'])

        self.cleaned_data['conditions_in'] = [
            condition for condition in kwargs.pop('conditions_in') if not condition['DELETE']
        ]

        self.cleaned_data['variables'] = [
            entity for entity in kwargs.pop('entities') if not entity['DELETE']
        ]

        self.cleaned_data['context_in'] = {
            variable.get('variable'): variable.get('value')
            for variable in kwargs.pop('context_in') if not variable['DELETE']
        }

        self.cleaned_data['context_out'] = {
            variable.get('variable'): variable.get('value')
            for variable in kwargs.pop('context_out') if not variable['DELETE']
        }

        self.cleaned_data['conditions_out'] = [
            {
                'intent_to_execute': condition_out['intent_to_execute'],
                'conditions': [
                    condition for condition in condition_out['conditions']
                    if not condition['DELETE']
                ]
            } for condition_out in kwargs.pop('conditions_out') if not condition_out['DELETE']
        ]

        return {
            **post_intent(self.cleaned_data, **kwargs),
            'cleaned_data': self.cleaned_data
        }


class AddAIForm(forms.Form):
    TIMEZONES = [(tz, tz) for tz in pytz.common_timezones]

    name = forms.CharField(
        help_text=_('Consisting of letters, numbers, spaces, underscores or hyphens.'),
        label=_('Name'),
        max_length=50,
        validators=[RegexValidator(regex=NAME_PATTERN)],
        widget=forms.TextInput(attrs={
            'pattern': NAME_PATTERN,
            'placeholder': _('My bot'),
            'title': _('Enter a valid “Name” consisting of letters, numbers, '
                       'spaces, underscores or hyphens.'),
            'tabindex': 1
        })
    )

    description = forms.CharField(
        label=_('Description'),
        max_length=250,
        widget=forms.TextInput(attrs={
            'placeholder': _('Something about the bot'),
            'tabindex': 2
        })
    )

    timezone = forms.ChoiceField(
        initial='Europe/London',
        label=_('Timezone'),
        choices=TIMEZONES,
        widget=forms.Select(attrs={
            'tabindex': 3
        })
    )

    default_chat_responses = forms.CharField(
        help_text=_('To create a new response press enter'),
        label=_('Default Response <small>This is sent when the bot doesn’t '
                'understand the user.</small>'),
        initial=_('Sorry I didn\'t understand, can you try rephrasing the question?'),
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'data-min-length': 1,
            'data-max-length': DEFAULT_TOKEN_CHARACTERS_LIMIT,
            'data-delimiter': settings.TOKENFIELD_DELIMITER,
            'data-tokenfield': True,
            'required': True,
            'placeholder': _('Edit bot response here'),
            'tabindex': 4
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


class CloneAIForm(AddAIForm):
    def save(self, *args, **kwargs):
        return post_clone_ai(ai_data=self.cleaned_data, **kwargs)


class SettingsAIForm(AddAIForm):

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
            'title': _('Enter a valid “Name” consisting of letters, numbers, '
                       'spaces, underscores or hyphens.')
        })
    )

    handover_message = forms.CharField(
        help_text=_('This is sent when the bot doesn\'t understand the user and '
                    'will no longer respond until a human takes over.'),
        initial=_('Chat disabled — handed over to external agent'),
        label='',
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'data-limit': 1,
            'data-min-length': 1,
            'data-max-length': DEFAULT_TOKEN_CHARACTERS_LIMIT,
            'data-delimiter': settings.TOKENFIELD_DELIMITER,
            'data-tokenfield': True,
            'required': False,
            'placeholder': _('add bot handover message'),
            'tabindex': 5
        })
    )

    handover_reset_timeout_seconds = forms.IntegerField(
        label=_('Handover Reset Timeout'),
        required=False,
        validators=[
            MinValueValidator(0)
        ],
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': 0,
            'required': False,
            'placeholder': _('ex. 15'),
        })
    )

    error_threshold_handover = forms.ChoiceField(
        label=_('Handover responses'),
        required=False,
        choices=[
            (-1, _('Off')),
            (1, _('Handover after 1 default error response')),
            (2, _('Handover after 2 default error responses')),
            (3, _('Handover after 3 default error responses')),
            (4, _('Handover after 4 default error responses'))
        ],
        widget=forms.Select(attrs={
            'class': 'form-control',
            'required': False
        })
    )

    def clean_handover_reset_timeout_seconds(self):
        """Change minutes to seconds"""

        return self.cleaned_data['handover_reset_timeout_seconds'] * 60


class ImportAIForm(forms.Form):

    ai_data = forms.FileField(
        label=_('Exported Bot JSON file'),
        validators=[MaxSizeValidator()],
        widget=forms.FileInput(attrs={
            'accept': '.json, application/json',
            'placeholder': 'YourBotConfig.json',
            'class': 'form-control'
        })
    )

    def clean_ai_data(self):
        """Check if imported data is a valid JSON"""
        ai_data = self.cleaned_data['ai_data']
        try:
            ai_data = json.loads(ai_data.read().decode('utf8'))
        except (json.JSONDecodeError, UnicodeDecodeError) as error:
            raise forms.ValidationError('Invalid JSON file')
        return ai_data

    def save(self, *args, **kwargs):
        data = self.cleaned_data['ai_data']
        return post_import_ai(ai_data=data, **kwargs)


class TrainingForm(forms.Form):

    training_data = forms.CharField(
        label='',
        widget=forms.Textarea(attrs={
            'placeholder': _("""Pairs of Questions and answers:

    What is your name?
    My name is Hu:toma.

    What does Hu:toma mean?
    It is the combination of two words, human and automata.""")
        })
    )

    def save(self, token, aiid):
        """Upload a file and start a new training"""

        training_data = self.cleaned_data['training_data']

        training = post_training(token, aiid, training_data)

        return training


class IntentBulkUpload(forms.Form):

    intents_file = forms.FileField(
        label=_('Upload CSV file'),
        validators=[MaxSizeValidator()],
        widget=forms.FileInput(attrs={
            'accept': '.csv, application/csv',
            'placeholder': 'intents.csv',
            'class': 'form-control'
        })
    )

    def save(self, token, aiid):
        """Upload a file and start a new training"""

        intents_file = self.cleaned_data['intents_file']

        return post_intent_bulk(token, aiid, intents_file)


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
        bots = get_purchased(self.token).get('bots', [])
        skills = [
            (skill['botId'], skill) for skill in bots
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
