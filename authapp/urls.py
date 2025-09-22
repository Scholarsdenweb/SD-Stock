from django.urls import path
from . import views

app_name = 'authapp'

urlpatterns = [
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('login/', views.Login.as_view(), name='login'),
    # path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('logout/', views.logout_view, name='logout'),
    # path('student/add/', views.add_student, name='add_student'),
    # path('student/import/', views.import_students, name='import_students'),
]