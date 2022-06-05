from django.db import models

# Create your models here.


class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=16)
    contact = models.CharField(max_length=13)
    gender = models.CharField(max_length=4)
    email = models.CharField(max_length=255, blank=True, null=True)
    address = models.CharField(max_length=45)
    birth = models.DateField()
    status = models.CharField(max_length=8)
    specifics = models.CharField(max_length=255, blank=True, null=True)
    create_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'user'


class EmotionResult(models.Model):
    user = models.ForeignKey('User', models.DO_NOTHING)
    fear = models.FloatField()
    surprise = models.FloatField()
    anger = models.FloatField()
    sadness = models.FloatField()
    neutrality = models.FloatField()
    happiness = models.FloatField()
    anxiety = models.FloatField()
    embarrassed = models.FloatField()
    hurt = models.FloatField()
    interest = models.FloatField()
    boredom = models.FloatField()
    date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'emotion_result'


class InputSentence(models.Model):
    user_num = models.IntegerField()
    sentence = models.CharField(max_length=512)
    date = models.DateTimeField(blank=True, null=True)
    done = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'input_sentence'


