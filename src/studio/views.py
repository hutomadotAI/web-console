import logging
import requests

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.forms import formset_factory
from django.http import HttpResponseRedirect, JsonResponse
from django.template import loader
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import ListView
from django.views.generic.base import ContextMixin
from django.views.generic.edit import FormView

from studio.forms import (
    AddAIForm,
    ImportAIForm,
    IntentForm,
    EntityForm,
    ProxyDeleteAIForm,
    ProxyRegenerateWebhookSecretForm,
    SkillsForm,
    TrainingForm,
)
from studio.services import (
    get_ai,
    delete_ai,
    get_ai_export,
    get_intent_list,
    get_entities_list,
    get_intent,
    post_intent,
    delete_intent,
    get_ai_list,
    post_regenerate_webhook_secret,
)

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

        if ai['training']['status'] == 'completed':
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
class ProxyRegenerateWebhookSecretView(View):
    """Temporary proxy until we open the full API to the world"""

    def post(self, request, aiid, *args, **kwargs):
        """We use forms to secure POST requests"""
        form = ProxyRegenerateWebhookSecretForm(request.POST)

        if form.is_valid():
            return JsonResponse(post_regenerate_webhook_secret(
                self.request.session.get('token', False),
                aiid
            ))
        else:
            level = messages.ERROR
            message = 'Something went wrong'

            messages.add_message(self.request, level, message)
            return redirect('studio:summary')


@method_decorator(login_required, name='dispatch')
class ProxyAiView(View):
    """Temporary proxy until we open the full API to the world"""

    def get(self, request, aiid, *args, **kwargs):
        return JsonResponse(get_ai(
            self.request.session.get('token', False),
            aiid
        ))

    def post(self, request, aiid, *args, **kwargs):
        """We use forms to secure POST requests"""
        form = ProxyDeleteAIForm(request.POST)

        if form.is_valid():
            status = form.save(
                token=self.request.session.get('token', False)
            )

            message = status['status']['info']

            if status['status']['code'] in [200, 201]:
                level = messages.SUCCESS
            else:
                level = messages.ERROR
        else:
            level = messages.ERROR
            message = 'Something went wrong'

        messages.add_message(self.request, level, message)
        return redirect('studio:summary')


@method_decorator(login_required, name='dispatch')
class ProxyAiExportView(View):
    """Temporary proxy until we open the full API to the world"""

    def get(self, request, aiid, *args, **kwargs):
        return JsonResponse(get_ai_export(
            self.request.session.get('token', False),
            aiid
        )['bot'])


@method_decorator(login_required, name='dispatch')
class ProxyIntentDeleteView(View):
    """Temporary proxy until we open the full API to the world"""

    def delete(self, request, aiid, *args, **kwargs):
        intent_name = request.GET.get('intent_name')

        return JsonResponse(delete_intent(
            self.request.session.get('token', False),
            aiid,
            intent_name
        ))


@method_decorator(login_required, name='dispatch')
class AIListView(ListView):
    """List of AIs, current homepage"""

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
            # We must enter a name
            del kwargs['add_form'].fields['name'].widget.attrs['readonly']
            # We must enter a name
            del kwargs['add_form'].fields['aiid']
            del kwargs['add_form'].fields['default_chat_responses']
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
        if new_ai['status']['code'] in [200, 201]:
            redirect_url = reverse_lazy(
                self.success_url,
                kwargs={'aiid': new_ai['aiid']}
            )
        else:
            redirect_url = reverse_lazy(self.fail_url)
            messages.error(self.request, new_ai['status']['info'])

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
class AIUpdateView(StudioViewMixin, FormView):
    """
    Create a new AI or import one from an export JSON file
    """
    form_class = AddAIForm
    template_name = 'settings_form.html'
    success_url = 'studio:settings'
    fail_url = 'studio:settings'

    def get_initial(self):
        """Returns the initial data to use for forms on this view."""

        initial = super(AIUpdateView, self).get_initial()
        initial = get_ai(
            self.request.session.get('token', False),
            self.kwargs['aiid']
        )
        initial['default_chat_responses'] = settings.TOKENFIELD_DELIMITER.join(
            initial['default_chat_responses']
        )
        return initial

    def form_valid(self, form):
        """Update an AI"""

        ai = form.save(
            aiid=self.kwargs['aiid'],
            token=self.request.session.get('token', False)
        )

        # Check if save was successful
        if ai['status']['code'] not in [200, 201]:
            url = self.fail_url
            level = messages.ERROR
        else:
            url = self.success_url
            level = messages.SUCCESS

        redirect_url = reverse_lazy(
            url,
            kwargs={
                'aiid': self.kwargs['aiid']
            }
        )
        messages.add_message(self.request, level, ai['status']['info'])

        return HttpResponseRedirect(redirect_url)


