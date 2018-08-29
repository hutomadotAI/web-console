"""
    console top URL Configuration

    The `urlpatterns` list routes URLs to views. For more information please see:
        https://docs.djangoproject.com/en/1.11/topics/http/urls/

    Examples:

    Function views
        1. Add an import:  from studio import views
        2. Add a URL to urlpatterns:  url('', views.home, name='home')

    Class-based views
        1. Add an import:  from studio.views import Home
        2. Add a URL to urlpatterns:  url('', Home.as_view(), name='home')

    Including another URLconf
        1. Import the include() function: from django.conf.urls import url, include
        2. Add a URL to urlpatterns:  url('blog/', include('blog.urls'))
"""

from django.urls import path, re_path

from django.views.generic.base import RedirectView
from studio.views import (
    AICloneView,
    AICreateView,
    AIDetailView,
    AIImportView,
    AIReImportView,
    AIListView,
    AIUpdateView,
    AIWizardView,
    EntitiesUpdateView,
    EntitiesView,
    EntityDeleteView,
    FacebookActionView,
    FacebookCustomiseView,
    InsightsView,
    IntegrationView,
    IntentDeleteView,
    IntentsBulkUploadView,
    IntentsEditView,
    IntentsUpdateView,
    IntentsView,
    OAuthView,
    ProxyAiExportView,
    ProxyAiView,
    ProxyChatView,
    ProxyContextResetView,
    ProxyHandoverResetView,
    ProxyInsightsChartView,
    ProxyInsightsLogsView,
    ProxyRegenerateWebhookSecretView,
    RetrainView,
    SkillsView,
    TemplateCloneView,
    TemplateGetView,
    TrainingView,
)

app_name = 'studio'

