from django.urls import path
from . import views

app_name = 'catalogue'

urlpatterns = [
    path('', views.main, name="main"),
    path('category/add/', views.CreateCategory.as_view(), name='add_category'),
    path('item/add/', views.ItemCreateView.as_view(), name='add_item'),
    path('variant/add/', views.CreateVariant.as_view(), name='add_variant'),
]