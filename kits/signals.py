from django.db.models.signals import post_save
from .sms import send_sms
from .models import KitAllocation
from django.dispatch import receiver
from django.http import JsonResponse

@receiver(post_save, sender=KitAllocation)
def on_kit_allocation(sender, instance, created, **kwargs):
    if created:
        response = send_sms(
            api_key = "2MLivU4Q3tyFXr1WJcNB8l5YhzT0pAesdoIxRPGwuCSgObZmkVMbkSmGBYOAgHrNosjUhXy854JL269E", 
            message_id = '186973',
            variables_values = [', '.join(str(item.variant.name)) for item in instance.kititems.all()],
            numbers= instance.student.phone or '7903956216',
            sender_id="SCHDEN"
        )
        
        return JsonResponse({'message': 'sms sent successfully'})
        
    else:
        return JsonResponse({'message': 'error'})