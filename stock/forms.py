from django import forms
from django.forms import ModelForm
from stock.models import *
from django.forms.widgets import DateInput
from datetime import date
from django.contrib import messages
from django.urls import reverse



class VendorForm(ModelForm):
    class Meta:
        model = Vendor
        fields = ['vendor_name', 'contact_person', 'phone', 'email', 'address', 'gst']
        
        widgets = {
            'vendor_name': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_person': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows':3}),
            'gst': forms.TextInput(attrs={'class': 'form-control'}),
        }

class CategoryForm(ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows':3}),
        }
        
        labels = {
            'name': 'Category Name',
        }
        
    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')

        if name and Category.objects.filter(name__icontains=name).exists():
            raise forms.ValidationError('Category already exists.')

        if name:
            cleaned_data['name'] = name.lower()

        return cleaned_data
        
        
  
        

        
class SerialEditForm(ModelForm):
    class Meta:
        model = Serialnumber
        fields = ['product_variant','serial_number']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product_variant'].widget.attrs.update({
            'readonly': True,
            'style': 'background-color:#e9ecef; cursor:not-allowed;'
        })
 
        
class StockEditForm(ModelForm):
    class Meta:
        model = Stock
        fields = ['variant', 'location', 'quantity']
        


SHIRT_SIZE = ['xs','s', 'm', 'l', 'xl', 'xxl', 'xxxl', '4xl', '5xl']
class StockDate(DateInput):
    input_type = 'date'

class ItemForm(ModelForm):
    class Meta:
        model = Item
        fields = ['name', 'category', 'code']

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            # 'description': forms.Textarea(attrs={'class': 'form-control', 'rows':3}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'code':forms.TextInput(attrs={'class': 'form-control'}), 
        }
        
        labels = {
            'name': 'Item Name',
            'category': 'Category',
            'code': 'Item Code',
        }

    # def clean(self):
    #     cleaned_data = super().clean()
    #     name = cleaned_data.get('name')
    #     category = cleaned_data.get('category')
        
    #     if name and Item.objects.filter(name__iexact=name, category=category).exists():
    #         raise forms.ValidationError('Item already exists.')

    #     if name and category:
    #         cleaned_data['name'] = name.lower()
    #         cleaned_data['category'] = category

    #     return cleaned_data
            


class VariantForm(ModelForm):    
    category = forms.ModelChoiceField(queryset=Category.objects.all(), widget=forms.Select(attrs={'class': 'form-select'}))
    meta_data = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': """Enter additional data. e.g. {"color": "red", "size": "M"}"""
            }
        ),
  
    )
    class Meta:
        model = Variant
        fields = ['product', 'name', 'meta_data', 'is_serialized', 'is_active']

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'is_serialized': forms.CheckboxInput(attrs={'id': 'is_serialized'}),
            'is_active': forms.CheckboxInput(),
        }
        
              
        labels = {
            'meta_data': 'Additional Data',
            'name': 'Variant Name',
        }
        
        
        
    field_order = ['category', 'product', 'name', 'sku', 'is_serialized', 'is_active']
    
    
    def __init__(self, *args, **kwargs):
        super(VariantForm, self).__init__(*args, **kwargs)
        self.fields['product'].queryset = Item.objects.all()
        
    def clean(self, *args, **kwargs):
        cleaned_data = super(VariantForm, self).clean(*args, **kwargs)
        name = cleaned_data.get('name')
        category = cleaned_data.get('category')
        if Variant.objects.filter(name = name, product__category = category).exists():
            raise forms.ValidationError('Variant already exists.')
        return self.cleaned_data
        
class SerialNumberForm(ModelForm):  
    class Meta:
        model = Serialnumber
        fields = ['item', 'product_variant', 'serial_number', 'status']


# class PurchaseForm(ModelForm):
#     # items = forms.ModelMultipleChoiceField(queryset=Item.objects.all(), widget=forms.CheckboxSelectMultiple)

#     class Meta:
#         model = Purchase
#         fields = ['item', 'quantity', 'unit_price', 'total_amount', 'tax_percent', 'discount', 'created_at', 'supplier']

#         widgets = {
#             'item': forms.Select(attrs={'class': 'form-select mt-2'}),
#             'quantity': forms.NumberInput(attrs={
#                 'class': 'form-control mt-2',
#             }),
#             'total_amount': forms.TextInput(attrs={'class': 'form-control mt-2'}),
#             'supplier': forms.TextInput(attrs={'class': 'form-control mt-2'}),
#             'unit_price': forms.TextInput(attrs={'class': 'form-control mt-2'}),
#             'created_at':forms.TextInput(attrs={'class': 'form-control mt-2', 'type': 'date'})
#         }
        
