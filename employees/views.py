from django.shortcuts import render
from .forms import EmployeeCreationForm
from authapp.models import Employee, User, Roles
from django.db import transaction
from django.contrib import messages

# Create your views here.
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

                if created:
                    dummy_password = 'dummy_password'
                    user.set_password(dummy_password)
                    user.save()

                    for role in roles:
                        user.role.add(role)

                    Employee.objects.create(user=user, **emp_form_data)

                    messages.success(request, 'Employee Registered Successfully')
                else:
                    messages.error(request, 'Employee Already Exists')
        else:
            context = {'form': form}
            messages.error(request, 'Please correct the highlighted errors.')
            return render(request, 'employees/employees.html', context)

    form = EmployeeCreationForm()

    context = {'form': form}
    return render(request, 'employees/employees.html', context)