@method_decorator(login_required, name='dispatch')
class IntentsView(StudioViewMixin, FormView):
    """Manage AI Intents and theirs relations with Entities"""

    form_class = IntentForm
    template_name = 'intent_form.html'
    success_url = 'studio:intents'
    fail_url = 'studio:intents'
    formset = formset_factory(EntityForm, extra=0, can_delete=True)
    formset_prefix = 'entities'

    def get_context_data(self, **kwargs):
        """Update context with Intents list and Entities formset"""

        context = super(IntentsView, self).get_context_data(**kwargs)

        # Get entities
        entities = get_entities_list(
            self.request.session.get('token', False)
        ).get('entities')

        # And pass it to formset initial choice
        # TODO: Change initial to entities after we refactor Intent API code
        context['formset'] = kwargs.get('formset', self.get_formset(
            initial=self.initial.get('variables', []),
            form_kwargs={'entities': entities},
        ))

        context['intents'] = get_intent_list(
            self.request.session.get('token', False),
            self.kwargs['aiid']
        )

        return context

    def form_valid(self, form, formset):
        """Try to save Intent, can still not valid"""

        intent = form.save(
            aiid=self.kwargs['aiid'],
            token=self.request.session.get('token', False),
            variables=formset.cleaned_data
        )

        # Check if save was successful
        if intent['status']['code'] in [200, 201]:
            level = messages.SUCCESS

            redirect_url = HttpResponseRedirect(
                reverse_lazy(
                    self.success_url,
                    kwargs={**self.kwargs}
                )
            )
        else:
            level = messages.ERROR
            redirect_url = self.render_to_response(
                self.get_context_data(form=form)
            )

        messages.add_message(self.request, level, intent['status']['info'])

        return redirect_url

    def form_invalid(self, form, formset):
        """If the form or formset is invalid, render the invalid form."""

        return self.render_to_response(
            self.get_context_data(form=form, formset=formset)
        )

    def get_formset(self, **kwargs):
        """Return an instance of the formset to be used in this view."""

        return self.formset(
            data=self.get_form_kwargs().get('data'),
            prefix=self.formset_prefix,
            **kwargs
        )

    def post(self, request, *args, **kwargs):
        """Custom post for handling both Intent form and Entities formset"""

        # Get entities
        entities = get_entities_list(
            self.request.session.get('token', False)
        ).get('entities')

        form = self.get_form()
        formset = self.get_formset(
            form_kwargs={'entities': entities}
        )

        if form.is_valid() and formset.is_valid():
            return self.form_valid(form, formset)
        else:
            return self.form_invalid(form, formset)


@method_decorator(login_required, name='dispatch')
class IntentsUpdateView(IntentsView):
    """Single Intent view"""

    success_url = 'studio:intents.edit'

    def get_initial(self, **kwargs):
        """Get and prepare Intent data"""

        # Get an intent
        intent = get_intent(
            self.request.session.get('token', False),
            self.kwargs['aiid'],
            self.kwargs['intent_name']
        )

        # Prepare data for the form
        # TODO: should be a better way to do it in the form itself?
        intent['webhook'] = intent['webhook']['endpoint']
        intent['responses'] = settings.TOKENFIELD_DELIMITER.join(
            intent['responses']
        )
        intent['user_says'] = settings.TOKENFIELD_DELIMITER.join(
            intent['user_says']
        )
        for entity in intent['variables']:
            entity['prompts'] = settings.TOKENFIELD_DELIMITER.join(
                entity['prompts']
            )

        self.initial = intent

        return super(IntentsUpdateView, self).get_initial(**kwargs)

    def get_context_data(self, **kwargs):
        """Provide intent name for the template"""

        context = super(IntentsUpdateView, self).get_context_data(**kwargs)
        context['intent_name'] = self.initial['intent_name']

        return context


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
