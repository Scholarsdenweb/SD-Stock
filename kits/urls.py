from django.urls import path
from . import views

app_name = 'kit'

urlpatterns = [
    path('', views.StudentIndex.as_view(), name='student_index'),
    path('create-kit/', views.KitsCreateView.as_view(), name='create_kit'),
    path('create-kititems/', views.kititem_view, name='create_kititems'),
    path('kititem-form/', views.get_kititem_form, name='kititem_form'),
]