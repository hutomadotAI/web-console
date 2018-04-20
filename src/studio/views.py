import json
import logging

import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.forms import formset_factory
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.shortcuts import redirect
from django.template import loader
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views import View
from django.views.generic import ListView
from django.views.generic.base import ContextMixin, TemplateView, RedirectView
from django.views.generic.edit import FormView

from studio.forms import (
    AddAIForm,
    ImportAIForm,
    IntentForm,
    EntityForm,
    EntityFormset,
    ProxyDeleteAIForm,
    ProxyRegenerateWebhookSecretForm,
    SkillsForm,
    TrainingForm,
)
from studio.services import (
    delete_entity,
    delete_intent,
    put_facebook_action,
    get_ai,
    get_ai_details,
    get_ai_export,
    get_ai_list,
    get_ai_training,
    get_entities_list,
    get_entity,
    get_facebook_connect_state,
    get_facebook_customisations,
    get_insights_chart,
    get_insights_chatlogs,
    get_intent,
    get_intent_list,
    post_regenerate_webhook_secret,
    put_training_start,
    put_training_update,
    post_facebook_connect_token,
    post_facebook_customisations,
)

logger = logging.getLogger(__name__)


class StudioViewMixin(ContextMixin):

    chatable = True

    def get_context_data(self, **kwargs):
        """Get AI information for studio navigation and training progress"""

        context = super(StudioViewMixin, self).get_context_data(**kwargs)
        context['ai'] = get_ai(
            self.request.session.get('token', False),
            self.kwargs['aiid']
        )
        context['ai_details'] = get_ai_details(
            self.request.session.get('token', False),
            self.kwargs['aiid']
        )
        context['chatable'] = bool(
            context['ai_details']['training_file'] or
            context['ai_details']['skills'] or
            context['ai_details']['intents']
        )
        context['api_url'] = settings.PUBLIC_API_URL

        if not context['chatable']:
            messages.info(self.request, _('To start chatting with your bot either upload a training file, add a skill, or add an intent.'))

        return context


@method_decorator(login_required, name='dispatch')
class IntegrationView(StudioViewMixin, TemplateView):
    template_name = 'integration.html'

    def get_context_data(self, **kwargs):
        context = super(IntegrationView, self).get_context_data(**kwargs)

        context['chatable'] = False

        token = self.request.session.get('token', False)
        aiid = self.kwargs['aiid']

        context['integration'] = get_facebook_connect_state(token, aiid)

        if context['integration'].get('page_integrated_id'):
            context['customisations'] = get_facebook_customisations(token, aiid)

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
        ai = get_ai(self.request.session.get('token', False), aiid)

        return JsonResponse(ai, status=ai['status']['code'])

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
class IntentDeleteView(View):
    """Removes an Intent, if successful prompt user to retrain AI"""

    def post(self, request, aiid, intent_name, *args, **kwargs):
        redirect_url = reverse_lazy('studio:intents', kwargs={'aiid': aiid})

        deleted_intent = delete_intent(
            self.request.session.get('token', False),
            aiid,
            intent_name
        )

        if deleted_intent['status']['code'] in [200, 201]:
            level = messages.WARNING
            template = 'messages/retrain.html'
            message_template = loader.get_template(template)
            message = message_template.render({'aiid': aiid})

        else:
            level = messages.ERROR
            message = deleted_intent['status']['info']

        messages.add_message(self.request, level, message)

        return HttpResponseRedirect(redirect_url)


@method_decorator(login_required, name='dispatch')
class EntityDeleteView(RedirectView):
    """Removes an Entity"""

    def post(self, request, aiid, entity_name, *args, **kwargs):
        redirect_url = reverse_lazy('studio:entities', kwargs={'aiid': aiid})

        deleted_intent = delete_entity(
            self.request.session.get('token', False),
            entity_name
        )

        if deleted_intent['status']['code'] in [200, 201]:
            level = messages.SUCCESS
            message = _('Entity removed')
        else:
            level = messages.ERROR
            message = deleted_intent['status']['info']

        messages.add_message(self.request, level, message)

        return HttpResponseRedirect(redirect_url)


