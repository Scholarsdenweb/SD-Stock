from django.urls import path
from . import views

app_name = 'catalogue'

urlpatterns = [
    path('', views.main, name="main"),
    path('category/add/', views.CreateCategory.as_view(), name='add_category'),
    path('delete/category/<int:pk>/', views.delete_category, name="delete_category"),
    path('item/add/', views.ItemCreateView.as_view(), name='add_item'),
    path('variant/add/', views.CreateVariant.as_view(), name='add_variant'),
    path('update-variant/<int:pk>/', views.UpdateVariant.as_view(), name='update_variant'),
    path('update-item/<int:pk>/', views.UpdateItem.as_view(), name='update_item'),
    path('update-category/<int:pk>/', views.UpdateCategory.as_view(), name='update_category'),
]