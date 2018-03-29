from django.contrib import admin
from django.urls import path
from django.conf.urls import include
from django.conf import settings
from .views import IndexView


urlpatterns = [
    path('admin/', admin.site.urls),

    path('', IndexView.as_view(), name='index'),

    path('ad_bot/', include('ad_bot.urls')),
    path('profiles/', include('profiles.urls')),
]

admin.site.site_header = 'LocalBitcoins_bot Administration'

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
