import logging
import urllib

from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from entities.services import get_entities, get_entity

logger = logging.getLogger(__name__)


class EntityListView(ListView):
    """
    List view of bots, filterable by category
    """
    context_object_name = 'entities'
    template_name = 'entity.html'

    def get_context_data(self, **kwargs):
        context = super(EntityListView, self).get_context_data(**kwargs)
        context['token'] = self.request.session.get('token', False)

        return context

    def get_queryset(self):
        return get_entities(token=self.request.session.get('token', False))
