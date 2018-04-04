from django.db import models
from profiles.models import APIKey, Profile
from django.contrib.postgres.fields import JSONField
from botbtc import hmac_auth
import json
import requests


class AdBot(models.Model):
    name = models.CharField(max_length=64, unique=True)
    api_keys = models.ForeignKey('profiles.APIKey',
                                 on_delete=models.CASCADE)
    stop_price = models.DecimalField(max_digits=9,
                                     decimal_places=2)
    step = models.IntegerField()
    volume = models.IntegerField(null=True)
    switch = models.BooleanField(default=False)
    frequency = models.DurationField()
    payment_method = models.CharField(
        max_length=64,
        choices=(('qiwi', 'QIWI'),
                 ('cash-deposit', 'CASH_DEPOSIT'),
                 ('transfers-with-specific-bank', 'SPECIFIC_BANK')))
    trade_direction = models.CharField(max_length=64,
                                       choices=(('buy-bitcoins-online',
                                                 'ONLINE_SELL'),
                                                ('sell-bitcoins-online',
                                                 'ONLINE_BUY')
                                                ))
    ad_id = models.IntegerField()
    username = models.ForeignKey('profiles.Profile',
                                 on_delete=models.CASCADE)
    change_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '%s, %s' % (self.name, self.ad_id)

    def api_connector_init(self):
        self.auth = hmac_auth.hmac(self.api_keys.api_key,
                                   self.api_keys.api_secret)
        self.base_url = 'https://localbitcoins.net'
        self.endpoints = {
                'get_my_ad': '/api/ad-get/%d/' % (self.ad_id),
                'post_upd_equat': '/api/ad-equation/%d/' %
                                                (self.ad_id),
                'public_ads': '/%s/rub/%s/.json' %
                                        (self.trade_direction,
                                         self.payment_method)
                        }
        self._get_ads()

    def _get_ads(self):
        self.my_ad = self.auth.call('GET', self.endpoints['get_my_ad']).json()
        self.all_ads = requests.get(
                            self.base_url +
                            self.endpoints['public_ads']).json()

    def _isfirst(self):
        result = {'isfirst': None, 'compensate': 0}

        if result['isfirst'] is None:
            for i, item in enumerate(self.all_ads['data']['ad_list']):
                if item['data']['ad_id'] == self.ad_id and i - result['compensate'] == 0:
                    result['isfirst'] = True
                    break
                else:
                    if item['data']['max_amount'] >= self.volume:
                        result['isfirst'] = False
                        result['enemy'] = i
                        break
                    else:
                        result['compensate'] += 1
        return result

    def _update_price(self, enemy):
        result = None
        target_price = Decimal()
        if self.trade_direction == 'ONLINE_SELL':
            target_price = Decimal(self.all_ads['data']['ad_list'][enemy]['data']['temp_price']
                        - self.step)
        elif self.trade_direction == 'ONLINE_BUY':
            target_price = Decimal(self.all_ads['data']['ad_list'][enemy]['data']['temp_price']
                        + self.step)

        if target_price == Decimal(self.my_ad['adata']['ad_list'][0]['data']['temp_price']):
            result = 'Your ad is up to date'
        else:
            response = self.auth.call('POST',
                                       self.endpoints['post_upd_equat'],
                                       params={'price-equation': '%s' % (target_price)})
            if response.status_code == 200:
                result = 'Your ad has been updated to target_price'

        return result

    def check_ads(self):
        import pdb
        pdb.set_trace()

        result = None
        if self.my_ad['data']['ad_list'][0]['data']['visible']:
            isfirst = self._isfirst()
            if isfirst['isfirst']:
                self._update_price(1+isfirst['compensate'])
                result = 'Already first'
            else:
                self._update_price(isfirst['enemy'])
                result = 'Your price has been updated'

        return result


class ActionLog(models.Model):
    action = models.TextField()
    timestamp = models.DateTimeField(auto_now=True)
    request_method = models.CharField(max_length=10)
    request_url = models.URLField()
    response_data = JSONField()
    response_code = models.IntegerField()
    bot_model = models.ForeignKey('ad_bot.AdBot',
                                  on_delete=models.CASCADE)
