from django.contrib import admin
from .utils import log_action
from .models import AuditLog
# Register your models here.
class AllocationAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        action = "update" if change else "create"
        log_action(user=request.user, request=request, action=action, instance=obj,
                   changes={"form_data": form.cleaned_data})

    def delete_model(self, request, obj):
        log_action(user=request.user, request=request, action="delete", instance=obj)
        super().delete_model(request, obj)
        

admin.site.register(AuditLog)