urlpatterns = [

    # Always use a path, explicit is better than implicit
    path(
        '',
        RedirectView.as_view(pattern_name='studio:summary'),
        name='index'
    ),

    # Summary page of studio app
    path(
        'summary',
        AIListView.as_view(),
        name='summary'
    ),

    # AI wizard view
    path(
        'bots/wizard',
        AIWizardView.as_view(),
        name='ai.wizard'
    ),

    # Create a new AI
    path(
        'bots/add',
        AICreateView.as_view(),
        name='ai.add'
    ),

    # Clone a bot
    path(
        'bots/clone/<uuid:aiid>',
        AICloneView.as_view(),
        name='ai.clone'
    ),

    # Import a new AI
    path(
        'bots/import',
        AIImportView.as_view(),
        name='ai.import'
    ),

    # Edit an existing AI
    path(
        'bots/edit/<uuid:aiid>',
        AIDetailView.as_view(),
        name='edit_bot'
    ),

    # Edit an existing AI
    path(
        'bots/dashboard/<uuid:aiid>',
        AIDetailView.as_view(),
        name='ai.dashboard'
    ),

    # Update training of an existing AI
    path(
        'bots/edit/<uuid:aiid>/training',
        TrainingView.as_view(),
        name='training'
    ),

    # Restart training of an AI
    path(
        'bots/edit/<uuid:aiid>/retrain',
        RetrainView.as_view(),
        name='retrain'
    ),

    # Update skills of an existing AI
    path(
        'bots/edit/<uuid:aiid>/skills',
        SkillsView.as_view(),
        name='skills'
    ),

    # Update entities of an existing AI
    path(
        'bots/edit/<uuid:aiid>/entities',
        EntitiesView.as_view(),
        name='entities'
    ),

    # Update an Entity of an existing AI
    path(
        'bots/edit/<uuid:aiid>/entities/<slug:entity_name>',
        EntitiesUpdateView.as_view(),
        name='entities.edit'
    ),

    # Intents list or create your first intent
    path(
        'bots/edit/<uuid:aiid>/intents',
        IntentsView.as_view(),
        name='intents'
    ),

    # Add a new intent
    path(
        'bots/edit/<uuid:aiid>/intents/add',
        IntentsEditView.as_view(),
        name='intents.add'
    ),

    # Update an Intent of an existing AI
    path(
        'bots/edit/<uuid:aiid>/intents/edit/<slug:intent_name>',
        IntentsUpdateView.as_view(),
        name='intents.edit'
    ),

    # Upload intents in CSV format
    path(
        'bots/edit/<uuid:aiid>/intents/bulk/upload',
        IntentsBulkUploadView.as_view(),
        name='intents.bulk.upload'
    ),

    # List the integration options for an existing AI
    path(
        'bots/edit/<uuid:aiid>/integrations',
        IntegrationView.as_view(),
        name='integrations'
    ),

    # Oauth endpoint used by Facebook
    path(
        'oauth',
        OAuthView.as_view(),
        name='oauth'
    ),

    # Perform actions for facebook integration
    re_path(
        r'^bots/edit/(?P<aiid>[0-9a-f-]+)/integrations/facebook/'
        '(?P<action>connect|page|disconnect)$',
        FacebookActionView.as_view(),
        name='facebook_actions'
    ),

    # Save customisations to facebook integration
    path(
        'bots/edit/<uuid:aiid>/integrations/facebook/customise',
        FacebookCustomiseView.as_view(),
        name='facebook_customise'
    ),

    # Insights: download chat logs for an existing AI
    path(
        'bots/edit/<uuid:aiid>/insights/logs',
        ProxyInsightsLogsView.as_view(),
        name='insights_log_data'
    ),

    # Insights: download chart data for an existing AI
    path(
        'bots/edit/<uuid:aiid>/insights/chart/<slug:metric>',
        ProxyInsightsChartView.as_view(),
        name='insights_chart_data'
    ),

    # Display insights of an existing AI
    path(
        'bots/edit/<uuid:aiid>/insights',
        InsightsView.as_view(),
        name='insights'
    ),

    # Update settings of an existing AI
    path(
        'bots/edit/<uuid:aiid>/settings',
        AIUpdateView.as_view(),
        name='settings'
    ),

    # Re import bot into an existing one
    path(
        'bots/edit/<uuid:aiid>/import',
        AIReImportView.as_view(),
        name='re_import'
    ),

    # Proxy ajax AI calls
    path(
        'proxy/ai/<uuid:aiid>',
        ProxyAiView.as_view(),
        name='proxy.ai'
    ),

    path(
        'proxy/ai/<uuid:aiid>/export',
        ProxyAiExportView.as_view(),
        name='proxy.ai.export'
    ),

    path(
        'proxy/ai/<uuid:aiid>/handover/reset',
        ProxyHandoverResetView.as_view(),
        name='proxy.handover.reset'
    ),

    path(
        'proxy/ai/<uuid:aiid>/context/reset',
        ProxyContextResetView.as_view(),
        name='proxy.context.reset'
    ),

    path(
        'proxy/ai/<uuid:aiid>/regenerate_webhook_secret',
        ProxyRegenerateWebhookSecretView.as_view(),
        name='proxy.ai.regenerate_webhook_secret'
    ),

    path(
        'proxy/ai/<uuid:aiid>/chat',
        ProxyChatView.as_view(),
        name='proxy.ai.chat'
    ),

    # Remove an intent
    path(
        'intent/delete/<uuid:aiid>/<slug:intent_name>',
        IntentDeleteView.as_view(),
        name='intent.delete'
    ),

    # Remove an intent
    path(
        'entity/delete/<uuid:aiid>/<slug:entity_name>',
        EntityDeleteView.as_view(),
        name='entity.delete'
    ),

    # Templates redirect
    path(
        'templates',
        RedirectView.as_view(
            url='https://www.hutoma.ai/templates',
            permanent=True
        ),
        name='templates'
    ),

    # Get a template
    path(
        'templates/get/<int:bot_id>',
        TemplateGetView.as_view(),
        name='template.get'
    ),

    # Clone a template
    path(
        'templates/clone/<uuid:aiid>',
        TemplateCloneView.as_view(),
        name='template.clone'
    ),
]
