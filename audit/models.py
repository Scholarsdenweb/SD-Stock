from django.db import models

# Create your models here.

# app: audit/models.py
from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import JSONField  # if using Postgres
# for cross-db, use models.JSONField in Django 3.1+

class AuditLog(models.Model):
    ACTION_CHOICES = [
        ("create", "Create"),
        ("update", "Update"),
        ("delete", "Delete"),
        ("login", "Login"),
        ("logout", "Logout"),
        ("custom", "Custom"),
    ]

    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=512, blank=True, default="")
    action = models.CharField(max_length=32, choices=ACTION_CHOICES)
    content_type = models.ForeignKey(ContentType, null=True, blank=True, on_delete=models.SET_NULL)
    object_id = models.CharField(max_length=255, blank=True, default="")
    object_repr = models.CharField(max_length=255, blank=True, default="")
    changes = models.JSONField(null=True, blank=True) 
    extra = models.JSONField(null=True, blank=True)

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
        models.Index(fields=["user"]),
        models.Index(fields=["content_type","object_id"]),
        models.Index(fields=["action"]),
    ]
