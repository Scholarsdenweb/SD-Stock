from django import forms
from django.forms import ModelForm
from stock.models import *
from django.forms.widgets import DateInput
from datetime import date
from django.contrib import messages

class StockDate(DateInput):
    input_type = 'date'

class ItemForm(ModelForm):
    class Meta:
        model = Item
        fields = ['name', 'unit_price', 'size', 'description']

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows':3}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control'}),
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
                if size not in ['s', 'm', 'l', 'xl', 'xxl']:
                    raise forms.ValidationError('Invalid size for "shirt". Allowed values are "s", "m", "l", "xl", "xxl".')
            
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
        fields = ['item', 'quantity', 'payment', 'supplier']

        widgets = {
            'item': forms.Select(attrs={'class': 'form-select mt-2'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control mt-2'}),
            'payment': forms.NumberInput(attrs={'class': 'form-control mt-2'}),
            'supplier': forms.TextInput(attrs={'class': 'form-control mt-2'})
        }



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

class IssueForm(ModelForm):
    items = forms.ModelMultipleChoiceField(queryset=Item.objects.all(), widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = Issue
        fields = [ 'enrollement', 'items']

        widgets = {
            'enrollement': forms.TextInput(attrs={'class': 'form-control mt-2'}),
            'items': forms.SelectMultiple(attrs={'class': 'form-check-input mt-2'})
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(IssueForm, self).__init__(*args, **kwargs)




FORMAT_CHOICE = [
    ('csv', 'CSV'),
    ('xlsx', 'XLSX'),
    ('json', 'JSON'),
]

class DownloadForm(forms.Form):
    format = forms.ChoiceField(choices=FORMAT_CHOICE, widget=forms.Select(attrs={'class': 'form-select'}))


