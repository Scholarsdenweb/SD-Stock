# from django.db.models.signals import post_save
# from django.dispatch import receiver

# from .models import StockUser, OTPCode
# from .utils import import_and_create_student


# @receiver(post_save, sender=StockUser)
# def on_user_creation(sender, instance, created, *args, **kwargs):
#     if created:
#         OTPCode.objects.create(user=instance)