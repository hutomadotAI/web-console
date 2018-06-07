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
    CloneAIForm,
    ConditionsFormset,
    ContextFormset,
    EntityForm,
    EntityFormset,
    ImportAIForm,
    IntentForm,
    ProxyDeleteAIForm,
    ProxyRegenerateWebhookSecretForm,
    SettingsAIForm,
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
    post_chat,
    post_facebook_connect_token,
    post_facebook_customisations,
    post_context_reset,
    post_handover_reset,
)
from studio.decorators import json_login_required

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

        if not context['chatable']:
            messages.info(self.request, _('To start chatting with your bot '
                                          'either upload a training file, add a '
                                          'skill, or add an intent.'))

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


class ProxyAiView(View):
    """Temporary proxy until we open the full API to the world"""

    @method_decorator(json_login_required)
    def get(self, request, aiid, *args, **kwargs):
        ai = get_ai(self.request.session.get('token', False), aiid)

        if ai['training']['status'] == 'error':
            template = loader.get_template('messages/retrain_error.html')
            ai['training']['message'] = template.render({'aiid': aiid})

        return JsonResponse(ai, status=ai['status']['code'])

    @method_decorator(login_required)
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
        bot = get_ai_export(
            self.request.session.get('token', False),
            aiid
        )['bot']
        return JsonResponse(bot, json_dumps_params={'indent': 2})


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
        return get_ai_list(
            self.request.session.get('token', False)
        ).get('ai_list', [])


@method_decorator(login_required, name='dispatch')
class AIDetailView(StudioViewMixin, TemplateView):
    """Summary of an AI"""
    template_name = 'ai_detail.html'


@method_decorator(login_required, name='dispatch')
class AIWizardView(TemplateView):
    """Summary of an AI"""
    template_name = 'ai_wizard.html'


@method_decorator(login_required, name='dispatch')
class AICreateView(FormView):
    """Create a new AI or import one from an export JSON file"""

    form_class = AddAIForm
    template_name = 'ai_add_form.html'
    success_url = 'studio:ai.dashboard'

    def form_valid(self, form):
        """
        Send new AI to API, if successful redirects to second step using AIID
        as a parameter, if not raises a error message and redirect back to the
        form.
        """

        ai = form.save(
            token=self.request.session.get('token', False),
            aiid=self.kwargs.get('aiid', '')
        )

        # Check if save was successful
        if ai['status']['code'] in [200, 201]:
            level = messages.SUCCESS
            redirect_url = HttpResponseRedirect(
                reverse_lazy(
                    self.request.GET.get('next', self.success_url),
                    kwargs={'aiid': ai.get('aiid', self.kwargs.get('aiid'))}
                )
            )
        else:
            level = messages.ERROR
            redirect_url = self.render_to_response(
                self.get_context_data(form=form)
            )

        messages.add_message(self.request, level, ai['status']['info'])

        return redirect_url


@method_decorator(login_required, name='dispatch')
class AICloneView(AICreateView):
    form_class = CloneAIForm

    def get_initial(self, **kwargs):
        # Get AI data
        ai = get_ai(
            self.request.session.get('token', False),
            self.kwargs['aiid']
        )

        ai['name'] = 'Copy of {name}'.format(name=ai['name'])
        ai['default_chat_responses'] = settings.TOKENFIELD_DELIMITER.join(
            ai['default_chat_responses']
        )

        self.initial = ai

        return super(AICloneView, self).get_initial(**kwargs)


@method_decorator(login_required, name='dispatch')
class AIImportView(AICreateView):
    """Create a new AI or import one from an export JSON file"""

    form_class = ImportAIForm
    template_name = 'ai_import_form.html'
    success_url = 'studio:ai.dashboard'


