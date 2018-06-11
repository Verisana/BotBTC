from django.contrib import admin
from .models import AdBot, ActionLog


class AdBotAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Настройки', {'fields':
                            ['switch',
                             'price_round',
                             'executing',
                             'ad_id',
                             'name',
                             'api_keys',
                             'frequency',
                             'stop_price',
                             'step',
                             'volume_max',
                             'volume_min',
                             'page_number',
                            ]}),
        ('Объявление', {'fields':
                            ['payment_method',
                             'trade_direction',
                             'executed_at',
                             'username',
                             ]}),
    ]

    list_display = ['name',
                    'username',
                    'ad_id',
                    'switch',
                    'stop_price',
                    'executed_at',
                    ]
    save_on_top = True


class ActionLogAdmin(admin.ModelAdmin):
    fields = ['action', 'bot_model']
    list_display = ['action', 'bot_model', 'timestamp']
    list_filter = ('action', 'bot_model__name')


admin.site.register(AdBot, AdBotAdmin)
admin.site.register(ActionLog, ActionLogAdmin)
