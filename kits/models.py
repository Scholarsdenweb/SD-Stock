from django.db import models
from stock.models import Variant
from authapp.models import Student
from datetime import datetime

# Create your models here.
class Kits(models.Model):
    FR = 'free'
    PD ='paid'
    
    KIT_TYPE = [
        (FR, 'Free'),
        (PD, 'Paid'),
    ]
    name = models.CharField(max_length=50)
    type = models.CharField(max_length=50, choices=KIT_TYPE, default=FR)
    description = models.CharField(max_length=254, blank=True)
    academic_year = models.CharField(max_length=50)
    
    class Meta:
        verbose_name = 'Kit'
        verbose_name_plural = 'Kits'
    
    def __str__(self):
        return f'{self.name} - {self.type}'
    
    def item_count(self):
       package = KitItems.objects.filter(kit=self).count()
       return package
   
    def total_price(self):
        total = 0
        for item in KitItems.objects.filter(kit=self):
            total += item.price * item.quantity
        return total
   
class KitItems(models.Model):
    kit = models.ForeignKey(Kits, on_delete=models.CASCADE)
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = 'Kit Item'
        verbose_name_plural = 'Kit Items'
        
    def __str__(self):
        return f'{self.variant}'
        
        
class KitAllocation(models.Model): 
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    kit = models.ForeignKey('Kits', on_delete=models.CASCADE)
    kititems = models.ManyToManyField(KitItems)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Kit Allocation'
        verbose_name_plural = 'Kit Allocations'
        
    def __str__(self):
        return f'{self.student}_{self.student.enrollement}'
    
    def total_payment(self):
        total = 0
        for item in self.kititems.all():
            total += item.price * item.quantity
        return total
