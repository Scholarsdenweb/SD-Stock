from django.shortcuts import render, redirect
from authapp.forms import *
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.views.generic.edit import CreateView
from stock.models import Student
from authapp.forms import StudentForm, OTPForm
from authapp.utils import import_and_create_student
from stock.send_sms import send_sms
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
                request.session['user_id'] = user.pk
                return redirect('authapp:verify_otp')
                # login(request, user)
                # next_url = request.POST.get('next') or request.GET.get('next')

                # return redirect(next_url or 'dashboard:home')  # Replace with your redirect URL
            else:
                form.fields['emp_id'].widget.attrs['class'] = 'form-control is-invalid my-2'
                form.fields['password'].widget.attrs['class'] = 'form-control is-invalid my-2'
                messages.error(request, 'Invalid username or password')
                return render(request, 'authapp/login.html', {'form': form})

    if request.user.is_authenticated:
        return redirect('dashboard:home')
                
    form = loginForm()
    return render(request, 'authapp/login.html', {'form': form})

# verify user with OTP
def verify_otp(request):
    form = OTPForm(request.POST or None)
    user_id = request.session.get('user_id')
    
    if user_id:
        user = StockUser.objects.get(pk = user_id)
        otp_obj = OTPCode.objects.get(user=user)
        
        if not request.POST:
            send_sms(
            api_key = "2MLivU4Q3tyFXr1WJcNB8l5YhzT0pAesdoIxRPGwuCSgObZmkVMbkSmGBYOAgHrNosjUhXy854JL269E", 
            message_id = '182187',
            variables_values = otp_obj.otp,
            numbers= user.phone or '', 
            sender_id="SCHDEN"
        )
        if form.is_valid():
            num = form.cleaned_data.get('otp')
            
            if str(num) == otp_obj.otp:
                otp_obj.save()
                # login the user here
                login(request, user)
                next_url = request.POST.get('next') or request.GET.get('next')
                return redirect(next_url or 'dashboard:home')
            else:
                return redirect('authapp:login') # to the otp form
    return render(request, 'authapp/otp_form.html', {'form':OTPForm})

def logout_user(request):
    logout(request)
    return redirect('authapp:login')


def add_student(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            form.save(commit=False)
            enrollement = form.cleaned_data['enrollement']
            roll = form.cleaned_data['roll']
            batch = form.cleaned_data['batch']

            student_exist = Student.objects.filter(enrollement=enrollement).first()
            if student_exist:
                messages.error(request, 'Enrollement number already exists')
                return render(request, 'authapp/add_student.html', {'form': form})
            
            # elif Student.objects.filter(roll=roll, batch=batch).exists():
            #     messages.error(request, 'Roll number already exists')
            #     form.add_error('roll', 'Roll number already exists')
            #     return render(request, 'authapp/add_student.html', {'form': form})
            
            elif Student.objects.filter(receipt=form.cleaned_data['receipt']).exists():
                messages.error(request, 'Receipt number already exists')
                return render(request, 'authapp/add_student.html', {'form': form})
            else:
                student =  form.save()
                messages.success(request, '{} with enrollement number {} added successfully'.format(student.name, student.enrollement))
                return render(request, 'authapp/success.html', {'form': form})

        else:
            form.fields['enrollement'].widget.attrs['class'] = 'form-control is-invalid my-2'
            form.fields['name'].widget.attrs['class'] = 'form-control is-invalid my-2'
            messages.error(request, 'Please fill up the required fields')
            return render(request, 'authapp/add_student.html', {'form': form})

    form = StudentForm()

    return render(request, 'authapp/add_student.html', {'form': form})
    

def import_students(request):
    if request.method == 'POST':
        form = ImportStudentForm(request.POST, request.FILES)
        if form.is_valid():
            # {'success': True, 'created': len(imported_data)}
            response = import_and_create_student(request.FILES['file'])
            if not response['success']:
                messages.error(request, response['errors'])
                return render(request, 'authapp/import_student.html', {'form': form})
            
            messages.success(request, f' {response["created"]} students added successfully')
            return render(request, 'authapp/import_student.html', {'form': form})
        else:
            form.fields['file'].widget.attrs['class'] = 'form-control is-invalid my-2'
            messages.error(request, 'Please choose the correct file format')
            return render(request, 'authapp/import_student.html', {'form': form})

    form = ImportStudentForm()
    return render(request, 'authapp/import_student.html', {'form': form})


