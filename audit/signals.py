# app: audit/signals.py
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django.forms.models import model_to_dict
from .utils import log_action
from django.apps import apps
from django_currentuser.middleware import (get_current_user, get_current_authenticated_user)

APPS_TO_TRACK = ["stock", "authapp", "allocate"] 


TRACK_MODELS = tuple(
    model
    for label in APPS_TO_TRACK
    for model in apps.get_app_config(label).get_models()
)
@receiver(pre_save)
def track_pre_save(sender, instance, **kwargs):
    if sender not in TRACK_MODELS:
        return
    if instance.pk:
        # existing object; store prior state on instance for post_save
        try:
            old = sender.objects.get(pk=instance.pk)
            instance._old_state = model_to_dict(old)
        except sender.DoesNotExist:
            instance._old_state = None

@receiver(post_save)
def track_post_save(sender, instance, created, **kwargs):
    if sender not in TRACK_MODELS:
        return
    old = getattr(instance, "_old_state", None) or {}
    new = model_to_dict(instance)
    action = "create" if created else "update"
    changes = {"old": old, "new": new}
    # you won't have request here; pass user via threadlocals or skip user
    log_action(user=get_current_user(), request=None, action=action, instance=instance, changes=changes)

@receiver(post_delete)
def track_delete(sender, instance, **kwargs):
    if sender not in TRACK_MODELS:
        return
    log_action(user=get_current_user(), request=None, action="delete", instance=instance, changes={"old": model_to_dict(instance)})
