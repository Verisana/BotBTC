from django.contrib import admin
from .models import AdBot, ActionLog


class AdBotAdmin(admin.ModelAdmin):
    fields = [
        'name',
        'username',
        'api_keys',
        'stop_price',
        'step',
        'volume',
        'switch',
        'frequency',
        'payment_method',
        'trade_direction',
        'ad_id']
    list_display = ['name', 'ad_id', 'switch']


class ActionLogAdmin(admin.ModelAdmin):
    field = ['actions', 'timestamp', 'request_method', 'request_url',
             'response_data', 'response_code'
             ]
    list_display = ['request_method', 'request_url', 'timestamp']


admin.site.register(AdBot, AdBotAdmin)
admin.site.register(ActionLog, ActionLogAdmin)
