from django.shortcuts import render, redirect
from .forms import EmployeeCreationForm
from authapp.models import Employee, User, Roles
from django.db import transaction
from django.contrib import messages

# Create your views here.
from django.db import transaction, IntegrityError
from audit.utils import log_action

def register_emp(request):
    if request.method == 'POST':
        form = EmployeeCreationForm(request.POST)
        
        if form.is_valid():
            post_data = form.cleaned_data

            user_form_data = {
                'full_name': post_data['full_name'],
                'email': post_data['email'],
            }

            emp_form_data = {
                'emp_id': post_data['emp_id'], 
                'phone': post_data['phone'],
                'department': post_data['department'],
                'designation': post_data['designation'],
            }

            roles = post_data.get('role')

            with transaction.atomic():
                user, created = User.objects.get_or_create(**user_form_data)

                if not created:
                    messages.error(request, 'User with this email already exists.')
                    return render(request, 'employees/employees.html', {'form': form})

                # create user first
                user.set_password('dummy_password')
                user.save()

                # assign roles
                user.role.add(*roles)

                Employee.objects.create(user=user, **emp_form_data)

                messages.success(request, 'Employee Registered Successfully')
                log_action(user=request.user, request=request, action="create", instance=user)
                return redirect('employees:register_emp')

        else:
            messages.error(request, 'Please correct the highlighted errors.')
            return render(request, 'employees/employees.html', {'form': form})

    return render(request, 'employees/employees.html', {'form': EmployeeCreationForm()})
