from django.views.generic import ListView
from django.views.generic.edit import CreateView

from studio.models import Ai


class AiList(ListView):
    queryset = Ai.objects.order_by('created_on')


class AiCreate(CreateView):
    model = Ai
    fields = [
        'ai_name',
        'ai_description',
        'ui_ai_voice',
        'ui_ai_timezone',
    ]
    template_name = 'ai_form.html'
