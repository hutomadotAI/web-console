import datetime

from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter(name='to_date')
@stringfilter
def to_date(date_string, format):
    """Change string to date object"""
    try:
        return datetime.datetime.strptime(date_string, format)
    except ValueError:
        return None
