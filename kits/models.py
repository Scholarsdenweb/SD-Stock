from django.db import models
from stock.models import Variant

# Create your models here.
class Kits(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=254, blank=True)
    academic_year = models.CharField(max_length=50)
    
    def __str__(self):
        return f'{self.name} - {self.academic_year}'
    
class KitItems(models.Model):
    kit = models.ForeignKey(Kits, on_delete=models.CASCADE)
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)