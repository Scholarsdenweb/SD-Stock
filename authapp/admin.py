from .models import *
from django.contrib import admin

admin.site.register(User)
admin.site.register(Roles)

class StudentAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'enrollement', 'program', 'admission_year']
    search_fields = ['name', 'enrollement']
    
    
admin.site.register(Student, StudentAdmin)


class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['id', 'user__full_name', 'emp_id', 'user__email', 'department', 'designation', 'phone']
    search_fields = ['name', 'email', 'phone', 'emp_id']
    
    fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('user','emp_id', 'phone', 'department', 'designation'),
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('user', 'emp_id', 'phone', 'department', 'designation'),
        }),
    )
    
    
admin.site.register(Employee, EmployeeAdmin)

# @admin.register(OTPCode) 
# class OTPCodeAdmin(admin.ModelAdmin):
#     list_display = ['id', 'user', 'otp']



# class StudentResource(resources.ModelResource):
#     class Meta:
#         model = Student
#         import_id_fields = ['enrollement']
#         fields = ['enrollement', 'receipt', 'name', 'date_of_birth', 'father_name', 'roll', 'batch', 'phone']
        
