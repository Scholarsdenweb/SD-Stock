from django.shortcuts import render, redirect
from authapp.forms import *
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
# Create your views here.


def register(request):
    if request.method=="POST":

        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'User registered successfully')
            return render(request, 'authapp/register.html', {'form': form})
        else:
            print(form.errors)
            messages.error(request, 'User not registered')
            return render(request, 'authapp/register.html', {'form': form})
    form = SignUpForm()


    return render(request, 'authapp/register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        form = loginForm(request.POST)
        if form.is_valid():
            print('login view')
            emp_id = form.cleaned_data['emp_id']
            password = form.cleaned_data['password']
            user = authenticate(request, emp_id=emp_id, password=password)
            if user is not None:
                login(request, user)
                next_url = request.POST.get('next') or request.GET.get('next')

                return redirect(next_url or 'dashboard:home')  # Replace with your redirect URL
            else:
                form.add_error(None, 'Invalid employee id or password')
    else:
        if request.user.is_authenticated:
            return redirect('dashboard:home')
    form = loginForm()
    return render(request, 'authapp/login.html', {'form': form})


def logout_user(request):
    logout(request)
    return redirect('authapp:login')