#         labels = {
#             'order': 'Order Taken by:',
#         }
        
#     def __init__(self, *args, **kwargs):
#         super(PurchaseForm, self).__init__(*args, **kwargs)
#         today_str = date.today().strftime('%Y-%m-%d')
#         self.fields['created_at'].widget.attrs.update({'max': today_str})
#         self.initial['created_at'] = today_str
        
        
class StockForm(ModelForm):
    item = forms.ModelChoiceField(queryset=Item.objects.all())
    
    class Meta:
        model = Stock
        fields = ['location', 'variant', 'quantity']
        
        widgets = {
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'location': forms.Select(attrs={'class': 'form-select'}),
            'variant': forms.Select(attrs={'class': 'form-select'}),
        }
        
    field_order = ['item', 'location', 'variant', 'quantity']
        
    def __init__(self, *args, **kwargs):
        super(StockForm, self).__init__(*args, **kwargs)
        self.label_suffix = ''
        self.fields['variant'].queryset = Variant.objects.all()
        


# class StockForm(ModelForm):
#     # item = forms.MultipleChoiceField(choices=ITEM_CHOICES, widget=forms.CheckboxSelectMultiple())

#     class Meta:
#         model = Stock
#         fields = ['stock_item', 'date']

#         widgets = {
#             'stock_item':forms.Select(attrs={'class': 'form-select mt-2'}),
#             'date': StockDate(attrs={'class': 'form-control mt-2', 'max':date.today()})
#         }

    # def clean(self, *args, **kwargs):
    #     cleaned_data = super().clean()
    #     stock_item = cleaned_data.get('stock_item')
    #     quantity = cleaned_data.get('quantity')

    #     if stock_item and quantity:
    #         if quantity > stock_item.item.quantity:
    #            raise ValidationError("Stock quantity cannot exceed purchase quantity.")
    #     return cleaned_data


# ITEM_CHOICES =  tuple((item.name, item.name.capitalize()) for item in Item.objects.all())



class StockCheckboxSelectMultiple(forms.CheckboxSelectMultiple):
    def __init__(self, *args, disabled_values=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.disabled_values = disabled_values or []

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)
        if str(value) in [str(v) for v in self.disabled_values]:
            option["attrs"]["disabled"] = True
            option["attrs"]["class"] = "out-of-stock"
        else:
            option["attrs"]["class"] = "in-stock"
        return option
    
    

class IssueItemForm(ModelForm):
    class Meta:
        model = IssueItem
        fields = ["quantity"]
        
        widgets = {
            'quantity': forms.TextInput(attrs={'size': '1', 'class': 'text-center'}),
        }
        
        
        
        
class IssueForm(ModelForm):
    items = forms.ModelMultipleChoiceField(queryset=Item.objects.all(), widget=StockCheckboxSelectMultiple)

    class Meta:
        model = Issue
        fields = [ 'enrollement', 'student', 'items']

        widgets = {
            'enrollement': forms.HiddenInput(attrs={'class': 'form-control mt-2'}),
            'student': forms.HiddenInput(attrs={'class': 'form-select mt-2'}),
            'items': forms.SelectMultiple(attrs={'class': 'form-check-input mt-2 fs-1'})
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        new_choices = []
        disabled_values = []

        for item in self.fields['items'].queryset:
            stock = Stock.objects.filter(stock_item=item).first()
            stock_info = stock.in_stock() if stock else dict(status=False, quantity=0)

            if stock_info['status']:
                label = f"{item} (In Stock — {stock_info['quantity']} left)"
            else:
                label = f"{item} (Out of Stock)"
                disabled_values.append(item.pk)

            new_choices.append((item.pk, label))

        self.fields['items'].choices = new_choices
        self.fields['items'].widget = StockCheckboxSelectMultiple(disabled_values=disabled_values)




class DownloadForm(forms.Form):
    FORMAT_CHOICE = [
        ('csv', 'CSV'),
        ('xlsx', 'XLSX'),
        ('json', 'JSON'),
]

    format = forms.ChoiceField(choices=FORMAT_CHOICE, widget=forms.Select(attrs={'class': 'form-select'}))




class KitReturnForm(forms.Form):
    enrollement = forms.CharField(widget=forms.HiddenInput())
    name = forms.CharField(widget=forms.HiddenInput())
    dob = forms.CharField(widget=forms.HiddenInput())
    
