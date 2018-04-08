from django.contrib import admin
from .models import AdBot, ActionLog


class AdBotAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Настройки', {'fields':
                            ['switch',
                             'ad_id',
                             'name',
                             'api_keys',
                             'frequency',
                             'stop_price',
                             'step',
                             'volume_max',
                             'volume_min',
                            ]}),
        ('Объявление', {'fields':
                            ['payment_method',
                             'trade_direction',
                             'executed_at',
                             'username',
                             ]}),
    ]

    list_display = ['name',
                    'ad_id',
                    'switch',
                    'stop_price',
                    'executed_at',
                    ]


class ActionLogAdmin(admin.ModelAdmin):
    fields = ['action', 'bot_model']
    list_display = ['action', 'bot_model', 'timestamp']
    list_filter = ('action', 'bot_model__name')


admin.site.register(AdBot, AdBotAdmin)
admin.site.register(ActionLog, ActionLogAdmin)
