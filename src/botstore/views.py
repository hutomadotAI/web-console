import logging
import urllib

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views.generic.base import RedirectView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView
from django.views.generic.list import ListView

from botstore.services import get_bot, get_bots, get_categories, post_purchase
from botstore.forms import PublishForm

from studio.services import get_ai

from users.decorators import has_info
from users.forms import DeveloperInfoForm
from users.services import get_info

logger = logging.getLogger(__name__)


@method_decorator(login_required, name='dispatch')
class PurchaseView(RedirectView):
    """Purchase a bot"""
    permanent = False
    query_string = True
    pattern_name = 'botstore:detail'

    def get_redirect_url(self, *args, **kwargs):

        purchased = post_purchase(
            self.request.session.get('token'),
            kwargs['bot_id']
        )

        # Check if save was successful
        if purchased['status']['code'] in [200, 201]:
            level = messages.SUCCESS
            message = _('Skill successfully added! You can now add this skill to your bots.')
        else:
            level = messages.ERROR
            message = purchased['status']['info']

        messages.add_message(self.request, level, message)

        return super(PurchaseView, self).get_redirect_url(*args, **kwargs)


@method_decorator(login_required, name='dispatch')
@method_decorator(has_info, name='dispatch')
class PublishView(FormView):
    """Publish a bot"""
    form_class = PublishForm
    template_name = 'publish_form.html'
    success_url = 'studio:summary'

    def get_context_data(self, **kwargs):
        """Get developer info initial data"""

        dev_info = get_info(
            token=self.request.session.get('token'),
            dev_id=self.request.session.get('dev_id')
        )

        kwargs['info_form'] = DeveloperInfoForm(initial=dev_info['info'])

        for name, field in kwargs['info_form'].fields.items():
            field.disabled = True
            field.widget.attrs['readonly'] = True

        return super().get_context_data(**kwargs)

    def get_initial(self):
        """Returns the initial data to use for forms on this view."""

        initial = super(PublishView, self).get_initial()
        initial = get_ai(
            self.request.session.get('token', False),
            self.kwargs['aiid']
        )
        return initial

    def form_valid(self, form):

        published = form.save(
            aiid=self.kwargs['aiid'],
            token=self.request.session.get('token', False)
        )

        # Check if save was successful
        if published['status']['code'] in [200, 201]:
            level = messages.SUCCESS
            redirect_url = HttpResponseRedirect(reverse_lazy(self.success_url))
        else:
            level = messages.ERROR
            redirect_url = self.render_to_response(
                self.get_context_data(form=form)
            )

        messages.add_message(self.request, level, published['status']['info'])

        return redirect_url


class BotDetailView(DetailView):
    """Detail view of a particular bot"""
    context_object_name = 'bot'
    template_name = 'bot_detail.html'

    def get_object(self, **kwargs):
        pk = self.kwargs.get('bot_id', None)
        return get_bot(
            pk, self.request.session.get('token', False)
        ).get('item')


class BotListView(ListView):
    """List view of bots, filterable by category"""
    context_object_name = 'bots'
    template_name = 'bot_list.html'

    def get_context_data(self, **kwargs):
        context = super(BotListView, self).get_context_data(**kwargs)
        context['category'] = urllib.parse.unquote(self.kwargs['category'])
        context['token'] = self.request.session.get('token', False)

        return context

    def get_queryset(self, **kwargs):
        category = self.kwargs['category']
        return get_bots(
            token=self.request.session.get('token', False),
            category=urllib.parse.unquote(category)
        ).get('items')


class CategoriesListView(ListView):
    """List of categories"""
    context_object_name = 'categories'
    template_name = 'categorie_list.html'

    def get_queryset(self, **kwargs):
        return get_categories(
            self.request.session.get('token', False)
        ).get('categories')
