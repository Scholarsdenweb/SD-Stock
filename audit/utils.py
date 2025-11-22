from .models import AuditLog
from django.contrib.contenttypes.models import ContentType
import datetime
from decimal import Decimal
from django.db.models import Model
from django.db.models.query import QuerySet




def json_safe(data: dict):
    safe = {}
    for key, value in data.items():
        if isinstance(value, (datetime.date, datetime.datetime)):
            safe[key] = value.isoformat()
        elif isinstance(value, Decimal):
            safe[key] = float(value)
        elif isinstance(value, Model):       # For FK field instances
            safe[key] = str(value)
        elif isinstance(value, QuerySet):    # ManyToMany
            safe[key] = [str(v) for v in value]
        else:
            safe[key] = value
    return safe

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
