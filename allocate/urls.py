from django.urls import path
from . import views

app_name = 'allocate'

urlpatterns = [
    path('', views.main_page, name='main'),
    path('list/', views.AllocationView.as_view(), name='allocation_list'),
    path('return/', views.ReturnView.as_view(), name='return_list'),
    path('load-variant/', views.load_variant, name='load_variant'),
]