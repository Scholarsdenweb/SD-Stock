from django.contrib.auth.views import LoginView
from django.contrib.auth import logout
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import CreateView
from .forms import SignupForm
from .models import Roles
from audit.utils import log_action


class SignupView(CreateView):
    template_name = 'authapp/register.html'
    form_class = SignupForm
    success_url = reverse_lazy('authapp:login')
    
    def form_valid(self, form):
        log_action(self.request.user, request=self.request, action = 'Created user', instance=form.instance)
        return super().form_valid(form)

class Login(LoginView):
    template_name = 'authapp/login.html'
    
    def get_success_url(self):
        return reverse_lazy('stock:create_stock')
    
    def form_valid(self, form):
        response = super().form_valid(form)

        if self.request.user.is_authenticated:
            log_action(
                self.request.user,
                request=self.request,
                action='Login',
                instance=self.request.user
            )
        return response

    
    
def logout_view(request):
    if request.user.is_authenticated:
        log_action(
            request.user,
            request=request,
            action='Login',
            instance=request.user
        )
    logout(request)
    return render(request, 'index.html')

