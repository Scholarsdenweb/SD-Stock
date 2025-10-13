from .models import *
from django.contrib import admin

admin.site.register(User)
admin.site.register(Roles)
admin.site.register(Employee)

class StudentAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'enrollement', 'program', 'admission_year']
    search_fields = ['name', 'enrollement']
    
    
admin.site.register(Student, StudentAdmin)

# @admin.register(OTPCode) 
# class OTPCodeAdmin(admin.ModelAdmin):
#     list_display = ['id', 'user', 'otp']



# class StudentResource(resources.ModelResource):
#     class Meta:
#         model = Student
#         import_id_fields = ['enrollement']
#         fields = ['enrollement', 'receipt', 'name', 'date_of_birth', 'father_name', 'roll', 'batch', 'phone']
        
