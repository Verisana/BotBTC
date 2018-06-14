import dateutil.parser
import pandas as pd
import numpy as np
from decimal import *
from django.shortcuts import render, reverse, redirect
from django.views import generic, View
from .models import AdBot, ReportData
from .tasks import adbot_runner, calculate_report
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages


class IndexView(LoginRequiredMixin, View):
    http_method_names = ['get', 'post']
    login_url = '/profiles/login/'

    def get(self, request, *args, **kwargs):
        context = {}
        context['adbot'] = AdBot.objects.filter(username=request.user.id).order_by('name')
        #b = AdBot.objects.get(ad_id=724665)
        #b.api_connector_init()
        #from remote_pdb import RemotePdb
        #RemotePdb('127.0.0.1', 4444).set_trace()
        #import pdb; pdb.set_trace()
        #b.check_ads()
        return render(request, 'ad_bot/index.html', context)


class SettingsView(LoginRequiredMixin, generic.ListView):
    model = AdBot
    template_name = 'ad_bot/settings.html'

class SwitchView(View):
    http_method = ['post']

    def post(self, request, *args, **kwargs):
        bot_id = int(request.POST.get('bot_id'))
        bot = AdBot.objects.get(id=bot_id)
        if bot.switch:
            bot.switch = False
        else:
            bot.switch = True
        bot.save()
        return redirect('ad_bot:index')

class ReportsView(LoginRequiredMixin, View):
    http_method = ['get', 'post']
    login_url = '/profiles/login/'

    def get(self, request, *args, **kwargs):
        context = {}
        context['adbot'] = AdBot.objects.all()

        return render(request, 'ad_bot/reports.html', context)

    def post(self, request, *args, **kwargs):
        calculate_report.delay()
        context = {}
        headers = ['num',
                   'date',
                   'contact_id',
                   'agent',
                   'price',
                   'amount_rub',
                   'amount_btc',
                   'fee_btc',
                 ]
        bot_id = int(request.POST.get('adbot_chooser'))
        context['adbot'] = AdBot.objects.all()
        if request.POST.get('date_1') and request.POST.get('date_2'):
            date_1 = dateutil.parser.parse(request.POST.get('date_1'), ignoretz=True)
            date_2 = dateutil.parser.parse(request.POST.get('date_2'), ignoretz=True)
        else:
            messages.success(request, 'Выберите даты')
            return render(request, 'ad_bot/reports.html', context)
        messages.success(request, 'Отчет успешно сформирован')
        context['report_raw'] = ReportData.objects.filter(adbot=bot_id,
                                                          date__range=(date_1, date_2),
                                                        ).order_by('-date')
        calc_data = []
        counter = 0
        for i in context['report_raw']:
            counter += 1
            calc_data.append([counter,
                              i.date,
                              i.contact_id,
                              i.agent,
                              i.price,
                              i.amount_rub,
                              i.amount_btc,
                              i.fee_btc,
                            ])
        if calc_data:
            df = pd.DataFrame(np.array(calc_data),
                              index=range(len(calc_data)),
                              columns=headers)
            context['mean_price'] = round(df['price'].mean(), 2)
            context['sum_rub'] = df['amount_rub'].sum()
            context['sum_rub_qiwi'] = context['sum_rub'] - (context['sum_rub']*Decimal(0.018))
            context['sum_btc'] = df['amount_btc'].sum()
            context['fee_sum'] = df['fee_btc'].sum()
            context['sum_all_btc'] = context['fee_sum'] + context['sum_btc']
            context['number_trades'] = counter
            context['is_data'] = '2'
        else:
            context['is_data'] = '1'

        return render(request, 'ad_bot/reports.html', context)

