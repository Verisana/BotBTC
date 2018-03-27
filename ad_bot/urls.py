from django.urls import path
from .views import IndexView, SettingsView

app_name = 'ad_bot'
urlpatterns = [
    path('index', IndexView.as_view(), name='index'),
    path('settings/', SettingsView.as_view(), name='settings'),
]
