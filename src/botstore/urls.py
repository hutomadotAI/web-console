"""
    console top URL Configuration

    The `urlpatterns` list routes URLs to views. For more information please see:
        https://docs.djangoproject.com/en/1.11/topics/http/urls/

    Examples:

    Function views
        1. Add an import:  from studio import views
        path('', views.home, name='home')

    Class-based views
        1. Add an import:  from studio.views import Home
        path('', Home.as_view(), name='home')

    Including another URLconf
        1. Import the include() function: from django.conf.urls import url, include
        path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.urls import path, re_path
from django.views.decorators.cache import cache_page

from botstore.views import (
    BotDetailView,
    BotListView,
    CategoriesListView,
    PublishView,
    PurchaseView,
)

app_name = 'botstore'

urlpatterns = [

    # Get a list of all categories with top bots
    path(
        '',
        CategoriesListView.as_view(),
        name='all'
    ),

    # Get a list of all bots for one category
    re_path(
        r'^(?P<category>entertainment|education|events|finance|fitness|games|health%20%26%20beauty|internet%20of%20things|news|personal|other|shopping|social|travel|virtual%20assistants)$',
        BotListView.as_view(),
        name='category'
    ),

    # Get details of a Bot
    path(
        'bots/<int:bot_id>',
        BotDetailView.as_view(),
        name='detail'
    ),

    # Publish a bot to Bot Store
    path(
        'publish/<uuid:aiid>',
        PublishView.as_view(),
        name='publish'
    ),

    # Purchase a bot in Bot Store
    path(
        'purchase/<int:bot_id>',
        PurchaseView.as_view(),
        name='purchase'
    ),

]
