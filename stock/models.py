from django import forms
from django.db import models
from datetime import datetime
from django.core.exceptions import ValidationError
from django.conf import settings
from django.contrib import messages
from django.urls import reverse
from django.core.validators import RegexValidator
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db.models.functions import Lower
from django.db.models import F
from authapp.models import User
from django.core.validators import MinValueValidator



class Category(models.Model):
    DR = 'durable'
    CN = 'consumable'
    
    TYPE_CHOICES = (
        (DR, 'Durable'),
        (CN, 'Consumable'),
    )
    
    name = models.CharField(max_length=50)
    # cat_type = models.CharField(max_length=10, choices=TYPE_CHOICES, verbose_name='Category Type')
    description = models.CharField(max_length=254, blank=True)
    
    
    class Meta:
       verbose_name_plural = 'Categories'
       verbose_name = 'Category'
    def __str__(self):
        return self.name
    
    
    
        
# Create your models here.

class Variant(models.Model):
    product = models.ForeignKey('Item', related_name='product', on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    sku = models.CharField(max_length=50, blank=True)
    meta_data = models.JSONField(null=True, blank=True,)
    is_serialized = models.BooleanField(default=False, verbose_name='Have serial number')
    is_active = models.BooleanField(default=True)
    def __str__(self):
        return self.name
    
    def get_serial_number(self):
        serial_number_obj = Serialnumber.objects.filter(product_variant=self)
        return serial_number_obj

    
class Item(models.Model):
    name = models.CharField(max_length=50)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    variant = models.ManyToManyField(Variant, blank=True)
    code = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        # if self.size is None:
        #     return f"{self.name.capitalize()}"
        return f"{self.name.capitalize()}"

    def save(self, *args, **kwargs):
        self.name = self.name.lower()
        if Item.objects.filter(name=self.name).exclude(pk=self.pk).exists():
            raise ValidationError("This item is already added.")
        super().save(*args, **kwargs)


            

    def get_absolute_url(self):
        return reverse('stock:item_detail', [self.pk])   
    





class Stock(models.Model):
    location = models.ForeignKey('Location', on_delete=models.CASCADE)
    variant = models.ForeignKey("Variant", related_name='item_variant', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.variant.product.name).capitalize()
    
    @property
    def get_absolute_url(self):
        return reverse("stock:item_detail", kwargs={"pk": self.pk})
    
    class Meta:
        ordering = [Lower('variant__product__name')]
    
        
    # def get_items(self):
    #     return self.stock_item
    
    # def in_stock(self):
    #     if self.quantity > 0:
    #         return dict(status=True, quantity=self.quantity)
    #     return dict(status=False, quantity=self.quantity)
    



class Student(models.Model):
    enrollement = models.CharField(max_length=15, unique=True, null=True, blank=True)
    receipt = models.CharField(max_length=5, null=True, blank=True, unique=True, validators=[RegexValidator(r'^\d+$')])
    name = models.CharField(max_length=100)
    father_name = models.CharField(max_length=100, null=True, blank=True, verbose_name="Father's name")
    batch = models.CharField(max_length=50, null=True, blank=True)
    roll = models.CharField(max_length=50, null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True, validators=[RegexValidator(r'^(\+?\d{2})?\d{10}$')])
    date_of_birth = models.DateField(null=True, blank=True)
    

    def __str__(self):
        return self.name
    

    def clean(self):
        super().clean()
        print(self.enrollement)
        
    def get_dob(self):
        if self.date_of_birth:
            return self.date_of_birth.strftime("%d-%m-%Y")
        return None
    
    def display_field(self, field):
        val = getattr(self, field)
        return val if val not in [None, ''] else "N/A"
    
    
    
class IssueItem(models.Model):
    issue = models.ForeignKey("Issue", on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.item.name} x {self.quantity}"



class Issue(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Issuing autority") 
    enrollement = models.CharField(max_length=20, verbose_name="Enrollement Number")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, blank=True)
    items = models.ManyToManyField(Item, through=IssueItem, related_name="kit_items")
    quantity = models.PositiveIntegerField(default=0)
    issue_date = models.DateTimeField(auto_now_add=True)
    last_upated = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=True)
    send_message = models.BooleanField(default=False)

    def __str__(self):
        items = ", ".join([str(item) for item in self.items.all()])
        return f"{items}" 
    

    def get_issued_date(self):
        return self.issue_date.strftime("%d-%m-%Y %H:%M:%S")
    
    def get_items(self):
        return ", ".join([str(item) for item in self.items.all()])

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
       

