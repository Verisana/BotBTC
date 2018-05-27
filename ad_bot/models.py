from django.db import models
from profiles.models import APIKey, Profile
from botbtc import hmac_auth
import json
import requests
from decimal import *


class AdBot(models.Model):
    name = models.CharField(max_length=64, unique=True)
    api_keys = models.ForeignKey('profiles.APIKey',
                                 on_delete=models.CASCADE)
    stop_price = models.DecimalField(max_digits=9,
                                     decimal_places=2,
                                     help_text='Цена для остановки')
    step = models.IntegerField(help_text='Шаг обновления цены')
    volume_max = models.IntegerField(null=True,
                                     help_text='Фильтр по мелким игрокам')
    volume_min = models.IntegerField(null=True,
                                     help_text='Фильтр по крупным игрокам')
    switch = models.BooleanField(default=False)
    frequency = models.DurationField(help_text='Частота обновления')
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
    ad_id = models.IntegerField(unique=True)
    username = models.ForeignKey('profiles.Profile',
                                 on_delete=models.CASCADE)
    executed_at = models.DateTimeField(blank=True, null=True)
    price_round = models.BooleanField(default=True)
    executing = models.BooleanField(default=False)

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

    def _get_next_page(self, next_page):
        self.all_ads = requests.get(next_page).json()

    def _stop_check(self, curr_ad):
        stop_check = True
        temp_price = curr_ad['data']['temp_price']

        if self.trade_direction == 'buy-bitcoins-online':
            if Decimal(float(temp_price)) < self.stop_price:
                stop_check = False
        else:
            if Decimal(float(temp_price)) > self.stop_price:
                stop_check = False
        return stop_check

    def _min_check(self, curr_ad):
        min_check = True
        min_amount = curr_ad['data']['min_amount']

        if self.volume_min:
            if int(min_amount) > self.volume_min:
                min_check = False
        return min_check

    def _max_check(self, curr_ad):
        max_check = True
        max_amount = curr_ad['data']['max_amount']

        if self.volume_max:
            if int(max_amount) <= self.volume_max:
                max_check = False
        return max_check

    def _filter_check(self, curr_ad):
        result = None
        if self._max_check(curr_ad) and self._min_check(
                    curr_ad) and self._stop_check(
                                curr_ad):
            result = True
        else:
            result = False
        return result

    def _isfirst(self):
        result = {'isfirst': None, 'compensate': 0}

        if result['isfirst'] is None:
            for i, item in enumerate(self.all_ads['data']['ad_list']):
                if item['data']['ad_id'] == self.ad_id and i - result['compensate'] == 0:
                    ad_below_me = self.all_ads['data']['ad_list'][i+1]
                    if self._filter_check(ad_below_me):
                        result['isfirst'] = True
                        break
                    else:
                        for l, item in enumerate(self.all_ads['data']['ad_list'][i+1:]):
                            if not self._filter_check(item):
                                result['compensate'] += 1
                            break
                        result['isfirst'] = True
                        result['compensate'] += 1
                        break
                else:
                    if self._filter_check(item):
                        result['isfirst'] = False
                        result['enemy'] = i
                        break
                    else:
                        result['compensate'] += 1
                        if result['compensate'] >= self.all_ads['data']['ad_count']:
                            self._get_next_page(self.all_ads['pagination']['next'])
        return result

    def _update_price(self, enemy):
        target_price = Decimal()
        int_price = int()
        str_price = str()

        if self.trade_direction == 'buy-bitcoins-online':
            target_price = Decimal(
                float(
                    self.all_ads['data']['ad_list'][enemy]['data']
                    ['temp_price']) - self.step)
            int_price = int(round(target_price))
            if self.price_round:
                while int_price % 100 > 0:
                    int_price -= 1
            if int_price < int(self.stop_price):
                int_price = int(self.stop_price)
            str_price = str(int_price) + '.00'
        elif self.trade_direction == 'sell-bitcoins-online':
            target_price = Decimal(
                float(
                    self.all_ads['data']['ad_list'][enemy]['data']
                    ['temp_price']) + self.step)
            int_price = int(round(target_price))
            if self.price_round:
                while int_price % 100 > 0:
                    int_price += 1
            if int_price > int(self.stop_price):
                int_price = int(self.stop_price)
            str_price = str(int_price) + '.00'

        if int_price == int(
            Decimal(
                float(
                    self.my_ad['data']['ad_list'][0]['data']
                    ['temp_price']))):
            message = 'Цена %s объявления %s нормальная. Ничего не меняю' % (
                str_price, self.name)
            ActionLog.objects.create(action=message,
                                     bot_model=self)
        else:
            message = 'Меняю цену объявления %s на %s' % (
                self.name, str_price)
            ActionLog.objects.create(action=message,
                                     bot_model=self)
            response = self.auth.call(
                'POST', self.endpoints['post_upd_equat'],
                params={'price_equation': '%s' % (str_price)})

    def check_ads(self):
        if self.my_ad['data']['ad_list'][0]['data']['visible']:
            isfirst = self._isfirst()
            if isfirst['isfirst']:
                message = '%s на первом месте. Проверяю цену' % (self.name)
                ActionLog.objects.create(action=message,
                                         bot_model=self)
                self._update_price(1+isfirst['compensate'])
            else:
                message = '%s перебито. Сейчас обновлю цену' % (self.name)
                ActionLog.objects.create(action=message,
                                         bot_model=self)
                self._update_price(isfirst['enemy'])
        else:
            self.switch = False
            self.save()


class ActionLog(models.Model):
    action = models.TextField()
    timestamp = models.DateTimeField(auto_now=True)
    bot_model = models.ForeignKey('ad_bot.AdBot',
                                  on_delete=models.CASCADE)

    def __str__(self):
        return '%d' % (self.id)
