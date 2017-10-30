import logging
import urllib

from django.shortcuts import render
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView, View

from entities.services import get_entities, get_entity, save_entity
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
        return get_entities(token=self.request.session.get('token', False))


class NewEntityView(View):
    """
    Create a new Entity.
    """
    context_object_name = 'entity'
    template_name = 'entityelement.html'

    def __init__(self):
        self.context = None

    def post(self, request, *args, **kwargs):
        """
        Determine which form is being submitted if there is a file in request
        it would be an Import form, if not and there is a `name` in POST part
        it's an Add form.
        """
        context = {}
        token = request.session.get('token', False)
        name = request.POST.get('entity_name')
        values = request.POST.getlist('value-entity-row')

        if len(values) > 0:
            context['entity_name'] = name
            context['values'] = values
            save_entity(name, values, token=token)
        else:
            entity = get_entity(name, token=token)
            context['entity_name'] = name
            context['values'] = entity['entity_values']

        return render(request, 'entityelement.html', context)

    def get_context_data(self, **kwargs):
        self.context = super(NewEntityView, self).get_context_data(**kwargs)
        self.context['token'] = self.request.session.get('token', False)
        self.context['entity_name'] = self.request.POST.get('entity_name', None)

        if self.context['entity_name'] is None:
            raise Exception('Not getting name properly.')

    def get_queryset(self):
        return get_entity(self.request.POST.get('entity_name', None), token=self.request.session.get('token', False))
