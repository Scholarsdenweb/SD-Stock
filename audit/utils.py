from .models import AuditLog
from django.contrib.contenttypes.models import ContentType

def log_action(user=None, action="custom", request=None,
               instance=None, changes=None, extra=None):
    ip = getattr(request, "client_ip", None) if request else None
    ua = getattr(request, "user_agent", "") if request else ""
    ct = None
    obj_id = ""
    obj_repr = ""
    if instance is not None:
        ct = ContentType.objects.get_for_model(instance.__class__)
        obj_id = getattr(instance, "pk", "")
        obj_repr = str(instance)

    AuditLog.objects.create(
        user=user,
        ip_address=ip,
        user_agent=ua[:512],
        action=action,
        content_type=ct,
        object_id=str(obj_id),
        object_repr=obj_repr[:255],
        changes=changes or {},
        extra=extra or {},
    )
