from django.contrib import admin

from reversion.admin import VersionAdmin

from botstore.models import Bot


class BotAdmin(VersionAdmin):
    list_display = ('name', 'license_type', 'price', 'publishing_state')
    list_filter = ('publishing_state',)
    search_fields = ('name', 'description', 'long_description')


admin.site.register(Bot, BotAdmin)
