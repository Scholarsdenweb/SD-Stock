from django import forms
from django.forms import inlineformset_factory
from authapp.models import Employee, User, Roles
from django.core.validators import RegexValidator


phone_validator = RegexValidator(
    r"^(\+\d{2})?\d{10}$",
    message="Please enter a valid mobile number. Example +917925666666 or 7925666666"
)

class EmployeeCreationForm(forms.Form):
    full_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control my-2'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control my-2'}), required=False)
    role = forms.ModelChoiceField(queryset=Roles.objects.all(), widget=forms.Select(attrs={'class': 'form-select my-2', 'multiple': True}), empty_label=None)
    emp_id = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control my-2'}), label='Employee ID')
    
    phone = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control my-2'}), required=False, validators=[phone_validator])
    
    department = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control my-2'}), required=False)
    
    designation = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control my-2'}), required=False)
