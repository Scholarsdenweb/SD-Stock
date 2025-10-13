from django.db.models.signals import post_save, post_delete, m2m_changed, pre_delete
from django.dispatch import receiver
from stock.models import Issue, Student, Serialnumber, Stock, Allocations, Variant
from django.http import JsonResponse
from django.db import transaction
from django.db.models import F





        
        
@receiver(pre_delete, sender=Serialnumber)
def decrement_stock_on_serial_delete(sender, instance, **kwargs):
    """
    Decrement Stock quantity when a Serialnumber is deleted.
    If Stock.quantity becomes 0, delete the Stock row.
    """
    with transaction.atomic():
        qs = Stock.objects.filter(variant=instance.product_variant)

        # atomically decrement quantity if >= 1
        updated = qs.filter(quantity__gte=1).update(quantity=F('quantity') - 1)
        if not updated:
            return

        # re-fetch to check current quantity
        stock = qs.first()
        if stock and stock.quantity <= 0:
            stock.delete()
            
@receiver(pre_delete, sender=Stock)            
def delete_serial_on_stock_delete(sender, instance, **kwargs):
    """
    Delets the related serail numbers when stock is deleted.
    """
    serials = Serialnumber.objects.filter(product_variant=instance.variant)
    serials.delete()
  


@receiver(post_delete, sender=Variant)
def on_variant_delete(sender, instance, **kwargs):
    if instance.photo:
        instance.photo.delete(save=False)
