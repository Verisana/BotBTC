from django.contrib import admin
from django.urls import path, reverse
from django.conf.urls import include
from django.conf import settings
from django.views.generic.base import RedirectView


urlpatterns = [
    path('admin/', admin.site.urls),

    path('', RedirectView.as_view(pattern_name='ad_bot:index')),

    path('ad_bot/', include('ad_bot.urls')),
    path('profiles/', include('profiles.urls')),
]

admin.site.site_header = 'LocalBitcoins_bot Administration'

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
