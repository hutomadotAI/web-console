"""
    console top URL Configuration

    The `urlpatterns` list routes URLs to views. For more information please see:
        https://docs.djangoproject.com/en/1.11/topics/http/urls/

    Examples:

    Function views
        1. Add an import:  from studio import views
        2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')

    Class-based views
        1. Add an import:  from studio.views import Home
        2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')

    Including another URLconf
        1. Import the include() function: from django.conf.urls import url, include
        2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""

from django.conf.urls import url

from django.views.generic.base import RedirectView

from studio.views import (
    AICreateView,
    AIListView,
    AIUpdateView,
    EntitiesUpdateView,
    EntitiesView,
    IntegrationFacebookView,
    IntegrationView,
    IntentsUpdateView,
    IntentsView,
    ProxyAiExportView,
    ProxyAiView,
    ProxyEntityDeleteView,
    ProxyIntentDeleteView,
    ProxyRegenerateWebhookSecretView,
    RetrainView,
    SkillsView,
    TrainingView,
    IntegrationFacebookView,
    FacebookIntegrationCustomiseView,
    InsightsView,
    ProxyInsightsLogsView,
    ProxyInsightsChartView
)

urlpatterns = [

    # Always use a path, explicit is better than implicit
    url(
        r'^$',
        RedirectView.as_view(pattern_name='studio:summary'),
        name='index'
    ),

    # Summary page of studio app
    url(
        r'^summary/?$',
        AIListView.as_view(),
        name='summary'
    ),

    # Creat a new AI
    url(
        r'^bots/add/?$',
        AICreateView.as_view(),
        name='add_bot'
    ),

    # Edit an existing AI
    url(
        r'^bots/edit/(?P<aiid>[0-9a-f-]+)/?$',
        RedirectView.as_view(pattern_name='studio:skills'),
        name='edit_bot'
    ),

    # Update training of an existing AI
    url(
        r'^bots/edit/(?P<aiid>[0-9a-f-]+)/training/?$',
        TrainingView.as_view(),
        name='training'
    ),

    # Restart training of an AI
    url(
        r'^bots/edit/(?P<aiid>[0-9a-f-]+)/retrain/?$',
        RetrainView.as_view(),
        name='retrain'
    ),

    # Update skills of an existing AI
    url(
        r'^bots/edit/(?P<aiid>[0-9a-f-]+)/skills/?$',
        SkillsView.as_view(),
        name='skills'
    ),

    # Update entities of an existing AI
    url(
        r'^bots/edit/(?P<aiid>[0-9a-f-]+)/entities/?$',
        EntitiesView.as_view(),
        name='entities'
    ),

    # Update an Entity of an existing AI
    url(
        r'^bots/edit/(?P<aiid>[0-9a-f-]+)/entities/(?P<entity_name>[-0-9a-zA-Z_]+)/?$',
        EntitiesUpdateView.as_view(),
        name='entities.edit'
    ),

    # Update Intents of an existing AI
    url(
        r'^bots/edit/(?P<aiid>[0-9a-f-]+)/intents/?$',
        IntentsView.as_view(),
        name='intents'
    ),

    # Update an Intent of an existing AI
    url(
        r'^bots/edit/(?P<aiid>[0-9a-f-]+)/intents/(?P<intent_name>[-0-9a-zA-Z_]+)/?$',
        IntentsUpdateView.as_view(),
        name='intents.edit'
    ),

    # List the integration options for an existing AI
    url(
        r'^bots/edit/(?P<aiid>[0-9a-f-]+)/integrations/?$',
        IntegrationView.as_view(),
        name='integrations'
    ),

    # List or update facebook integration for this AI
    url(
        r'^bots/edit/(?P<aiid>[0-9a-f-]+)/integrations/facebook/(?P<action>get|page|disconnect)/(?P<id>[0-9]*)$',
        IntegrationFacebookView.as_view(),
        name='integrations_facebook'
    ),

    # save customisations to facebook integration
    url(
        r'^bots/edit/(?P<aiid>[0-9a-f-]+)/integrations/facebook/customise$',
        FacebookIntegrationCustomiseView.as_view(),
        name='integrations_facebook_customise'
    ),

    # Insights: download chat logs for an existing AI
    url(
        r'^bots/edit/(?P<aiid>[0-9a-f-]+)/insights/logs/?$',
        ProxyInsightsLogsView.as_view(),
        name='insights_log_data'
    ),

    # Insights: download chart data for an existing AI
    url(
        r'^bots/edit/(?P<aiid>[0-9a-f-]+)/insights/chart/?$',
        ProxyInsightsChartView.as_view(),
        name='insights_chart_data'
    ),

    # Display insights of an existing AI
    url(
        r'^bots/edit/(?P<aiid>[0-9a-f-]+)/insights/?$',
        InsightsView.as_view(),
        name='insights'
    ),

    # Update settings of an existing AI
    url(
        r'^bots/edit/(?P<aiid>[0-9a-f-]+)/settings/?$',
        AIUpdateView.as_view(),
        name='settings'
    ),

    # Proxy ajax AI calls
    url(
        r'^proxy/ai/(?P<aiid>[0-9a-f-]+)$',
        ProxyAiView.as_view(),
        name='proxy.ai'
    ),

    url(
        r'^proxy/ai/(?P<aiid>[0-9a-f-]+)/export$',
        ProxyAiExportView.as_view(),
        name='proxy.ai.export'
    ),

    url(
        r'^proxy/ai/(?P<aiid>[0-9a-f-]+)/regenerate_webhook_secret$',
        ProxyRegenerateWebhookSecretView.as_view(),
        name='proxy.ai.regenerate_webhook_secret'
    ),

    # Remove an intent
    url(
        r'^proxy/intent/(?P<aiid>[0-9a-f-]+)/?$',
        ProxyIntentDeleteView.as_view(),
        name='proxy.intent.delete'
    ),

    # Remove an intent
    url(
        r'^proxy/entity$',
        ProxyEntityDeleteView.as_view(),
        name='proxy.entity.delete'
    ),
]
