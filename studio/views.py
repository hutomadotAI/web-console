from django.views.generic import ListView
from django.views.generic.edit import CreateView

from studio.models import Ai
from studio.services import get_ai_list

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


@method_decorator(login_required, name='dispatch')
class AIListView(ListView):
    """
    List of AIs, current homepage
    """
    context_object_name = 'ais'
    template_name = 'ai_list.html'

    def get_queryset(self, **kwargs):
        return get_ai_list(self.request.user)


@method_decorator(login_required, name='dispatch')
class AICreateView(CreateView):
    """
    Creat a new AI
    """
    model = Ai
    fields = [
        'ai_name',
        'ai_description',
        'ui_ai_voice',
        'ui_ai_timezone',
    ]
    template_name = 'ai_form.html'