@method_decorator(login_required, name='dispatch')
class AIUpdateView(StudioViewMixin, AICreateView):
    """Manage AI settings"""

    form_class = SettingsAIForm
    template_name = 'settings_form.html'
    success_url = 'studio:settings'

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

        initial['handover_reset_timeout_seconds'] = int(
            initial['handover_reset_timeout_seconds'] / 60
        )
        return initial


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
    formsets = {
        'CONDITIONS': formset_factory(ConditionsFormset, extra=0, can_delete=True),
        'ENTITIES': formset_factory(EntityFormset, extra=0, can_delete=True),
        'CONTEXT_IN': formset_factory(ContextFormset, extra=0, can_delete=True),
        'CONTEXT_OUT': formset_factory(ContextFormset, extra=0, can_delete=True),
    }

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
        context['formsets'] = {
            'conditions': kwargs.get('conditions_formset', self.get_formset(
                prefix='CONDITIONS',
                initial=self.initial.get('conditions_in', []),
            )),
            'entities': kwargs.get('entities', self.get_formset(
                prefix='ENTITIES',
                initial=self.initial.get('variables', []),
                form_kwargs={'entities': entities},
            )),
            'context_in': kwargs.get('entities', self.get_formset(
                prefix='CONTEXT_IN',
                initial=self.initial.get('context_in', [])
            )),
            'context_out': kwargs.get('entities', self.get_formset(
                prefix='CONTEXT_OUT',
                initial=self.initial.get('context_out', [])
            ))

        }

        return context

    def form_valid(self, form, formsets):
        """Try to save Intent, can still not valid"""

        intent = form.save(
            aiid=self.kwargs['aiid'],
            token=self.request.session.get('token', False),
            conditions=formsets['conditions'].cleaned_data,
            entities=formsets['entities'].cleaned_data,
            context_in=formsets['context_in'].cleaned_data,
            context_out=formsets['context_out'].cleaned_data
        )

        # Check if save was successful
        if intent['status']['code'] in [200, 201]:
            level = messages.SUCCESS

            redirect = self.request.GET.get('next', False)

            if redirect:
                messages.add_message(
                    self.request, messages.SUCCESS, _('Intent saved')
                )

                response = HttpResponseRedirect(reverse_lazy(
                    redirect,
                    kwargs={'aiid': self.kwargs['aiid']}
                ))
            else:
                response = HttpResponseRedirect(reverse_lazy(
                    'studio:intents.edit',
                    kwargs={
                        'aiid': self.kwargs['aiid'],
                        'intent_name': intent['cleaned_data']['intent_name']
                    }
                ))

            template = 'messages/retrain.html'
            message = loader.get_template(template)

            messages.add_message(
                self.request, messages.WARNING, message.render({
                    'aiid': self.kwargs['aiid']
                })
            )

        else:
            level = messages.ERROR
            response = self.render_to_response(
                self.get_context_data(form=form)
            )

            messages.add_message(self.request, level, intent['status']['info'])

        return response

    def form_invalid(self, form, formsets):
        """If the form or entities_formset is invalid, render the invalid form."""

        return self.render_to_response(
            self.get_context_data(form=form, formsets=formsets)
        )

    def get_formset(self, **kwargs):
        """Return an instance of the entities_formset to be used in this view."""

        return self.formsets[kwargs.get('prefix')](
            data=self.get_form_kwargs().get('data'),
            **kwargs
        )

    def post(self, request, *args, **kwargs):
        """Custom post for handling both Intent form and Entities entities_formset"""

        # Get entities
        entities = get_entities_list(
            self.request.session.get('token', False)
        ).get('entities')

        form = self.get_form()
        formsets = {
            'conditions': self.get_formset(prefix='CONDITIONS'),
            'entities': self.get_formset(
                prefix='ENTITIES',
                form_kwargs={'entities': entities}
            ),
            'context_in': self.get_formset(prefix='CONTEXT_IN'),
            'context_out': self.get_formset(prefix='CONTEXT_OUT')
        }

        if form.is_valid() and all(formset.is_valid() for key, formset in formsets.items()):
            return self.form_valid(form, formsets)
        else:
            return self.form_invalid(form, formsets)


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
            intent['webhook'] = '' if intent['webhook'] is None else intent['webhook']['endpoint']
            intent['responses'] = settings.TOKENFIELD_DELIMITER.join(
                intent['responses']
            )
            intent['user_says'] = settings.TOKENFIELD_DELIMITER.join(
                intent['user_says']
            )

            intent['context_in'] = [
                {'variable': key, 'value': value} for key, value in intent['context_in'].items()
            ]

            intent['context_out'] = [
                {'variable': key, 'value': value} for key, value in intent['context_out'].items()
            ]

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


@method_decorator(json_login_required, name='dispatch')
class ProxyHandoverResetView(View):
    """Reset handover to human state"""

    def post(self, request, aiid, *args, **kwargs):

        response = post_handover_reset(
            self.request.session.get('token', False),
            aiid,
            chatId=json.loads(request.body).get('chatId', '')
        )
        return JsonResponse(response, status=response['status']['code'])


@method_decorator(json_login_required, name='dispatch')
class ProxyContextResetView(View):
    """Reset handover to human state"""

    def post(self, request, aiid, *args, **kwargs):

        response = post_context_reset(
            self.request.session.get('token', False),
            aiid,
            chatId=json.loads(request.body).get('chatId', '')
        )
        return JsonResponse(response, status=response['status']['code'])


@method_decorator(json_login_required, name='dispatch')
class ProxyChatView(View):
    """Send chat message"""

    def post(self, request, aiid, *args, **kwargs):
        response = post_chat(
            self.request.session.get('token', False),
            aiid,
            payload=json.loads(request.body)
        )
        return JsonResponse(response, status=response['status']['code'])
