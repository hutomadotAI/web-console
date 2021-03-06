"""
    console top URL Configuration

    The `urlpatterns` list routes URLs to views. For more information please see:
        https://docs.djangoproject.com/en/1.11/topics/http/urls/

    Examples:

    Function views
        1. Add an import:  from studio import views
        path('$', views.home, name='home')

    Class-based views
        1. Add an import:  from studio.views import Home
        path('$', Home.as_view(), name='home')

    Including another URLconf
        1. Import the include() function: from django.conf.urls import url, include
        path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.views import defaults, generic
from django.views.generic.base import RedirectView

from users.views import PasswordChangeView


# Ugly but, Simple is better than complex
admin.site.site_header = 'Hu:toma admin'

urlpatterns = [


    path(
        '',
        include('studio.urls', namespace='studio')
    ),

    path(
        'botstore/',
        include('botstore.urls', namespace='botstore')
    ),

    # Used to access admin section
    path(
        'admin/',
        admin.site.urls
    ),

    path(
        'accounts/password/change/',
        PasswordChangeView.as_view(),
        name='password_change'
    ),

    # Used to support authentication and users management
    path(
        'accounts/',
        include('allauth.urls')
    ),

    path(
        'users/',
        include('users.urls', namespace='users')
    ),

    # Used for changing users language settings
    path(
        'i18n/',
        include('django.conf.urls.i18n'),
    ),

    # robots.txt
    path(
        'robots.txt',
        generic.base.TemplateView.as_view(
            content_type='text/plain',
            template_name='robots.txt'
        )
    ),

    # favicon fallback
    path(
        'favicon.ico',
        generic.base.RedirectView.as_view(
            url='/static/images/favicon.png',
            permanent=True
        ),
        name='favicon'
    ),

    # loader io key
    re_path(
        r'^loaderio-(?P<loader_io_id>[0-9a-f-]{32})/',
        generic.base.TemplateView.as_view(
            content_type='text/plain',
            template_name='loaderio.txt'
        )
    ),

    # Privacy redirect
    path(
        'cookies',
        RedirectView.as_view(
            url='https://c.fastcdn.co/u/97a8436d/27853407-0-cookiepolicy.pdf',
            permanent=True
        ),
        name='cookies'
    ),

    # Landing home page redirect
    path(
        'home',
        RedirectView.as_view(
            url='https://www.hutoma.ai',
            permanent=True
        ),
        name='home'
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
        path(
            '400',
            defaults.bad_request,
            kwargs={'exception': Exception('Bad Request!')}
        ),
        path(
            '403',
            defaults.permission_denied,
            kwargs={'exception': Exception('Permission Denied')}
        ),
        path(
            '404',
            defaults.page_not_found,
            kwargs={'exception': Exception('Page not Found')}
        ),
        path(
            '500',
            defaults.server_error
        ),
    ]

    if 'debug_toolbar' in settings.INSTALLED_APPS:

        import debug_toolbar

        urlpatterns += [
            path(
                '__debug__/',
                include(debug_toolbar.urls)
            ),
        ]
else:
    """
    By default Django errors are missing context, this allows the error
    pages to get request object in error templates.
    """
    from django.conf import urls

    urls.handler400 = 'app.errors.handler400'
    urls.handler403 = 'app.errors.handler403'
    urls.handler404 = 'app.errors.handler404'
    urls.handler500 = 'app.errors.handler500'
