from django.urls import path
from . import views

app_name = 'dashoboard'

urlpatterns = [
    path('', views.dashboard, name='home'),
]