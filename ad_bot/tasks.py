from __future__ import absolute_import, unicode_literals
from celery import shared_task, task
from .models import AdBot
from datetime import datetime
from django.utils import timezone


@shared_task
def run_bot(bot_id):
    bot_inst = AdBot.objects.get(id=bot_id)
    bot_inst.executed_at = timezone.now()
    bot_inst.save()
    bot_inst.api_connector_init()
    bot_inst.check_ads()


@shared_task
def adbot_runner():
    bot_id = None
    for i in AdBot.objects.filter(switch=True):
        if i.executed_at:
            delta = timezone.now() - i.executed_at
            if delta >= i.frequency:
                bot_id = i.id
                run_bot.delay(bot_id)
        else:
            bot_id = i.id
            run_bot.delay(bot_id)
