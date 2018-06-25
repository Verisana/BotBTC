from django.contrib import admin
from .models import AdBot, OpenTrades, ReportData, AdBotTechnical


class AdBotAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Настройки', {'fields':
                            ['switch',
                             'price_round',
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
                    ]
    save_on_top = True

class OpenTradesAdmin(admin.ModelAdmin):
    fields = ['trade_id', 'username', 'adbot']
    list_display = ['trade_id', 'username', 'adbot']

class ReportDataAdmin(admin.ModelAdmin):
    fields = ['date',
              'adbot',
              'contact_id',
              'agent',
              'price',
              'amount_rub',
              'amount_btc',
              'fee_btc',
              ]
    list_display = ['date',
                    'adbot',
                    'contact_id',
                    'agent',
                    'price',
                    'amount_rub',
                    'amount_btc',
                    'fee_btc',
                ]
    list_filter = ['adbot', 'date']
    date_hierarchy = 'date'


"""class AdBotTechnicalAdmin(admin.ModelAdmin):
    fields = ['adbot',
              'executed_at',
              'executing',
              'message_executing',
              'message_executed_at',
              'message_frequency',
            ]
    list_display = ['adbot',
            'executed_at',
            'executing',
            'message_executing',
            'message_executed_at',
            'message_frequency',
        ] """


admin.site.register(AdBot, AdBotAdmin)
admin.site.register(OpenTrades, OpenTradesAdmin)
admin.site.register(ReportData, ReportDataAdmin)
#admin.site.register(AdBotTechnical, AdBotTechnicalAdmin)
