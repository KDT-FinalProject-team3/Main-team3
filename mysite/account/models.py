from django.db import models

# Create your models here.


class Account(models.Model):
    account = models.CharField(max_length=16)
    password = models.CharField(max_length=255)
    name = models.CharField(max_length=20)
    phonenumber = models.CharField(max_length=13)
    email = models.CharField(max_length=254)
    membertype = models.IntegerField()
    user_id = models.IntegerField()
    user_name = models.CharField(max_length=8)
    date_joined = models.DateTimeField()

    class Meta:
        managed = True
        db_table = 'account'




