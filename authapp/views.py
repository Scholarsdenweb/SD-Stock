from django.shortcuts import render, redirect
from authapp.forms import *
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
# Create your views here.


def register(request):
    if request.method=="POST":

        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'User registered successfully')
            next_url = request.POST.get('next') or request.GET.get('next')
            return redirect(next_url or 'dashboard:home')  # Replace with your redirect URL
        else:
            for f in form.fields:
               if form[f].errors:
                #    form[f].field.widget.attrs['class'] = 'form-control is-invalid'
                   form[f].field.widget.attrs.update({'class': 'form-control is-invalid'})
               else:
                #    form[f].field.widget.attrs['class'] = 'form-control is-valid'
                   form[f].field.widget.attrs.update({'class': 'form-control is-valid'})
            return render(request, 'authapp/register.html', {'form': form})
    form = SignUpForm()


    return render(request, 'authapp/register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        form = loginForm(request.POST)
        if form.is_valid():
            emp_id = form.cleaned_data['emp_id']
            password = form.cleaned_data['password']
            user = authenticate(request, emp_id=emp_id, password=password)
            if user is not None:
                login(request, user)
                next_url = request.POST.get('next') or request.GET.get('next')

                return redirect(next_url or 'dashboard:home')  # Replace with your redirect URL
            else:
                form.fields['emp_id'].widget.attrs['class'] = 'form-control is-invalid my-2'
                form.fields['password'].widget.attrs['class'] = 'form-control is-invalid my-2'
                messages.error(request, 'Invalid username or password')
                return render(request, 'authapp/login.html', {'form': form})


                
    form = loginForm()
    return render(request, 'authapp/login.html', {'form': form})


def logout_user(request):
    logout(request)
    return redirect('authapp:login')


def hxtest(request):
   
    if request.method == 'POST':
        print(request.POST)
        data = request.POST.get('text')
        return HttpResponse(f"<p style='color:green'>{data}</p>")

    return render(request, 'authapp/hxtest.html')
