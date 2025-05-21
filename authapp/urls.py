from django.urls import path
from . import views

app_name = 'authapp'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('student/add/', views.add_student, name='add_student'),
    path('student/import/', views.import_students, name='import_students'),
]