@method_decorator(login_required, name='dispatch')
class AIListView(ListView):
    """List of AIs, current homepage"""

    context_object_name = 'ais'
    template_name = 'ai_list.html'

    def get_queryset(self, **kwargs):
        try:
            ai_list = get_ai_list(
                self.request.session.get('token', False)
            ).get('ai_list')
        except Exception as e:
            ai_list = []

        return ai_list


@method_decorator(login_required, name='dispatch')
class AIDetailView(StudioViewMixin, TemplateView):
    """Summary of an AI"""

    template_name = 'ai_detail.html'


@method_decorator(login_required, name='dispatch')
class AICreateView(FormView):
    """Create a new AI or import one from an export JSON file"""

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
            level = messages.SUCCESS
            redirect_url = reverse_lazy(
                self.success_url,
                kwargs={'aiid': new_ai['aiid']}
            )
        else:
            level = messages.ERROR
            redirect_url = reverse_lazy(self.fail_url)

        messages.add_message(self.request, level, new_ai['status']['info'])

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
    """Manage AI settings"""

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
class EntitiesView(StudioViewMixin, FormView):
    """Manage AI Entities"""

    form_class = EntityForm
    template_name = 'entity_form.html'
    success_url = 'studio:entities.edit'

    def get_context_data(self, **kwargs):
        """Update context with Entities list"""

        context = super(EntitiesView, self).get_context_data(**kwargs)

        # Get entities
        context['entities'] = get_entities_list(
            self.request.session.get('token', False)
        ).get('entities')

        return context

    def form_valid(self, form):
        """Try to save Entity, can still be invalid"""

        entity = form.save(
            token=self.request.session.get('token', False),
            **self.kwargs
        )

        # Check if save was successful
        if entity['status']['code'] in [200, 201]:
            level = messages.SUCCESS

            redirect_url = HttpResponseRedirect(
                reverse_lazy(
                    self.success_url,
                    kwargs={
                        'aiid': self.kwargs['aiid'],
                        'entity_name': form.cleaned_data['entity_name']
                    }
                )
            )

        else:
            level = messages.ERROR
            redirect_url = self.render_to_response(
                self.get_context_data(form=form)
            )

        messages.add_message(self.request, level, entity['status']['info'])

        return redirect_url


@method_decorator(login_required, name='dispatch')
class EntitiesUpdateView(EntitiesView):
    """Single Entity view"""

    def get_initial(self, **kwargs):
        """Get and prepare Entity data"""

        # Get an entity
        intent = get_entity(
            self.request.session.get('token', False),
            self.kwargs['entity_name']
        )

        # Prepare data for the form
        # TODO: should be a better way to do it in the form itself?
        intent['entity_values'] = settings.TOKENFIELD_DELIMITER.join(
            intent['entity_values']
        )

        self.initial = intent

        return super(EntitiesUpdateView, self).get_initial(**kwargs)

    def get_context_data(self, **kwargs):
        """Provide entity name for the template"""

        context = super(EntitiesUpdateView, self).get_context_data(**kwargs)
        context['entity_name'] = self.initial['entity_name']

        return context


@method_decorator(login_required, name='dispatch')
class IntentsView(StudioViewMixin, ListView):
    """List of AIs, current homepage"""
    context_object_name = 'intents'
    template_name = 'intents_list.html'

    def get_queryset(self, **kwargs):
        intents = get_intent_list(
            self.request.session.get('token', False),
            self.kwargs['aiid']
        ).get('intents')

        if not intents:
            self.template_name = 'intents_empty.html'

        return intents


