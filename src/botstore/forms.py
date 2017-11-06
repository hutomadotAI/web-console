import logging

from django import forms
from django.utils.translation import ugettext_lazy as _
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
)

from botstore.services import post_bot, post_icon

logger = logging.getLogger(__name__)


class PublishForm(forms.Form):
    LICENSE_TYPE = (
        ('Free', _('Free')),
        ('Subscription', _('Subscription')),
        ('Perpetual', _('Perpetual')),
    )

    CATEGORIES = (
        ('Other', _('Other')),
        ('Education', _('Education')),
        ('Entertainment', _('Entertainment')),
        ('Events', _('Events')),
        ('Finance', _('Finance')),
        ('Fitness', _('Fitness')),
        ('Games', _('Games')),
        ('Health & Beauty', _('Health & Beauty')),
        ('Internet of Things', _('Internet of Things')),
        ('News', _('News')),
        ('Personal', _('Personal')),
        ('Shopping', _('Shopping')),
        ('Social', _('Social')),
        ('Sports', _('Sports')),
        ('Travel', _('Travel')),
        ('Virtual Assistants', _('Virtual Assistants'))
    )

    CLASSIFICATION = (
        ('Everyone', _('Everyone')),
        ('Everyone 10+', _('Everyone 10+')),
        ('Teen', _('Teen')),
        ('Mature', _('Mature')),
    )

    MAX_PRICE = 1000
    MIN_PRICE = 0

    name = forms.CharField(
        label=_('Name'),
        widget=forms.TextInput(attrs={'placeholder': _('My bot name')})
    )

    description = forms.CharField(
        label=_('Short Description'),
        widget=forms.TextInput(attrs={'placeholder': _('My bot description…')})
    )

    icon = forms.ImageField(
        label=_('Select file from your computer'),
        widget=forms.FileInput(
            attrs={
                'accept': '.jpg, .jpeg, .png',
                'data-accept': 'image/jpg, image/jpeg, image/png',
                'data-size': '512000',
                'data-type': 'image'
            }
        )
    )

    longDescription = forms.CharField(
        label=_('Long Description'),
        widget=forms.Textarea(attrs={'placeholder': _('Some more details…')})
    )

    sample = forms.CharField(
        label=_('Show Example of Conversation'),
        widget=forms.Textarea(attrs={'placeholder': _('Some more details…')})
    )

    licenseType = forms.ChoiceField(
        label=_('Select License Type'),
        choices=LICENSE_TYPE,
        widget=forms.Select()
    )

    category = forms.ChoiceField(
        label=_('Select Category'),
        choices=CATEGORIES,
        widget=forms.Select()
    )

    classification = forms.ChoiceField(
        disabled=True,
        initial='Everyone',
        label=_('Select Classification'),
        choices=CLASSIFICATION,
        widget=forms.Select(attrs={'readonly': True})
    )

    price = forms.FloatField(
        initial=0,
        label=_('Price'),
        validators=[
            MaxValueValidator(MAX_PRICE),
            MinValueValidator(MIN_PRICE)
        ],
        widget=forms.NumberInput(attrs={
            'min': MIN_PRICE,
            'max': MAX_PRICE,
        })
    )

    privacyPolicy = forms.URLField(
        label=_('Link Privacy Policy Page'),
        widget=forms.URLInput(attrs={
            'placeholder': _('Enter a link to privacy policy')
        })
    )

    version = forms.CharField(
        disabled=True,
        initial='1',
        label=_('Version'),
        widget=forms.TextInput(attrs={
            'placeholder': _('Some more details…'),
            'readonly': True
        })
    )

    alertMessage = forms.CharField(
        label=_('Alert message'),
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': _('Enter a message to show.')
        })
    )

    videoLink = forms.URLField(
        label=_('Link Video Sample'),
        required=False,
        widget=forms.URLInput(attrs={
            'placeholder': _('Enter a link to a video')
        })
    )

    badge = forms.CharField(
        required=False,
        widget=forms.HiddenInput()
    )

    def save(self, *args, **kwargs):
        """Send publishe to API"""

        icon = self.cleaned_data.pop('icon')
        published = post_bot(bot_data=self.cleaned_data, **kwargs)

        if published.get('bot'):
            post_icon(
                bot_id=published['bot']['botId'],
                icon_file=icon,
                **kwargs
            )

        return published
