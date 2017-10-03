import pytz

from django.db import models
from django.utils.translation import ugettext_lazy as _


class Ai(models.Model):
    FEMALE = 0
    MALE = 1
    TIMEZONES = [(tz, tz) for tz in pytz.common_timezones]
    VOICES = zip(
        [FEMALE, MALE],
        [_('Female'), _('Male')]
    )

    aiid = models.CharField(unique=True, max_length=50)
    ai_name = models.CharField(max_length=50, blank=True, null=True)
    ai_description = models.CharField(max_length=250, blank=True, null=True)
    default_chat_responses = models.TextField()  # This field type is a guess.
    created_on = models.DateTimeField(blank=True, null=True)
    dev_id = models.CharField(max_length=50)
    is_private = models.BooleanField(default=False)
    client_token = models.CharField(max_length=250)
    hmac_secret = models.CharField(max_length=50, blank=True, null=True)
    ui_ai_language = models.CharField(max_length=10, blank=True, null=True)
    ui_ai_timezone = models.CharField(
        default='Europe/London',
        choices=TIMEZONES,
        max_length=63,
    )
    ui_ai_confidence = models.FloatField(blank=True, null=True)
    ui_ai_personality = models.PositiveIntegerField(blank=True, null=True)
    ui_ai_voice = models.PositiveIntegerField(
        default=0,
        choices=VOICES,
    )
    deleted = models.BooleanField(default=False)
    passthrough_url = models.URLField(max_length=1024, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ai'

    def __str__(self):
        return 'AI: %s' % (self.aiid)
