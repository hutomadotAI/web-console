from django.contrib import admin

from reversion.admin import VersionAdmin

from studio.models import Ai


class AiAdmin(VersionAdmin):
    list_display = (
        'ai_name',
        'aiid',
        'is_private',
        'deleted',
        'created_on'
    )
    list_filter = ('is_private', 'ui_ai_language')
    search_fields = ('ai_name', 'aiid', 'dev_id', 'ai_description')


admin.site.register(Ai, AiAdmin)
