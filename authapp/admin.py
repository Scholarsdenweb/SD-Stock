from django.contrib import admin
from authapp.models import *
from stock.models import Student
from authapp.models import StockUser
from import_export import resources
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import StockUser
from .forms import StockUserCreationForm, StockUserChangeForm



# Register your models here.
# admin.py


class StockUserAdmin(BaseUserAdmin):
    form = StockUserChangeForm
    add_form = StockUserCreationForm

    list_display = ('emp_id', 'name', 'email', 'phone', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('emp_id', 'password')}),
        ('Personal info', {'fields': ('name', 'email', 'phone')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('emp_id', 'name', 'email', 'phone', 'password1', 'password2'),
        }),
    )
    search_fields = ('emp_id', 'name', 'email')
    ordering = ('emp_id',)
    filter_horizontal = ('groups', 'user_permissions',)
    
admin.site.register(StockUser, StockUserAdmin)


@admin.register(OTPCode) 
class OTPCodeAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'otp']



class StudentResource(resources.ModelResource):
    class Meta:
        model = Student
        import_id_fields = ['enrollement']
        fields = ['enrollement', 'receipt', 'name', 'date_of_birth', 'father_name', 'roll', 'batch', 'phone']
        
