from django.db import models


class Bot(models.Model):
    dev = models.ForeignKey(
        'users.Users',
        models.DO_NOTHING
    )

    aiid = models.ForeignKey(
        'studio.Ai',
        models.DO_NOTHING,
        db_column='aiid'
    )

    name = models.CharField(
        max_length=50
    )

    description = models.CharField(
        max_length=1024
    )

    long_description = models.TextField(blank=True, null=True)
    alert_message = models.CharField(max_length=150, blank=True, null=True)
    badge = models.CharField(max_length=20, blank=True, null=True)
    license_type = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=0)
    sample = models.TextField(blank=True, null=True)
    last_update = models.DateTimeField()
    category = models.CharField(max_length=50)
    privacy_policy = models.TextField(blank=True, null=True)
    classification = models.CharField(max_length=50)
    version = models.CharField(max_length=25)
    video_link = models.CharField(max_length=1800, blank=True, null=True)
    publishing_state = models.IntegerField()

    boticon = models.ImageField(
        db_column='botIcon',
        upload_to='boticon/',
        blank=True,
        null=True
    )  # Field name made lowercase.

    featured = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'botStore'

    def __str__(self):
        return 'Bot from store: %s' % (self.name)
