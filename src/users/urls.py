from django.urls import path

from users.views import DeveloperInfoView

app_name = 'users'

urlpatterns = [

    # User developer info
    path(
        'info',
        DeveloperInfoView.as_view(),
        name='info'
    ),

]
