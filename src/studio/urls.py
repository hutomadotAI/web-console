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

from studio.views import AICreateView, AIListView

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
        AICreateView.as_view(),
        name='edit_bot'
    ),

]
