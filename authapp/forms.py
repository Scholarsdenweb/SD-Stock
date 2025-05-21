from django import forms
from django.contrib.auth.forms import UserCreationForm
from authapp.models import StockUser
from stock.models import Student


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


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = '__all__'

        labels = {
            'enrollement': 'Enrollement Number*',
            'name': 'Full Name*',
            'roll': 'Roll Number',
        }

        widgets = {
            'enrollement': forms.TextInput(attrs={'class': 'form-control my-2', 'placeholder': 'Enter Enrollement Number'}),
            'name': forms.TextInput(attrs={'class': 'form-control my-2', 'placeholder': 'Enter Full Name'}),
            'roll': forms.TextInput(attrs={'class': 'form-control my-2', 'placeholder': 'Enter Roll Number'}),
            'batch': forms.TextInput(attrs={'class': 'form-control my-2', 'placeholder': 'Enter Your Batch'}),

        }

        def clean(self, *args, **kwargs):
            super().clean()
            enrollement = self.cleaned_data.get('enrollement')
            roll = self.cleaned_data.get('roll')
            batch = self.cleaned_data.get('batch')


class ImportStudentForm(forms.Form):
    file = forms.FileField(label='Upload Excel File', required=True, widget=forms.ClearableFileInput(attrs={'class': 'form-control my-2'}))

    def clean_file(self):
        file = self.cleaned_data.get('file')
        
        if file and not file.name.endswith('.xlsx'):
            raise forms.ValidationError("Only .xlsx files are allowed.")
        return file