@method_decorator(login_required, name='dispatch')
class IntentsEditView(StudioViewMixin, FormView):
    """Manage AI Intents and theirs relations with Entities"""

    form_class = IntentForm
    template_name = 'intent_form.html'
    formset = formset_factory(EntityFormset, extra=0, can_delete=True)
    formset_prefix = 'entities'

    def get_context_data(self, **kwargs):
        """Update context with Intents list and Entities formset"""

        context = super(IntentsEditView, self).get_context_data(**kwargs)

        # Get entities
        entities = get_entities_list(
            self.request.session.get('token', False)
        ).get('entities')

        # Custom entities goes first, sort alphabetically
        entities.sort(key=lambda entity: (
            entity['is_system'],
            entity['entity_name']
        ))

        # And pass it to formset initial choice
        # TODO: Change initial to entities after we refactor Intent API code
        context['formset'] = kwargs.get('formset', self.get_formset(
            initial=self.initial.get('variables', []),
            form_kwargs={'entities': entities},
        ))

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

            logger.warn(intent)

            redirect_url = HttpResponseRedirect(
                reverse_lazy(
                    'studio:intents.edit',
                    kwargs={
                        'aiid': self.kwargs['aiid'],
                        'intent_name': intent['cleaned_data']['intent_name']
                    }
                )
            )

            template = 'messages/retrain.html'
            message = loader.get_template(template)

            messages.add_message(
                self.request, messages.WARNING, message.render({
                    'aiid': self.kwargs['aiid']
                })
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
class IntentsUpdateView(IntentsEditView):
    """Single Intent view"""

    success_url = 'studio:intents.edit'

    def get_initial(self, **kwargs):
        """Get and prepare Intent data"""

        if not self.initial:
            # Get an intent if not prepared yet (get_form_kwargs) is calling
            # get_initial  we don't want to run it multiple times
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
        """Save skills attached to a bot"""
        skills = form.save()

        if skills['status']['code'] in [200, 201]:
            level = messages.SUCCESS
            skills['status']['info'] = _('Skills updated')
        else:
            level = messages.ERROR

        messages.add_message(self.request, level, skills['status']['info'])

        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class TrainingView(StudioViewMixin, FormView):
    form_class = TrainingForm
    template_name = 'training_form.html'
    success_url = 'studio:training'
    fail_url = 'studio:training'

    def get_initial(self, **kwargs):
        """Get and prepare Intent data"""

        training = get_ai_training(
            self.request.session.get('token', False),
            self.kwargs['aiid']
        )

        self.initial = {
            'training_data': training.get('trainingFile', '')
        }

        return super(TrainingView, self).get_initial(**kwargs)

    def form_valid(self, form):

        training = form.save(
            token=self.request.session.get('token', False),
            aiid=self.kwargs['aiid']
        )

        # Check if save was successful
        if training['status']['code'] in [200, 201]:
            level = messages.SUCCESS
            url = self.success_url
        else:
            level = messages.ERROR
            url = self.fail_url

        messages.add_message(self.request, level, training['status']['info'])

        redirect_url = reverse_lazy(
            url,
            kwargs={
                'aiid': self.kwargs['aiid']
            }
        )

        return HttpResponseRedirect(redirect_url)


@method_decorator(login_required, name='dispatch')
class RetrainView(RedirectView):
    """
    Restart bot training and get back to where you came from, if we don't
    know that to studio summary
    """

    permanent = False
    query_string = True
    pattern_name = 'studio:edit_bot'

    def get_redirect_url(self, *args, **kwargs):

        training = put_training_update(
            self.request.session.get('token'),
            kwargs['aiid']
        )

        # Start training if succesfully  updated
        if training['status']['code'] in [200, 201]:
            training = put_training_start(
                self.request.session.get('token'),
                kwargs['aiid']
            )

        if training['status']['code'] in [200, 201]:
            level = messages.SUCCESS
        else:
            level = messages.ERROR

        messages.add_message(self.request, level, training['status']['info'])

        return self.request.META.get(
            'HTTP_REFERER',
            super(RetrainView, self).get_redirect_url(*args, **kwargs)
        )


@method_decorator(login_required, name='dispatch')
class InsightsView(StudioViewMixin, TemplateView):
    template_name = 'insights.html'

    def get_context_data(self, **kwargs):
        context = super(InsightsView, self).get_context_data(**kwargs)

        # hard code dates to 30 day window
        today = datetime.date.today()
        context['to_date'] = today.isoformat()
        context['from_date'] = (
            datetime.date.today() - datetime.timedelta(days=30)
        ).isoformat()

        context['chatable'] = False

        # generate date range description
        context['date_interval'] = 'from {from_date} to {to_date}'.format(**context)

        return context


@method_decorator(login_required, name='dispatch')
class OAuthView(RedirectView):
    """Handle OAuth redirecting to State next view"""

    def get_redirect_url(self):
        state = json.loads(self.request.GET.get('state', {}))

        return reverse_lazy(
            state.pop('next'), kwargs=state
        ) + '?' + self.request.GET.urlencode()


@method_decorator(login_required, name='dispatch')
class FacebookActionView(RedirectView):
    """Handle Facebook connect, disconnect and attach page actions"""

    def get(self, request, aiid, action, *args, **kwargs):
        # Perform action

        if action == 'connect':
            results = post_facebook_connect_token(
                self.request.session.get('token', False),
                aiid,
                payload={
                    'connect_token': self.request.GET.get('code'),
                    'redirect_uri': self.request.build_absolute_uri('/oauth')
                }
            )
        else:
            results = put_facebook_action(
                self.request.session.get('token', False),
                aiid,
                {
                    'action': action,
                    'id': self.request.GET.get('id')
                }
            )

        # Provide user feedback and redirect to integrations tab
        if results['status']['code'] == 200:
            level = messages.SUCCESS
        else:
            level = messages.ERROR

        messages.add_message(self.request, level, results['status']['info'])

        return HttpResponseRedirect(
            reverse_lazy('studio:integrations', kwargs={'aiid': aiid})
        )


@method_decorator(login_required, name='dispatch')
class FacebookCustomiseView(View):
    """
    FB Integration customisations save handler
    """

    def post(self, request, aiid, *args, **kwargs):
        token = request.session.get('token', False)
        # pull the data from the json payload
        payload = json.loads(request.body)
        # call the API
        result = post_facebook_customisations(
            token,
            aiid,
            payload=payload
        )
        # return an error unless we got a 200 in JSON from the API
        if bool(result and result.get('status')):
            return HttpResponse(status=result['status']['code'])

        return HttpResponse(status=400)


@method_decorator(login_required, name='dispatch')
class ProxyInsightsLogsView(View):
    """Get logs from the api and relay them as an attachment"""

    def post(self, request, aiid, *args, **kwargs):

        # get date params from the request body
        fromDate = request.POST.get('from', '')
        toDate = request.POST.get('to', '')

        logs = get_insights_chatlogs(
            self.request.session.get('token', False),
            aiid,
            fromDate,
            toDate
        )

        response = HttpResponse(logs, content_type='application/csv')
        response['Content-Disposition'] = 'attachment; filename="chatlogs.csv"'
        return response


@method_decorator(login_required, name='dispatch')
class ProxyInsightsChartView(View):
    """Get chart data from the api and relay json content directly"""

    def get(self, request, aiid, metric, *args, **kwargs):
        token = self.request.session.get('token', False)

        # hard code dates to a 30 day window
        today = datetime.date.today()
        toDate = today.isoformat()
        fromDate = (
            datetime.date.today() - datetime.timedelta(days=30)
        ).isoformat()

        # relay request to the api
        response = get_insights_chart(token, aiid, metric, fromDate, toDate)

        return JsonResponse(response)
