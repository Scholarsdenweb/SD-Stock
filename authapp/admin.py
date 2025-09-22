from .models import *
from django.contrib import admin

admin.site.register(User)
admin.site.register(Roles)
admin.site.register(Employee)



# @admin.register(OTPCode) 
# class OTPCodeAdmin(admin.ModelAdmin):
#     list_display = ['id', 'user', 'otp']



# class StudentResource(resources.ModelResource):
#     class Meta:
#         model = Student
#         import_id_fields = ['enrollement']
#         fields = ['enrollement', 'receipt', 'name', 'date_of_birth', 'father_name', 'roll', 'batch', 'phone']
        
