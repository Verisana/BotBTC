from __future__ import absolute_import, unicode_literals
import dateutil.parser
from urllib.parse import urlparse, parse_qs
from celery import shared_task, task
from .models import AdBot, OpenTrades, ReportData, AdBotTechnical
from datetime import datetime
from django.utils import timezone
from ast import literal_eval as make_tuple
from celery.result import AsyncResult


@shared_task
def run_bot(bot_id):
    bot_inst = AdBot.objects.get(id=bot_id)
    tech = AdBotTechnical.objects.get(adbot=bot_inst)
    tech.executed_at = timezone.now()
    tech.save(update_fields=['executed_at'])
    bot_inst.api_connector_init()
    bot_inst._get_ads()
    if bot_inst.my_ad['data']['ad_list'][0]['data']['visible']:
        bot_inst.check_ads()
    else:
        bot_inst.switch = False
        bot_inst.save(update_fields=['switch'])


@shared_task
def adbot_runner():
    for i in AdBot.objects.filter(switch=True):
        tech = AdBotTechnical.objects.get_or_create(adbot=i)[0]
        if tech.executed_at:
            delta = timezone.now() - tech.executed_at
            if delta >= i.frequency:
                if tech.task_id:
                    task_status = AsyncResult(tech.task_id)
                    if task_status.ready:
                        run_bot_async = run_bot.delay(i.id)
                        tech.task_id = run_bot_async.task_id
                        tech.save(update_fields=['task_id'])
                else:
                    run_bot_async = run_bot.delay(i.id)
                    tech.task_id = run_bot_async.task_id
                    tech.save(update_fields=['task_id'])
        else:
            run_bot_async = run_bot.delay(i.id)
            tech.task_id = run_bot_async.task_id
            tech.save(update_fields=['task_id'])

        if tech.message_executed_at:
            delta = timezone.now() - tech.message_executed_at
            if delta >= tech.message_frequency:
                if tech.message_task_id:
                    task_status = AsyncResult(tech.message_task_id)
                    if task_status.ready:
                        message_bot_async = message_bot.delay()
                        tech.message_task_id = message_bot_async.task_id
                        tech.save(update_fields=['message_task_id'])
                else:
                    message_bot_async = message_bot.delay()
                    tech.message_task_id = message_bot_async.task_id
                    tech.save(update_fields=['message_task_id'])
        else:
            message_bot_async = message_bot.delay()
            tech.message_task_id = message_bot_async.task_id
            tech.save(update_fields=['message_task_id'])


@shared_task
def message_bot(bot_id):
    bot_inst = AdBot.objects.get(id=bot_id)
    tech = AdBotTechnical.objects.get(adbot=bot_inst)
    tech.message_executed_at = timezone.now()
    tech.save(update_fields=['message_executed_at'])

    if bot_inst.enable_autoposting:
        bot_inst.api_connector_init()
        bot_inst.send_first_message()


@shared_task
def opentrades_cleaner():
    for i in OpenTrades.objects.all():
        i.adbot.api_connector_init()
        i.adbot.send_second_message(i.trade_id)


@shared_task
def calculate_report():
    stop_date = dateutil.parser.parse('2018-05-01T00:00:00+00:00')
    for i in AdBot.objects.all():
        i.api_connector_init()
        i._get_released_trades()
        if ReportData.objects.filter(adbot=i.id):
            last_report_id = ReportData.objects.filter(adbot=i.id).latest('date').contact_id
        else:
            last_report_id = 0
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
        while go:
            for l in i.released_trades['data']['contact_list']:
                release_date = dateutil.parser.parse(
                        l['data']['released_at'],

                        )
                contact_ref = l['data']['contact_id']
                if not contact_ref == last_report_id and release_date >= stop_date:
                    trade_dir = l['data']['advertisement']['trade_type']
                    payment = l['data']['advertisement']['payment_method']
                    if i.get_trade_direction_display() == trade_dir and i.get_payment_method_display() == payment:
                        date = release_date
                        amount_rub = float(l['data']['amount'])
                        amount_btc = float(l['data']['amount_btc'])
                        fee_btc = float(l['data']['fee_btc'])
                        price = amount_rub / (amount_btc + fee_btc)
                        if trade_dir == 'ONLINE_SELL':
                            agent = l['data']['buyer']['name']
                        else:
                            agent = l['data']['seller']['name']
                        contact_id = int(l['data']['contact_id'])
                        ReportData.objects.create(date=date,
                                                  adbot=i,
                                                  contact_id=contact_id,
                                                  agent=agent,
                                                  price=price,
                                                  amount_rub=amount_rub,
                                                  amount_btc=amount_btc,
                                                  fee_btc=fee_btc,
                                                )
                else:
                    go = False
                    break
            if go:
                parsed = urlparse(l.released_trades['pagination']['next'])
                params = parse_qs(parsed.query)
                i._get_released_trades(next_p=params)
