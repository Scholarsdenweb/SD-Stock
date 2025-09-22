from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Employee, User, Roles
from django import forms

class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['full_name', 'email', 'password1', 'password2']
        
    def save(self, commit=True):
        user = super().save(commit=commit)
        role = Roles.objects.get(id=2)
        user.role.add(role)
        user.user_permissions.clear()
        
        if commit:
            user.save()
  
        return user


# class ImportStudentForm(forms.Form):
#     file = forms.FileField(label='Upload Excel File', required=True, widget=forms.ClearableFileInput(attrs={'class': 'form-control my-2'}))

#     def clean_file(self):
#         file = self.cleaned_data.get('file')
        
#         if file and not file.name.endswith('.xlsx'):
#             raise forms.ValidationError("Only .xlsx files are allowed.")
#         return file
    
    
    
# class OTPForm(forms.ModelForm):
#     class Meta:
#         model = OTPCode
#         fields = ['otp']
        
#         widgets = {
#             'otp':forms.widgets.TextInput(attrs={'class':'form-control mt-2', 'placeholder':'Enter OTP'})
#         }
        
#         labels = {
#             'otp':"Enter OTP sent to your mobile"
#         }