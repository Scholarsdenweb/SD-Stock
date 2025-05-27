from django.db.models.signals import post_save, post_delete 
from django.dispatch import receiver
from stock.models import Issue, Student
from .send_sms import send_sms
from django.http import JsonResponse

@receiver(post_save, sender=Issue)
def on_kit_issue(sender, instance, created, **kwargs):
    if created:
        print(instance)
        student = Student.objects.get(enrollement=instance.enrollement)
        response = send_sms(
            api_key = "2MLivU4Q3tyFXr1WJcNB8l5YhzT0pAesdoIxRPGwuCSgObZmkVMbkSmGBYOAgHrNosjUhXy854JL269E", 
            message_id = '182187',
            variables_values = instance.enrollement,
            numbers= '7903956216', 
            sender_id="SCHDEN"
        )
        
    else:
        print("some error occured")
    
# variables_values = instance.enrollement + '|' + instance.get_issued_date() + '|' + instance.get_items(),
