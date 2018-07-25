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


@register.filter(name='has_group')
def has_group(user, group_name):
    """Check if user is member of a group"""
    return user.groups.filter(name=group_name).exists()
