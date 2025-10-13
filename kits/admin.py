from django.contrib import admin
from kits.models import *
# Register your models here.


class KitAdmin(admin.ModelAdmin):
    list_display = ['id','name', 'type', 'academic_year', 'description']
    search_fields = ['name', 'academic_year']
    
admin.site.register(Kits, KitAdmin)


class KitItemAdmin(admin.ModelAdmin):
    list_display = ['id','kit', 'variant', 'quantity']
    search_fields = ['kit', 'variant']
    
admin.site.register(KitItems, KitItemAdmin)


class KitAllocationAdmin(admin.ModelAdmin):
    list_display = ['id','student', 'student__enrollement', 'student__admission_year', 'kit', 'kit__type']
    search_fields = ['student']
    
admin.site.register(KitAllocation, KitAllocationAdmin)