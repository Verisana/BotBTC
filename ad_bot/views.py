from django.shortcuts import render, reverse, redirect
from django.views import generic, View
from .models import AdBot, ActionLog
from .tasks import adbot_runner
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.mixins import LoginRequiredMixin


class IndexView(LoginRequiredMixin, View):
    http_method_names = ['get', 'post']
    login_url = '/profiles/login/'

    def get(self, request, *args, **kwargs):
        context = {}
        context['adbot'] = AdBot.objects.filter(username=request.user.id).order_by('name')
        context['actionlist'] = ActionLog.objects.all()
#        b = AdBot.objects.get(ad_id=720202)
#        b.api_connector_init()
#        from remote_pdb import RemotePdb; RemotePdb('127.0.0.1', 4444).set_trace()
#        b.check_ads()
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
