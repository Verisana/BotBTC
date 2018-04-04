from django.shortcuts import render
from django.views import generic, View
from .models import AdBot
from botbtc import hmac_auth
import json
import requests


class IndexView(View):
    http_method_names = ['get', 'post']

    def get(self, request, *args, **kwargs):
        context = {}
        adbot_inst = AdBot.objects.get(name='ad_bot_rw')
        adbot_inst.api_connector_init()
        adbot_inst.check_ads()
        return render(request, 'ad_bot/index.html', context)


class SettingsView(generic.TemplateView):
    pass
