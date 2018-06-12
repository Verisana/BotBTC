from __future__ import absolute_import, unicode_literals
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
