from django.core.validators import BaseValidator
from django.utils.translation import ugettext_lazy as trans


class MaxSelectedValidator(BaseValidator):
    """Validates if numer of selected item is les than the limit"""

    message = trans('Please select up to %(limit_value)s items')
    code = 'max_selected'

    def compare(self, a, b):
        return len(a) > b