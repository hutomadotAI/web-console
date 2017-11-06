from django.conf.urls import url

from users.views import DeveloperInfoView

urlpatterns = [

    # User developer info
    url(
        r'^info/?$',
        DeveloperInfoView.as_view(),
        name='info'
    ),

]
