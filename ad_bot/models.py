from django.db import models
from profiles.models import APIKeyModel 
from django.contrib.postgres.fields import JSONField

class AdBotModel(models.Model):
    name = models.CharField(max_length=64, unique=True)
    api_keys = models.ForeignKey('profiles.APIKeyModel', on_delete=models.CASCADE)
    stop_price = models.DecimalField(max_digits=9, decimal_places=2)
    step = models.IntegerField()
    volume = models.IntegerField(null=True)
    switch = models.BooleanField(default=False)
    frequency = models.DurationField()
    payment_method = models.CharField(max_length=32)
    ad_id = models.IntegerField()
    trade_direction = models.CharField(max_length=32,
                                       choices = (
                                            ('sell-bitcoins-online',
                                             'Встать на покупку'),
                                            ('buy-bitcoins-online',
                                             'Встать на продажу'),
                                       ))


class ActionLogModel(models.Model):
    action = models.TextField()
    timestamp = models.DateTimeField(auto_now=True)
    request_method = models.CharField(max_length=10)
    request_url = models.URLField()
    response_data = JSONField()
    response_code = models.IntegerField()
