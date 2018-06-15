from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin


class IndexView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'index.html'
