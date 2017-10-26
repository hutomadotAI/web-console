import logging
import pytz

from django import forms
from django.conf import settings
from django.core.validators import RegexValidator
from django.utils.translation import ugettext_lazy as _

from app.validators import MaxSelectedValidator

from entities.services import *

logger = logging.getLogger(__name__)


class createEntity(forms.Form):
    entity_name = forms.CharField(
        label=_('Name'),
        max_length=50,
        widget=forms.TextInput(attrs={'placeholder': _('Entity_Name')})
    )
    print (str(entity_name))
