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

from django.contrib.auth.decorators import login_required
from django.views.generic.base import RedirectView, TemplateView

from studio.views import AiCreate

urlpatterns = [

    # Always use a path, explicit is better than implicit
    url(
        r'^$',
        login_required(
            RedirectView.as_view(pattern_name='summary')
        ),
        name='index'
    ),

    # Summary page of studio app
    url(
        r'^summary/?$',
        login_required(
            TemplateView.as_view(template_name='summary.html')
        ),
        name='summary'
    ),

    # Summary page of studio app
    url(
        r'^bots/add/?$',
        AiCreate.as_view(),
        name='add_bot'
    ),

]
