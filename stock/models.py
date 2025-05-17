from django import forms
from django.db import models
from datetime import datetime
from django.core.exceptions import ValidationError
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.validators import RegexValidator


User = get_user_model()




# Create your models here.
SIZE_CHOICES = (
    ('s', 'S'),
    ('m', 'M'),
    ('l', 'L'),
    ('xl', 'XL'),
    ('xxl', 'XXL'),
    ('small', 'Small'),
    ('big', 'Big')
)
class Item(models.Model):

    T_SHIRT_S = 's'
    T_SHIRT_M = 'm'
    T_SHIRT_L = 'l'
    T_SHIRT_XL = 'xl'
    T_SHIRT_XXL = 'xxl'
    SMALL = 'small'
    BIG= 'big'
    

    SIZE_CHOICES = (
    (T_SHIRT_S, 'S'),
    (T_SHIRT_M, 'M'),
    (T_SHIRT_L, 'L'),
    (T_SHIRT_XL, 'XL'),
    (T_SHIRT_XXL, 'XXL'),
    (SMALL, 'Small'),
    (BIG, 'Big'),
    (None, 'NA')

    )

    name = models.CharField(max_length=50)
    description = models.CharField(max_length=254, null=True, blank=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=0)
    size = models.CharField(max_length=10, null=True, blank=True, choices=SIZE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.size is None:
            return f"{self.name.capitalize()} - Size: N/A"
        return f"{self.name.capitalize()} - Size: {self.size.upper()}"

    def save(self, *args, **kwargs):
        if Item.objects.filter(name=self.name, size=self.size, unit_price=self.unit_price).exclude(pk=self.pk).exists():
            raise ValidationError("Item with the same name, size, and unit price already exists.")
        super().save(*args, **kwargs)


            

    def get_absolute_url(self):
        return reverse('stock:item_detail', [self.pk])   
    


class Purchase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Purchased by')
    item = models.ForeignKey(Item, on_delete=models.CASCADE,  verbose_name='Item')
    quantity = models.PositiveIntegerField(default=1)
    payment = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Purchased on')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Last updated')
    supplier = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return str(self.item.name) 
    
    

    def get_absolute_url(self):
        return reverse('stock:purchase_detail', args=[self.pk])


class Stock(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stock_item = models.ForeignKey(Item, on_delete=models.CASCADE, )
    created_at = models.DateTimeField(auto_now_add=True)
    date = models.DateField(default=datetime.now)
    update_at = models.DateTimeField(auto_now=True)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.stock_item.name} x {self.quantity}"
    

    

class Student(models.Model):
    enrollement = models.CharField(max_length=15, unique=True, validators=[RegexValidator(r'^\d+$')])
    name = models.CharField(max_length=100)
    batch = models.CharField(max_length=50, null=True, blank=True)
    roll = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.enrollement
    

    def clean(self):
        super().clean()
        print(self.enrollement)



class Issue(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Issuing autority") 
    enrollement = models.CharField(max_length=20, verbose_name="Enrollement Number")
    items = models.ManyToManyField(Item,  related_name="kit_items")
    quantity = models.PositiveIntegerField(default=1)
    issue_date = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(default=True)

    def __str__(self):
        items = ", ".join([str(item) for item in self.items.all()])
        return f"{self.enrollement} - {items }" 
    
    def get_items(self):
        return ", ".join([str(item.name.capitalize()) for item in self.items.all()])

    def get_absolute_url(self):
        return reverse('stock:issue_detail', args=[self.pk])
    
    def get_student_name(self):
        try:
            student = Student.objects.get(enrollement=self.enrollement)
            return student.name
        except Student.DoesNotExist:
           return None
        
    def get_student(self):
        try:
            student = Student.objects.get(enrollement=self.enrollement)
            return student
        except Student.DoesNotExist:
           return None



class Transaction(models.Model):
    PURCHASE = 'PU'
    ISSUE = 'IS'
    RETURN = 'RE'
    ADJUSTMENT = 'AD'

    TRANSACTION_TYPE = [
        (PURCHASE, 'Purchase'),
        (ISSUE, 'Issue'),
        (RETURN, 'Return'),
    ]

    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=2, choices=TRANSACTION_TYPE)
    quantity = models.PositiveIntegerField(default=1)
    reference_id = models.PositiveIntegerField(default=0)
    reference_model = models.CharField(max_length=50, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    manager = models.ForeignKey(User, on_delete=models.CASCADE,  default=User)
    created_at = models.DateTimeField(auto_now_add=True)


    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.item} x {self.quantity}"
    

    @classmethod
    def record_transaction(cls, item, transaction_type, quantity, reference_obj, user):
        """Helper method to record any stock transaction"""
        return cls.objects.create(
            item=item,
            transaction_type=transaction_type,
            quantity=quantity,
            reference_id=reference_obj.id,
            reference_model=reference_obj.__class__.__name__,
            notes = "{}".format(transaction_type),
            manager=user
        )


