import logging

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from django.views.generic.edit import CreateView, FormView
from django.urls import reverse_lazy
from django.contrib import messages

from studio.forms import AddAI, ImportAI
from studio.services import get_ai_list, post_ai

logger = logging.getLogger(__name__)


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
    form_class = AddAI
    template_name = 'ai_form.html'
    success_url = 'studio:edit_bot'
    fail_url = 'studio:add_bot'

    def get_context_data(self, **kwargs):
        """
        Updates context base on provided data, if there is a form parameter, we
        are dealing with an invalid form and we need to feel the form with
        provided data. If not build new empty form.
        """
        if 'form' in kwargs and isinstance(kwargs['form'], AddAI):
            kwargs['add_form'] = kwargs['form']
        if 'form' in kwargs and isinstance(kwargs['form'], ImportAI):
            kwargs['import_form'] = kwargs['form']
        if 'add_form' not in kwargs:
            kwargs['add_form'] = AddAI()
        if 'import_form' not in kwargs:
            kwargs['import_form'] = ImportAI()

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
            form_class = ImportAI
        elif 'name' in request.POST:
            form_class = AddAI

        # get the form
        form = self.get_form(form_class=form_class)

        # validate
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)
