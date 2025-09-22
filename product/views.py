from django.shortcuts import render
from django.views.generic.base import TemplateView

# Create your views here.
class CatelogueView(TemplateView):
    template_name = 'product/catelogue.html'