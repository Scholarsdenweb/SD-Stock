from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from authapp.decorators import is_manager

# Create your views here.
@login_required
@is_manager
def dashboard(request):
    return render(request, 'dashboard/home.html')