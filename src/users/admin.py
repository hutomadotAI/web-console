import logging

from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from reversion.admin import VersionAdmin

logger = logging.getLogger(__name__)
admin.site.login = login_required(admin.site.login)


class UserAdmin(VersionAdmin):
    list_display = (
        'username',
        'email',
        'date_joined',
        'is_superuser',
        'is_staff',
        'is_active',
        'dev_id'
    )
    list_filter = [
        'is_superuser',
        'is_staff',
        'is_active',
        'emailaddress__verified'
    ]
    ordering = ['date_joined']
    search_fields = ['username', 'email', 'profile__dev_id']

    def get_queryset(self, request):
        """Prefetch profile data"""
        return super(UserAdmin, self).get_queryset(request).select_related(
            'profile'
        )

    def dev_id(self, obj):
        return obj.profile.dev_id
    dev_id.admin_order_field = 'profile__dev_id'


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
