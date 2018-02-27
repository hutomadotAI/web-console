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
        'get_dev_id'
    )
    list_filter = [
        'is_superuser',
        'is_staff',
        'is_active',
        'emailaddress__verified'
    ]
    ordering = ['date_joined']
    search_fields = ['username', 'email', 'profile__dev_id']

    def get_dev_id(self, obj):
        return obj.profile.dev_id
    get_dev_id.admin_order_field = 'profile__dev_id'
    get_dev_id.short_description = 'Dev ID'

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
