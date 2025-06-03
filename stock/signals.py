from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch import receiver
from stock.models import Issue, Student
from .send_sms import send_sms
from django.http import JsonResponse

# @receiver(post_save, sender=Issue)
# def on_kit_issue(sender, instance, created, **kwargs):
#     if created:
#         # student = Student.objects.get(enrollement=instance.enrollement)
#         # student = instance.student
#         # print('from signal', instance.items.all())
#         response = send_sms(
#             api_key = "2MLivU4Q3tyFXr1WJcNB8l5YhzT0pAesdoIxRPGwuCSgObZmkVMbkSmGBYOAgHrNosjUhXy854JL269E", 
#             message_id = '186973',
#             variables_values = instance.items.all(),
#             numbers= instance.student.phone or '7903956216', 
#             sender_id="SCHDEN"
#         )
        
#     else:
#         return JsonResponse({'message': 'error'})
    
# variables_values = instance.enrollement + '|' + instance.get_issued_date() + '|' + instance.get_items(),

@receiver(m2m_changed, sender=Issue.items.through)
def on_kit_issue(sender, instance, **kwargs):
    if kwargs['action'] == 'post_add':
        # student = Student.objects.get(enrollement=instance.enrollement)
        response = send_sms(
            api_key = "2MLivU4Q3tyFXr1WJcNB8l5YhzT0pAesdoIxRPGwuCSgObZmkVMbkSmGBYOAgHrNosjUhXy854JL269E", 
            message_id = '186973',
            variables_values = instance.get_items(),
            numbers= instance.student.phone or '7903956216', 
            sender_id="SCHDEN"
        )