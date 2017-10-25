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
from django.conf.urls import include, url
from django.contrib import admin
from django.views import defaults, generic


# Ugly but, Simple is better than complex
admin.site.site_header = 'Hu:toma admin'

urlpatterns = [


    url(
        r'^',
        include('studio.urls', namespace='studio')
    ),

    url(
        r'^botstore/',
        include('botstore.urls')
    ),

    # Used to access admin section
    url(
        r'^admin/',
        admin.site.urls
    ),

    # Used to support authentication and users management
    url(
        r'^accounts/',
        include('allauth.urls')
    ),

    url(
        r'^entities/',
        include('entities.urls')
    ),

    # Used for changing users language settings
    url(
        r'^i18n/',
        include('django.conf.urls.i18n'),
    ),

    # favicon fallback
    url(
        r'^favicon\.ico$',
        generic.base.RedirectView.as_view(
            url='/static/images/favicon.png',
            permanent=True
        ),
        name='favicon'
    ),

    # favicon fallback
    url(
        r'^loaderio-beeabb3d964411d8b9bf497039873568/$',
        generic.base.TemplateView.as_view(template_name='loaderio.txt')
    ),
]

if settings.DEBUG:
    """
    This allows the error pages to be debugged during development, just visit
    these url in browser to see how these error pages look like.

    TODO:
        - 401
        - CSRF errors

    Use urls for Django toolbar if available
    """
    urlpatterns += [
        url(
            r'^400/$',
            defaults.bad_request,
            kwargs={'exception': Exception('Bad Request!')}
        ),
        url(
            r'^403/$',
            defaults.permission_denied,
            kwargs={'exception': Exception('Permission Denied')}
        ),
        url(
            r'^404/$',
            defaults.page_not_found,
            kwargs={'exception': Exception('Page not Found')}
        ),
        url(
            r'^500/$',
            defaults.server_error
        ),
    ]

    if 'debug_toolbar' in settings.INSTALLED_APPS:

        import debug_toolbar

        urlpatterns += [
            url(
                r'^__debug__/',
                include(debug_toolbar.urls)
            ),
        ]
