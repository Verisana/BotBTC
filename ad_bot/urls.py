from django.urls import path
from .views import IndexView, SettingsView, SwitchView, ReportsView

app_name = 'ad_bot'
urlpatterns = [
    path('index', IndexView.as_view(), name='index'),
    path('settings/', SettingsView.as_view(), name='settings'),
    path('switch/', SwitchView.as_view(), name='switch'),
    path('reports/', ReportsView.as_view(), name='reports'),
]
