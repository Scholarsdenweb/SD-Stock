from django.contrib.auth.views import LoginView
from django.contrib.auth import logout
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.contrib.auth.forms import UserCreationForm
from django.views.generic.edit import CreateView
from .forms import SignupForm
from .models import Roles


class SignupView(CreateView):
    template_name = 'authapp/register.html'
    form_class = SignupForm
    success_url = reverse_lazy('authapp:login')
    
    # def form_valid(self, form):
    #     user = form.save()
    #     role = Roles.objects.get(id=2)
    #     user.role.add(role)
    #     user.save()
    #     return super().form_valid(form)

class Login(LoginView):
    template_name = 'authapp/login.html'
    
    def get_success_url(self):
        return reverse_lazy('stock:create_stock')
    
    
def logout_view(request):
    logout(request)
    return render(request, 'index.html')