# class Transaction(models.Model):
#     PURCHASE = 'PU'
#     ISSUE = 'IS'
#     RETURN = 'RE'
#     EXCHANGE = 'AD'

#     TRANSACTION_TYPE = [
#         (PURCHASE, 'Purchase'),
#         (ISSUE, 'Issue'),
#         (RETURN, 'Return'),
#         (EXCHANGE, 'Exchange'),
#     ]

#     item = models.ForeignKey(Item, on_delete=models.CASCADE)
#     transaction_type = models.CharField(max_length=2, choices=TRANSACTION_TYPE)
#     quantity = models.PositiveIntegerField(default=1)
#     reference_id = models.PositiveIntegerField(default=0)
#     reference_model = models.CharField(max_length=50, null=True, blank=True)
#     notes = models.TextField(null=True, blank=True)
#     manager = models.ForeignKey(User, on_delete=models.CASCADE,  default=User)
#     created_at = models.DateTimeField(auto_now_add=True)


#     class Meta:
#         ordering = ['-created_at']

#     def __str__(self):
#         return f"{self.get_transaction_type_display()} - {self.item} x {self.quantity}"
    

#     @classmethod
#     def record_transaction(cls, item, transaction_type, quantity, reference_obj, user):
#         """Helper method to record any stock transaction"""
#         return cls.objects.create(
#             item=item,
#             transaction_type=transaction_type,
#             quantity=quantity,
#             reference_id=reference_obj.id,
#             reference_model=reference_obj.__class__.__name__,
#             notes = "{}".format(transaction_type),
#             manager=user
#         )
        
     
     
class Location(models.Model):
    ST = 'store'
    RM = 'room'
    LB = 'lab'
    CL = 'classroom'
    
    LOCATION_TYPE = [
        (ST, 'Store'),
        (RM, 'Room'),
        (LB, 'Lab'),
        (CL, 'Classroom'),
    ]
    name = models.CharField(max_length=50)
    loc_type = models.CharField(max_length=50, choices=LOCATION_TYPE)
    
    
    def __str__(self):
        return self.name
    
    
    
    
class Serialnumber(models.Model):
    NS = 'in stock'
    AL = 'allocated'
    SC = 'scrapped'
    
    STATUS = [
        (NS, 'In Stock'),
        (AL, 'Allocated'),
        (SC, 'Scrapped'),
    ]
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    product_variant = models.ForeignKey(Variant, on_delete=models.CASCADE)
    serial_number = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=50, choices=STATUS, default=NS)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    
    def __str__(self):
        return str(self.serial_number)
    
    def get_content_object_model(self):
        return self.content_type.model
    


class Vendor(models.Model):
    vendor_name = models.CharField(max_length=50)
    contact_person = models.CharField(max_length=50)
    phone = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True, default='', unique=True)
    gst = models.CharField(max_length=50, blank=True)
    address = models.CharField(max_length=50, blank=True)
    
    def __str__(self):
        return self.vendor_name
  
  
class Purchase(models.Model):
    order = models.ForeignKey('PurchaseOrder', on_delete=models.CASCADE, null=True, blank=True, verbose_name='Order')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Purchased by')
    item = models.ForeignKey(Item, on_delete=models.CASCADE,  verbose_name='Item')
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE, verbose_name='Variant')
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    tax_percent = models.PositiveIntegerField()
    discount = models.PositiveIntegerField()   
    created_at = models.DateTimeField(default=datetime.now, verbose_name='Date')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Last updated')
    
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return str(self.item.name).capitalize() 
    
    @property
    def get_total_amount(self):
        return self.quantity * self.unit_price

    def get_absolute_url(self):
        return reverse('stock:purchase_detail', args=[self.pk])    
    
