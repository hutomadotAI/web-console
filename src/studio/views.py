import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.template import loader
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import ListView
from django.views.generic.base import ContextMixin
from django.views.generic.edit import FormView

from studio.forms import (
    AddAIForm,
    ImportAIForm,
    TrainingForm,
    SkillsForm,
    EntityForm
)
from studio.services import get_ai, get_ai_list, get_entities, get_entity, save_entity

logger = logging.getLogger(__name__)


class StudioViewMixin(ContextMixin):
    def get_context_data(self, **kwargs):
        """
        Get AI information for studio navigation and training progress
        """
        context = super(StudioViewMixin, self).get_context_data(**kwargs)

        ai = get_ai(
            self.request.session.get('token', False),
            self.kwargs['aiid']
        )

        template = 'messages/training_status.html'
        message = loader.get_template(template)

        if ai['training']['status'] == 'ai_training_complete':
            level = messages.SUCCESS
        else:
            level = messages.INFO

        messages.add_message(self.request, level,  message.render({
            'ai': ai
        }))

        context['ai'] = ai
        context['api_url'] = settings.API_URL

        return context


@method_decorator(login_required, name='dispatch')
class ProxyAiView(View):
    """Temporary proxy until we open the full API to the world"""

    def get(self, request, aiid, *args, **kwargs):
        return JsonResponse(get_ai(
            self.request.session.get('token', False),
            aiid
        ))


@method_decorator(login_required, name='dispatch')
class AIListView(ListView):
    """
    List of AIs, current homepage
    """
    context_object_name = 'ais'
    template_name = 'ai_list.html'

    def get_queryset(self, **kwargs):
        return get_ai_list(self.request.session.get('token', False))


@method_decorator(login_required, name='dispatch')
class AICreateView(FormView):
    """
    Create a new AI or import one from an export JSON file
    """
    form_class = AddAIForm
    template_name = 'ai_form.html'
    success_url = 'studio:edit_bot'
    fail_url = 'studio:add_bot'

    def get_context_data(self, **kwargs):
        """
        Updates context base on provided data, if there is a form parameter, we
        are dealing with an invalid form and we need to feel the form with
        provided data. If not build new empty form.
        """
        if 'form' in kwargs and isinstance(kwargs['form'], AddAIForm):
            kwargs['add_form'] = kwargs['form']
        if 'form' in kwargs and isinstance(kwargs['form'], ImportAIForm):
            kwargs['import_form'] = kwargs['form']
        if 'add_form' not in kwargs:
            kwargs['add_form'] = AddAIForm()
        if 'import_form' not in kwargs:
            kwargs['import_form'] = ImportAIForm()

        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        """
        Send new AI to API, if successful redirects to second step using AIID
        as a parameter, if not raises a error message and redirect back to the
        form.
        """

        new_ai = form.save(token=self.request.session.get('token', False))

        # Check if save was successful
        if new_ai['status']['code'] not in [200, 201]:
            redirect_url = reverse_lazy(self.fail_url)
            messages.error(self.request, new_ai['status']['info'])
        else:
            redirect_url = reverse_lazy(
                self.success_url,
                kwargs={
                    'aiid': new_ai['aiid']
                }
            )

        return HttpResponseRedirect(redirect_url)

    def post(self, request, *args, **kwargs):
        """
        Determine which form is being submitted if there is a file in request
        it would be an Import form, if not and there is a `name` in POST part
        it's an Add form.
        """

        if request.FILES:
            form_class = ImportAIForm
        elif 'name' in request.POST:
            form_class = AddAIForm

        # get the form
        form = self.get_form(form_class=form_class)

        # validate
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


@method_decorator(login_required, name='dispatch')
class SkillsView(StudioViewMixin, FormView):
    form_class = SkillsForm
    template_name = 'skill_form.html'
    success_url = 'skills'

    def get_form(self, form_class=None):
        """Return an instance of the form to be used in this view."""
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(
            token=self.request.session.get('token', False),
            aiid=self.kwargs['aiid'],
            **self.get_form_kwargs()
        )

    def get_initial(self):
        """Returns the initial data to use for forms on this view."""
        initial = super(SkillsView, self).get_initial()
        ai = get_ai(
            self.request.session.get('token', False),
            self.kwargs['aiid']
        )
        initial = {
            'skills': ai['linked_bots']
        }
        return initial

    def form_valid(self, form):
        """
        Send new AI to API, if successful redirects to second step using AIID
        as a parameter, if not raises a error message and redirect back to the
        form.
        """
        form.save()

        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class TrainingView(StudioViewMixin, FormView):
    form_class = TrainingForm
    template_name = 'training_form.html'
    success_url = 'studio:training'
    fail_url = 'studio:training'

    def form_valid(self, form):
        """
        Send new AI to API, if successful redirects to second step using AIID
        as a parameter, if not raises a error message and redirect back to the
        form.
        """

        ai = form.save(
            token=self.request.session.get('token', False),
            aiid=self.kwargs['aiid'],
            request=self.request
        )

        # Check if save was successful
        if ai['status']['code'] in [200, 201]:
            level = messages.SUCCESS
            url = self.success_url
        else:
            level = messages.ERROR
            url = self.fail_url

        messages.add_message(self.request, level, ai['status']['info'])

        redirect_url = reverse_lazy(
            url,
            kwargs={
                'aiid': self.kwargs['aiid']
            }
        )

        return HttpResponseRedirect(redirect_url)

class EntityListView(ListView):
    """
    List view of bots, filterable by category
    """
    context_object_name = 'entities'
    template_name = 'entity.html'

    def get_context_data(self, **kwargs):

        if 'create_entity_form' not in kwargs:
            kwargs['create_entity_form'] = EntityForm()

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
