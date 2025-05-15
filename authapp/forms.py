from django import forms
from django.contrib.auth.forms import UserCreationForm
from authapp.models import StockUser

class SignUpForm(UserCreationForm):
    class Meta:
        model = StockUser
        fields = ('emp_id', 'name', 'email', 'password1', 'password2')

        widgets = {
            'emp_id': forms.TextInput(attrs={'class': 'form-control my-2', 'placeholder': 'Enter Employee ID'}),
            'name': forms.TextInput(attrs={'class': 'form-control my-2', 'placeholder': 'Enter Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control my-2', 'placeholder': 'Enter Email'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control my-2'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control my-2'}),
        }

        labels = {
            'emp_id': 'Your Employee ID*',
            'name': 'Full name',
            'email': 'Email',
            'password1': 'Password*',
            'password2': 'Confirm Password*',
        }


    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control my-2', 'placeholder': 'Enter at least 8 characters long password'})
        self.fields['password1'].label = 'Password*'
        self.fields['password2'].widget.attrs.update({'class': 'form-control my-2', 'placeholder': 'Enter same password as above'})
        self.fields['password2'].label = 'Confirm Password*'




class loginForm(forms.Form):
    emp_id = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control my-3'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control my-3'}))

    class Meta:
        model = StockUser
        fields = ['emp_id', 'password']


    def __init__(self, *args, **kwargs):
        super(loginForm, self).__init__(*args, **kwargs)
        self.fields['emp_id'].label = 'Employee ID*'
        self.fields['password'].label = 'Password*'


