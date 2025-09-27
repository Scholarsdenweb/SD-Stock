from .models import User
from authapp.models import Roles
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
def is_manager(view_func):
    def wrapper_func(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('authapp:login')
        
        roles = request.user.role.all().values_list('id', flat=True)
        if Roles.MANAGER in roles: 
            return view_func(request, *args, **kwargs)
        else:
            return HttpResponseForbidden("You are not authorized")
    return wrapper_func
