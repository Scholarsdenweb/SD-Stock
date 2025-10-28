from django.urls import path
from .views import register_emp

app_name = 'employees'

urlpatterns = [
   path('register-emp/', register_emp, name='register_emp'),
]