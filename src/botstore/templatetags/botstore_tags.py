
"""
`botstore` template tags. To use in a template just put the following
*load* tag inside a template:

    `{% load botstore_tags %}`
"""
import logging

from django import template

from botstore.services import get_categories

logger = logging.getLogger(__name__)
register = template.Library()


@register.filter(name='lookup')
def lookup(dictionary, key):
    """
    Helpers tag to lookup for an entry inside of a dictionary, ruturns `None`
    for nonexisting keys.
    """
    return dictionary.get(key.lower())


@register.inclusion_tag('botstore_navigation.html')
def botstore_navigation(active, botstore):
    """Renders a botstore Naviagtion menu based on API proviaded data"""
    return {
        'categories': get_categories().get('categories'),
        'active': active,
        'botstore': botstore,
        'icons': {
            'entertainment': 'fa-film',
            'education': 'fa-graduation-cap',
            'events': 'fa-calendar-check-o',
            'finance': 'fa-eur',
            'fitness': 'fa-bicycle',
            'games': 'fa-gamepad',
            'health & beauty': 'fa-heartbeat',
            'internet of things': 'fa-laptop',
            'news': 'fa-newspaper-o',
            'personal': 'fa-male',
            'other': 'fa-search',
            'shopping': 'fa-cart-plus',
            'social': 'fa-thumbs-o-up',
            'travel': 'fa-plane',
            'virtual assistants': 'fa-headphones',
        }
    }
