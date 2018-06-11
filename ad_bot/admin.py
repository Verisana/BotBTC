from django.contrib import admin
from .models import AdBot, OpenTrades


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
                             'enable_autoposting',
                             'greetings_text',
                             'farewell_text',
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
                    'enable_autoposting',
                    'price_round',
                    'stop_price',
                    'executed_at',
                    ]
    save_on_top = True

class OpenTradesAdmin(admin.ModelAdmin):
    fields = ['trade_id', 'username', 'delete_flag']
    list_display = ['trade_id', 'username', 'delete_flag']
    save_on_top = True

admin.site.register(AdBot, AdBotAdmin)
admin.site.register(OpenTrades, OpenTradesAdmin)
