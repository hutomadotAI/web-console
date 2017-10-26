import logging
import urllib

from django.shortcuts import render
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView, View

from entities.services import get_entities, get_entity
from entities.forms import *

logger = logging.getLogger(__name__)


class EntityListView(ListView):
    """
    List view of bots, filterable by category
    """
    context_object_name = 'entities'
    template_name = 'entity.html'

    def get_context_data(self, **kwargs):

        if 'create_entity_form' not in kwargs:
            kwargs['create_entity_form'] = createEntity()

        context = super(EntityListView, self).get_context_data(**kwargs)
        context['token'] = self.request.session.get('token', False)

        return context

    def get_queryset(self):
        entities = [
            {"name": "sys.any", "values": ["value_a", "value_b", "value_c", "value_d"], "is_system": True},
            {"name": "entity_name_2", "values": ["value_e", "value_f", "value_g"], "is_system": False}
        ]
        return entities#get_entities(token=self.request.session.get('token', False))


class NewEntityView(View):
    """
    Create a new Entity.
    """
    context_object_name = 'entity'
    template_name = 'new_entity.html'

    def post(self, request, *args, **kwargs):
        """
        Determine which form is being submitted if there is a file in request
        it would be an Import form, if not and there is a `name` in POST part
        it's an Add form.
        """

        return render(request, template_name='new_entity.html')

    def get_context_data(self, **kwargs):
        context = super(NewEntityView, self).get_context_data(**kwargs)
        context['token'] = self.request.session.get('token', False)
        context['entity_name'] = self.request.POST.get('entity_name', None)

        if context['entity_name'] is None:
            raise Exception('Not getting name properly.')

    def get_queryset(self):
        return get_entity(self.request.POST.get('entity_name', None), token=self.request.session.get('token', False))
