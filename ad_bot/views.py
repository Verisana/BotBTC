import dateutil.parser
from django.shortcuts import render, reverse, redirect
from django.views import generic, View
from .models import AdBot
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
        context = {}
        bot_id = int(request.POST.get('adbot_chooser'))
        date_1 = dateutil.parser.parse(request.POST.get('date_1'), ignoretz=True)
        date_2 = dateutil.parser.parse(request.POST.get('date_2'), ignoretz=True)
        context['result'] = calculate_report.delay(bot_id,
                               request.POST.get('date_1'),
                               request.POST.get('date_2'),
                            )
        context['adbot'] = AdBot.objects.all()
        messages.success(request, 'Отчет успешно сформирован')
        return render(request, 'ad_bot/reports.html', context)
