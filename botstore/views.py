import logging
import urllib

from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from botstore.services import get_bot, get_bots, get_categories

logger = logging.getLogger(__name__)


class BotDetailView(DetailView):
    """
    Detail view of a particular bot
    """
    context_object_name = 'bot'
    template_name = 'bot_detail.html'

    def get_object(self, **kwargs):
        pk = int(self.kwargs.get('pk', None))
        return get_bot(self.request.user, pk)


class BotListView(ListView):
    """
    List view of bots, filterable by category
    """
    context_object_name = 'bots'
    template_name = 'bot_list.html'

    def get_context_data(self, **kwargs):
        context = super(BotListView, self).get_context_data(**kwargs)
        context['category'] = urllib.parse.unquote(self.kwargs['category'])
        return context

    def get_queryset(self, **kwargs):
        category = self.kwargs['category']
        return get_bots(self.request.user, urllib.parse.unquote(category))


class CategoriesListView(ListView):
    """
    List of categories
    """
    context_object_name = 'categories'
    template_name = 'categorie_list.html'

    def get_queryset(self, **kwargs):
        return get_categories(self.request.user)
