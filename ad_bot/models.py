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
    price_round = models.BooleanField(default=True)
    page_number = models.IntegerField(default=1)
    greetings_text = models.TextField(blank=True, null=True)
    farewell_text = models.TextField(blank=True, null=True)
    enable_autoposting = models.BooleanField(default=False)


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
                'public_ads': '/%s/rub/%s/.json?page=%d' %
                                        (self.trade_direction,
                                         self.payment_method,
                                         self.page_number),
                'open_trades': '/api/dashboard/',
                'current_trade': '/api/contact_info/',
                'post_message': '/api/contact_message_post/',
                'released_trades': '/api/dashboard/released/',
                'all_notifications': '/api/notifications/',
                'mark_notification': '/api/notifications/mark_as_read/',
                        }

    def _get_ads(self):
        self.my_ad = self.auth.call('GET', self.endpoints['get_my_ad']).json()
        self.all_ads = requests.get(
                            self.base_url +
                            self.endpoints['public_ads']).json()

    def _get_open_trades(self):
        self.opened_trades = self.auth.call(
                    'GET', self.endpoints['open_trades']).json()

    def _get_released_trades(self, next_p=''):
        self.released_trades = self.auth.call(
                    'GET',
                    self.endpoints['released_trades'],
                    params=next_p).json()

    def _get_curr_trade(self, con_id):
        self.curr_trade = self.auth.call(
                    'GET', self.endpoints['current_trade']+str(con_id)+'/').json()

    def _get_all_notifications(self):
        self.all_notif = self.auth.call(
                    'GET', self.endpoints['all_notifications']).json()

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

    def _is_trade_repeating(self, con_id):
        for i in OpenTrades.objects.all():
            if con_id == i.trade_id:
                return True
        return False

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
            pass
        else:
            response = self.auth.call(
                'POST', self.endpoints['post_upd_equat'],
                params={'price_equation': '%s' % (str_price)})

    def check_ads(self):
        if not self.my_ad:
            self._get_ads()

        isfirst = self._isfirst()
        if isfirst['isfirst']:
            self._update_price(1+isfirst['compensate'])
        else:
            self._update_price(isfirst['enemy'])

    def send_first_message(self):
        self._get_open_trades()
        for i in self.opened_trades['data']['contact_list']:
            contact_id = i['data']['contact_id']
            if not i['data']['disputed_at'] and not self._is_trade_repeating(contact_id):
                self.auth.call(
                    'POST',
                    self.endpoints['post_message']+str(contact_id)+'/',
                    params={'msg': self.greetings_text})
                self._get_all_notifications()
                for i in self.all_notif['data']:
                    if i['contact_id'] == contact_id:
                        self.auth.call(
                            'POST',
                            self.endpoints['mark_notification']+str(i['id'])+'/')
                        break
                OpenTrades.objects.create(trade_id=contact_id,
                                          username=self.username,
                                          adbot=self)
        self._check_closed_deals()

    def _check_closed_deals(self):
        self._get_released_trades()
        open_trades_qs = OpenTrades.objects.all()

        for i in self.released_trades['data']['contact_list']:
            for l in open_trades_qs:
                if i['data']['contact_id'] == l.trade_id:
                    self.auth.call(
                            'POST',
                            self.endpoints['post_message']+str(i['data']['contact_id'])+'/',
                            params={'msg': self.farewell_text})
                    l.delete()
                    break

    def send_second_message(self, contact_id):
        self._get_curr_trade(contact_id)
        to_delete = OpenTrades.objects.get(trade_id=contact_id)
        if self.curr_trade['data']['released_at']:
            self.auth.call(
                    'POST',
                    self.endpoints['post_message']+str(contact_id)+'/',
                    params={'msg': self.farewell_text})
            to_delete.delete()
        elif self.curr_trade['data']['closed_at']:
            to_delete.delete()


class OpenTrades(models.Model):
    trade_id = models.IntegerField(null=True)
    username = models.ForeignKey('profiles.Profile',
                                  on_delete=models.CASCADE)
    adbot = models.ForeignKey('AdBot',
                              on_delete=models.CASCADE)

    def __str__(self):
        return '%s' % self.trade_id


class ReportData(models.Model):
    adbot = models.ForeignKey('AdBot',
                                 on_delete=models.CASCADE,
                                )
    date = models.DateTimeField()
    contact_id = models.IntegerField()
    agent = models.CharField(max_length=256)
    price = models.DecimalField(max_digits=9,
                                decimal_places=2,
                               )
    amount_rub = models.DecimalField(max_digits=9,
                                     decimal_places=2,
                                    )
    amount_btc = models.DecimalField(max_digits=9,
                                     decimal_places=8,
                                    )
    fee_btc = models.DecimalField(max_digits=9,
                                  decimal_places=8,
                                 )

    def __str__(self):
        return '%s' % self.contact_id


class AdBotTechnical(models.Model):
    adbot = models.ForeignKey('AdBot',
                              on_delete=models.CASCADE)
    executed_at = models.DateTimeField(blank=True, null=True)
    task_id = models.CharField(max_length=64, blank=True, null=True)
    message_task_id = models.CharField(max_length=64, blank=True, null=True)
    message_executed_at = models.DateTimeField(blank=True, null=True)
    message_frequency = models.DurationField(default='30', blank=True, null=True)

    def __str__(self):
        return '%s' % self.adbot
