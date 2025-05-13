from django import forms
from django.contrib.auth.forms import UserCreationForm
from authapp.models import StockUser

class SignUpForm(UserCreationForm):
    class Meta:
        model = StockUser
        fields = ('emp_id', 'name', 'email', 'password1', 'password2')

        widgets = {
            'emp_id': forms.TextInput(attrs={'class': 'form-control my-2'}),
            'name': forms.TextInput(attrs={'class': 'form-control my-2'}),
            'email': forms.EmailInput(attrs={'class': 'form-control my-2'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control my-2'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control my-2'})
        }

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control my-2'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control my-2'})




class loginForm(forms.Form):
    emp_id = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control my-3'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control my-3'}))