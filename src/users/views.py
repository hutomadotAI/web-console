import logging

from allauth.account.views import PasswordChangeView

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic.edit import FormView

from users.forms import DeveloperInfoForm

logger = logging.getLogger(__name__)


@method_decorator(login_required, name='dispatch')
class PasswordChangeView(PasswordChangeView):
    """Custom class to override the password change view, redirect o homepage"""
    success_url = '/'


@method_decorator(login_required, name='dispatch')
class DeveloperInfoView(FormView):
    """Publish a bot"""

    form_class = DeveloperInfoForm
    template_name = 'info_form.html'

    def get_context_data(self, **kwargs):
        kwargs['next'] = self.request.GET.get('next')

        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        """Submit developer info and redirect to success URL"""

        info = form.save(
            token=self.request.session.get('token'),
            dev_id=self.request.session.get('dev_id')
        )

        # Check if save was successful
        if info['status']['code'] in [200, 201]:
            level = messages.SUCCESS

            if self.request.GET['next']:
                redirect_url = HttpResponseRedirect(self.request.GET['next'])
            else:
                redirect_url = HttpResponseRedirect(
                    reverse_lazy(self.success_url)
                )
        else:
            level = messages.ERROR
            redirect_url = self.render_to_response(
                self.get_context_data(form=form)
            )

        messages.add_message(self.request, level, info['status']['info'])

        return redirect_url
