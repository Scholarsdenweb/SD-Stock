from django.contrib import admin
from stock.models import *
from django.urls import path


# imports for djnago import-export tool
from import_export import resources
from import_export.fields import Field  


    

# Register your models here.

class ItemAdmin(admin.ModelAdmin):
    # list_display = ('id','name', 'description',  'created_at', 'updated_at')
    list_display = ('id','name', 'created_at', 'updated_at')
    ordering = ('created_at',)





class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('id','item__name', 'item__id', 'unit_price', 'quantity', 'total_amount', 'user', 'created_at', 'updated_at')
    ordering = ('created_at',)



    


    # def item__size(self, obj):
    #     if obj.item.size == None:
    #         return 'N/A'
    #     else:
    #         return obj.item.size.upper() # or however your relation is structured
    # item__size.short_description = 'Size'


class StockAdmin(admin.ModelAdmin):
    list_display = ['id', 'variant']
    # ordering = ('date',)

    # def stock_item__item__size(self, obj):
    #     if obj.stock_item.size == None:
    #         return 'N/A'
    #     else:
    #         return obj.stock_item.size.upper() # or however your relation is structured
    # stock_item__item__size.short_description = 'Size'  # Custom label in admin


    def stock_item__id(self, obj):
        return obj.stock_item.id  
    stock_item__id.short_description = 'Item ID'


    def stock_item__quantity(self, obj):
        return obj.stock_item.quantity  
    stock_item__quantity.short_description = 'Quantity'

class IssueAdmin(admin.ModelAdmin):
    list_display = ['id','enrollement', 'get_student_name', 'get_items', 'quantity', 'issue_date', 'status', 'user' ]

    def get_items(self, obj):
        return ", ".join([str(item.name.capitalize()) for item in obj.items.all()])
    get_items.short_description = 'Items'

    def get_student_name(self, obj):
        student = Student.objects.get(enrollement='123456')
        print('student', student)
        return student.name
    get_student_name.short_description = 'Student Name'
    

    

class TransactionAdmin(admin.ModelAdmin):
    list_display = ['id','item__name', 'item__id' ,'reference_id', 'quantity', 'transaction_type', 'reference_model', 'manager','notes', 'created_at']


    # def item__size(self, obj):
    #     if obj.item.size == None:
    #         return 'N/A'
    #     else:
    #         return obj.item.size.upper() # or however your relation is structured
    

admin.site.register(Stock, StockAdmin)
admin.site.register(Purchase, PurchaseAdmin)
admin.site.register(Issue, IssueAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(Location)
admin.site.register(PurchaseOrder)
admin.site.register(Serialnumber)


class StockResource(resources.ModelResource):
    updated_at = Field(attribute='updated_at', column_name='Last Updated')
    created_at = Field(attribute='created_at', column_name='Added On')
    variant__product__name = Field(attribute='variant__product__name', column_name='Product Name')
    location__name = Field(attribute='location__name', column_name='Location')
    variant__name = Field(attribute='variant__name', column_name='Product Variant')
    class Meta:
        model = Stock
        fields = ('id','variant__product__name', 'location__name', 'variant__name', 'quantity', 'created_at', 'updated_at')

    
    def dehydrate_updated_at(self, obj):
        return obj.updated_at.strftime("%d-%m-%Y %H:%M:%S")
    
    def dehydrate_created_at(self, obj):
        return obj.created_at.strftime("%d-%m-%Y %H:%M:%S")
    

# class PurchaseResource(resources.ModelResource):
#     created_at = Field()
#     user = Field()
#     item__size = Field
#     class Meta:
#         model = Purchase
#         fields = ('id','item__name', 'item__id', 'item__size', 'quantity', 'total_amount', 'user', 'supplier', 'created_at', 'updated_at')

#     def dehydrate_created_at(self, obj):
#         return obj.created_at.strftime("%d-%m-%Y %H:%M:%S")
    
#     def dehydrate_user(self, obj):
#         return f"{obj.user.name}({obj.user.emp_id})"
    
#     def dehydrate_item__size(self, obj):
#         if obj.item.size == None:
#             return 'N/A'
#         else:
#             return obj.item.size.upper()
    

# class TransactionResouece(resources.ModelResource):
#     created_at = Field(column_name="Transaction Date")
#     manager = Field()
#     item__size = Field(column_name="Item Size")
#     class Meta:
#         model = Transaction
#         fields = ('id','item__name', 'item__id', 'item__size', 'reference_id', 'quantity', 'transaction_type', 'reference_model', 'manager','notes', 'created_at')

#     def dehydrate_created_at(self, obj):
#         return obj.created_at.strftime("%d-%m-%Y %H:%M:%S")
    
#     def dehydrate_manager(self, obj):
#         return f"{obj.manager.name}({obj.manager.emp_id})"
    
#     def dehydrate_item__size(self, obj):
#         if obj.item.size == None:
#             return 'N/A'
#         else:
#             return obj.item.size.upper()
        
class KitResource(resources.ModelResource):
    issue_date = Field()
    status = Field()
    user = Field()
    items = Field()
    class Meta:
        model = Issue
        fields = ('id', 'enrollement','items', 'issue_date', 'quantity', 'status', 'user') 
    
    def dehydrate_issue_date(self, obj):
        return obj.issue_date.strftime("%d-%m-%Y %H:%M:%S")
    
    def dehydrate_status(self, obj):
        if obj.status == True:
            return 'Issued'
        else:
            return 'Not Issued'
        
    def dehydrate_user(self, obj):
        return f"{obj.user.name}({obj.user.emp_id})"
    
    def dehydrate_items(self, obj):
        items = obj.get_items()
        return items
    


# class StudentAdmin(admin.ModelAdmin):
#     form = StudentForm
#     list_display = ['id', 'name', 'enrollement', 'receipt', 'phone']
    
    
# admin.site.register(Student, StudentAdmin)
# admin.site.register(IssueItem)    
admin.site.register(Category)
admin.site.register(Variant)
admin.site.register(Vendor)
