from math import log2

from django.core.exceptions import ValidationError
from django.conf import settings
from django.core.validators import BaseValidator
from django.utils.translation import ugettext_lazy as _


class MaxSelectedValidator(BaseValidator):
    """Validates if numer of selected item is les than the limit"""

    message = _('Please select up to %(limit_value)s items')
    code = 'max_selected'

    def compare(self, list, limit):
        return len(list) > limit


class MaxSizeValidator(BaseValidator):
    """Validates uploaded file size in bytes"""

    message = _('File size exceeding maximum upload file size %(limit_value_unitize)s')
    code = 'max_file_size'
    suffixes = ['bytes', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB', 'ZiB', 'YiB']

    def __init__(self, limit_value=settings.MAX_UPLOAD_SIZE, message=None):
        super(MaxSizeValidator, self).__init__(limit_value, message)

    def __call__(self, value):
        cleaned = self.clean(value)
        params = {
            'limit_value': self.limit_value,
            'limit_value_unitize': self.unitize(self.limit_value),
            'show_value': cleaned,
            'value': value
        }
        if self.compare(cleaned, self.limit_value):
            raise ValidationError(self.message, code=self.code, params=params)

    def compare(self, file, limit):
        return file.size > limit

    def unitize(self, size):
        """
            Borrowed from:
            https://stackoverflow.com/questions/1094841/reusable-library-to-get-human-readable-version-of-file-size#answer-25613067
        """
        # determine binary order in steps of size 10
        # (coerce to int, // still returns a float)
        order = int(log2(size) / 10) if size else 0
        # format file size
        # (.4g results in rounded numbers for exact matches and max 3 decimals,
        # should never resort to exponent values)
        return '{value:.4g} {unit}'.format(
            value=size / (1 << (order * 10)),
            unit=self.suffixes[order]
        )
