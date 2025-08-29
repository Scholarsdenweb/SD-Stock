from django import forms
from django.forms import ModelForm
from stock.models import *
from django.forms.widgets import DateInput
from datetime import date
from django.contrib import messages

SHIRT_SIZE = ['xs','s', 'm', 'l', 'xl', 'xxl', 'xxxl', '4xl', '5xl']
class StockDate(DateInput):
    input_type = 'date'

class ItemForm(ModelForm):
    class Meta:
        model = Item
        fields = ['name', 'size', 'description']

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows':3}),
            'size': forms.Select(attrs={'class': 'form-select'})   
        }

        def clean(self):
            name = self.name.lower()
            size = self.size.lower() if self.size else None
            uniprice = self.unit_price

            if name == 'bag' or name == 'pen' and self.size is not None:
                if size:
                    raise forms.ValidationError('Size should not be specified for item "pen" or "bag".')
            
            elif name == 'shirt' or name=='t-shirt' and self.size is not None:
                if size not in SHIRT_SIZE:
                    allowed_sizes = ', '.join(SHIRT_SIZE)
                    raise forms.ValidationError('Invalid size for "shirt". Allowed values are {}'.format(allowed_sizes))
            
            elif name == 'diary' and self.size is not None:
                if size not in ['small', 'big']:
                    raise forms.ValidationError('Invalid size for "diary". Allowed values are "Small", "Big"')
                
            elif name not in ['bag', 'pen']:
                valid_choices = [choice[0].lower() for choice in SIZE_CHOICES]
                if not size or size not in valid_choices:
                    raise forms.ValidationError(f'Invalid size for item "{self.name}". Allowed values are: {[choice[0] for choice in SIZE_CHOICES]}.')
                
            elif name and size and uniprice:
                if Item.objects.filter(name=name, size=size, unit_price=uniprice).exists():
                    print("Found")
                    raise forms.ValidationError("An item with the same name, size, and unit price already exists.")
                
            try:
                item = Item.objects.filter(name=name, size=size, unit_price=uniprice).exists
                if item:
                    raise forms.ValidationError('Item already exists')
            except Item.DoesNotExist:
                pass





class PurchaseForm(ModelForm):
    # items = forms.ModelMultipleChoiceField(queryset=Item.objects.all(), widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = Purchase
        fields = ['item', 'quantity', 'unit_price', 'total_amount','created_at', 'supplier', 'supplier_location']

        widgets = {
            'item': forms.Select(attrs={'class': 'form-select mt-2'}),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control mt-2',
            }),
            'total_amount': forms.TextInput(attrs={'class': 'form-control mt-2'}),
            'supplier': forms.TextInput(attrs={'class': 'form-control mt-2'}),
            'supplier_location': forms.TextInput(attrs={'class': 'form-control mt-2'}),
            'unit_price': forms.TextInput(attrs={'class': 'form-control mt-2'}),
            'created_at':forms.TextInput(attrs={'class': 'form-control mt-2', 'type': 'date'})
        }
        
    def __init__(self, *args, **kwargs):
        super(PurchaseForm, self).__init__(*args, **kwargs)
        today_str = date.today().strftime('%Y-%m-%d')
        self.fields['created_at'].widget.attrs.update({'max': today_str})
        self.initial['created_at'] = today_str
        
        



class StockForm(ModelForm):
    # item = forms.MultipleChoiceField(choices=ITEM_CHOICES, widget=forms.CheckboxSelectMultiple())

    class Meta:
        model = Stock
        fields = ['stock_item', 'date']

        widgets = {
            'stock_item':forms.Select(attrs={'class': 'form-select mt-2'}),
            'date': StockDate(attrs={'class': 'form-control mt-2', 'max':date.today()})
        }

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
    
