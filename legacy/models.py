from django.db import models


class Users(models.Model):
    """To be removed after we switch to Django Console"""
    username = models.CharField(max_length=50)
    email = models.CharField(max_length=100)
    password = models.CharField(max_length=64)
    password_salt = models.CharField(max_length=250)
    first_name = models.CharField(max_length=30)
    created = models.DateTimeField()
    attempt = models.CharField(max_length=15)
    dev_token = models.CharField(max_length=250)
    plan_id = models.IntegerField()
    dev_id = models.CharField(unique=True, max_length=50)
    last_name = models.CharField(max_length=30)
    valid = models.IntegerField()
    internal = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'users'
