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

from django.conf import settings
from django.conf.urls import url
from django.views.decorators.cache import cache_page

from botstore.views import BotDetailView, BotListView, CategoriesListView

urlpatterns = [

    # Get details of a Bot
    url(
        r'^bots/(?P<pk>\d+)/$',
        cache_page(settings.TEMPLATES_CACHE_AGE)(BotDetailView.as_view()),
        name='bot-detail'
    ),

    # Get a list of all categories with top bots
    url(
        r'^$',
        cache_page(settings.TEMPLATES_CACHE_AGE)(CategoriesListView.as_view()),
        name='botstore'
    ),

    # Get a list of all bots for one category
    url(
        r'^(?P<category>entertainment|education|events|finance|fitness|games|health%20%26%20beauty|internet%20of%20things|news|personal|other|shopping|social|travel|virtual%20assistants)$',
        cache_page(settings.TEMPLATES_CACHE_AGE)(BotListView.as_view()),
        name='botstore_category'
    ),

    # Publish a bot to Bot Store
    url(
        r'^bots/publish/(?P<aiid>[0-9a-f-]+)/?$',
        cache_page(settings.TEMPLATES_CACHE_AGE)(BotDetailView.as_view()),
        name='publish_bot'
    ),

]
