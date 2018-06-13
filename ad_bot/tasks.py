from __future__ import absolute_import, unicode_literals
import dateutil.parser
import pandas as pd
import numpy as np
from urllib.parse import urlparse, parse_qs
from celery import shared_task, task
from .models import AdBot, OpenTrades
from datetime import datetime
from django.utils import timezone


@shared_task
def run_bot(bot_id):
    bot_inst = AdBot.objects.get(id=bot_id)
    bot_inst.executed_at = timezone.now()
    bot_inst.save(update_fields=['executed_at'])
    bot_inst.api_connector_init()
    bot_inst._get_ads()
    if bot_inst.my_ad['data']['ad_list'][0]['data']['visible']:
        bot_inst.check_ads()
        bot_inst.executing = False
        bot_inst.save(update_fields=['executing'])
    else:
        bot_inst.switch = False
        bot_inst.executing = False
        bot_inst.save(update_fields=['switch', 'executing'])


@shared_task
def adbot_runner():
    bot_id = None
    for i in AdBot.objects.filter(switch=True):
        if i.executed_at:
            delta = timezone.now() - i.executed_at
            if delta >= i.frequency:
                bot_id = i.id
                if not i.executing:
                    i.executing = True
                    i.save(update_fields=['executing'])
                    run_bot.delay(bot_id)
        else:
            bot_id = i.id
            if not i.executing:
                i.executing = True
                i.save(update_fields=['executing'])
                run_bot.delay(bot_id)


@shared_task
def message_bot():
    bot_id = None
    contact_id = None
    for i in AdBot.objects.filter(switch=True):
        if i.enable_autoposting:
            i.api_connector_init()
            i.send_first_message()


@shared_task
def opentrades_cleaner():
    for i in OpenTrades.objects.all():
        i.adbot.api_connector_init()
        i.adbot.send_second_message(i.trade_id)

@shared_task
def calculate_report(bot_id, date_1_raw, date_2_raw):
    result = {}
    date_1 = dateutil.parser.parse(date_1_raw, ignoretz=True)
    date_2 = dateutil.parser.parse(date_2_raw, ignoretz=True)
    bot_inst = AdBot.objects.get(id=bot_id)
    bot_inst.api_connector_init()
    bot_inst._get_released_trades()
    go = True
    calc_data = []
    np_data = []
    headers = ['num',
               'date',
               'contact_id',
               'agent',
               'price',
               'amount_rub',
               'amount_btc',
               'fee_btc',
                ]
    l = 0
    while go:
        for i in bot_inst.released_trades['data']['contact_list']:
            release_date = dateutil.parser.parse(
                    i['data']['released_at'],
                    ignoretz=True,
                )
            if release_date >= date_1 and release_date <= date_2:
                trade_dir = i['data']['advertisement']['trade_type']
                payment = i['data']['advertisement']['payment_method']
                if bot_inst.get_trade_direction_display() == trade_dir and bot_inst.get_payment_method_display() == payment:
                    l += 1
                    date = release_date
                    amount_rub = float(i['data']['amount'])
                    amount_btc = float(i['data']['amount_btc'])
                    fee_btc = float(i['data']['fee_btc'])
                    price = amount_rub / (amount_btc + fee_btc)
                    agent = i['data']['buyer']['name']
                    contact_id = int(i['data']['contact_id'])
                    temp_dic = {'num': l,
                                'date': date,
                                'contact_id': contact_id,
                                'agent': agent,
                                'price': price,
                                'amount_rub': amount_rub,
                                'amount_btc': amount_btc,
                                'fee_btc': fee_btc,
                                }
                    temp_list = [l,
                                 date,
                                 contact_id,
                                 agent,
                                 price,
                                 amount_rub,
                                 amount_btc,
                                 fee_btc,
                                 ]
                    np_data.append(temp_list)
                    calc_data.append(temp_dic)
            elif release_date >= date_1:
                continue
            else:
                go = False
                break
        if go:
            parsed = urlparse(bot_inst.released_trades['pagination']['next'])
            params = parse_qs(parsed.query)
            bot_inst._get_released_trades(next_p=params)

    if calc_data:
        df = pd.DataFrame(np.array(np_data),
                        index=range(len(np_data)),
                        columns=headers)
        result['mean_price'] = round(df['price'].mean(), 2)
        result['sum_rub'] = df['amount_rub'].sum()
        result['sum_rub_qiwi'] = result['sum_rub'] - (result['sum_rub']*0.018)
        result['sum_btc'] = df['amount_btc'].sum()
        result['fee_sum'] = df['fee_btc'].sum()
        result['sum_all_btc'] = result['fee_sum'] + result['sum_btc']
        result['number_trades'] = calc_data[-1]['num']
        result['calc_data'] = calc_data
    else:
        result['nodata'] = 'Нет информации по указанному периоду'
    return result
