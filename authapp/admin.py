from django.contrib import admin
from authapp.models import *
from stock.models import Student
from import_export import resources



# Register your models here.
admin.site.register(StockUser)


class StudentResource(resources.ModelResource):
    class Meta:
        model = Student
        import_id_fields = ['enrollement']
        fields = ['enrollement', 'receipt', 'name', 'date_of_birth', 'father_name', 'roll', 'batch', 'phone']
        