class PurchaseOrder(models.Model):
    
    DR = 'draft'
    AP = 'approved'
    RC = 'received'
    CN = 'cancelled'
    
    STATUS_CHOICES = (
        (DR, 'Draft'),
        (AP, 'Approved'),
        (RC, 'Received'),
        (CN, 'Cancelled'),
    )
    
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    order_date = models.DateTimeField(default=datetime.now)
    status = models.CharField(choices=STATUS_CHOICES, default=DR, max_length=50)
    
    def __str__(self):
        return str(self.vendor.vendor_name)
    
    
    
class PurchaseOrderItems(models.Model):
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE)
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.PositiveIntegerField(default=0)
    tax_percent = models.PositiveIntegerField(default=0)
    discount = models.PositiveIntegerField(default=0)   
    
    
class GoodsReceipt(models.Model):
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE)
    recieved_date = models.DateField(default=datetime.now)
    invoice_number = models.CharField(max_length=50)
    invoice_file = models.ImageField(upload_to='invoice/', null=True, blank=True)
    
    
class GoodsReceiptItems(models.Model):
    goods_receipt = models.ForeignKey(GoodsReceipt, on_delete=models.CASCADE)
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE)
    quantity_received = models.PositiveIntegerField(default=1)
    unit_cost = models.PositiveIntegerField(default=0)
    
    
class StockTransactions(models.Model):
    IN = 'in'
    OT = 'out'
    RN = 'return'
    AD = 'adjustment'
    TRANSACTION_TYPE = [
        (IN, 'In'),
        (OT, 'Out'),
        (RN, 'Return'),
        (AD, 'Adjustment'),
    ]
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE)
    txn_type = models.CharField(max_length=50, choices=TRANSACTION_TYPE)
    quantity = models.PositiveIntegerField(default=1)
    txn_date = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    contenttype = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    reference = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('contenttype', 'reference')
    
    class Meta:
        ordering = ['-txn_date']
        
    def get_object(self):
        return self.contenttype.get_object_for_this_type(pk=self.reference)
    
    def get_serial_number(self):
        if self.variant.is_serialized:
            serial_number = Serialnumber.objects.filter(content_type=self.contenttype, object_id=self.reference).first()
            return serial_number
            

    
    
class Allocations(models.Model):
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    allocated_date = models.DateField(default=datetime.now)
    issued_by = models.ForeignKey(User, on_delete=models.CASCADE)
    contenttype = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    allocated_to = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('contenttype', 'allocated_to')
    
    class Meta:
        verbose_name_plural = 'Allocations'
    
    @property
    def get_recipient(self):
        recipient = self.contenttype.get_object_for_this_type(pk=self.allocated_to)
        # return recipient
        return recipient
    def get_object(self):
        if self.variant.is_serialized:
            serial_number = Serialnumber.objects.filter(content_type=self.contenttype, object_id=self.allocated_to).first()
            return serial_number
        else:
            return self.contenttype.get_object_for_this_type(pk=self.allocated_to)
    
    def __str__(self):
        return str(self.variant)
  
        
class Returns(models.Model):
    GD = 'good'
    DG = 'damaged'
    LT = 'lost'
    
    CONDITION_CHOICES = [
        (GD, 'Good'),
        (DG, 'Damaged'),
        (LT, 'Lost'),
    ]
    
    allocation = models.ForeignKey(Allocations, on_delete=models.CASCADE)
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE)
    returned_by = models.ForeignKey(User, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    condition = models.CharField(max_length=50, choices=CONDITION_CHOICES)
    return_date = models.DateTimeField(auto_now_add=True)
    
    
    class Meta:
        verbose_name_plural = 'Returns'
        
    


