from stock.models import PurchaseOrder, Purchase
from django.forms import ModelForm
from django import forms



class OrderForm(ModelForm):
    class Meta:
        model = PurchaseOrder
        fields = '__all__'
        
        widgets = {
            'vendor': forms.Select(attrs={'class': 'form-select'}),
            'order_date': forms.DateTimeInput(attrs={'type': 'date', 'class': 'form-control', 'min': '2023-01-01'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }
        
        
        
class PurchaseForm(ModelForm):
    # items = forms.ModelMultipleChoiceField(queryset=Item.objects.all(), widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = Purchase
        fields = ['order', 'item', 'variant', 'quantity', 'unit_price', 'tax_percent', 'discount', 'total_amount','created_at']

        widgets = {
            'order':forms.Select(attrs={'class': 'form-select mt-2'}),
            'item': forms.Select(attrs={'class': 'form-select mt-2'}),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control mt-2',
            }),
            'variant': forms.Select(attrs={'class': 'form-select mt-2'}),
            'total_amount': forms.TextInput(attrs={'class': 'form-control mt-2'}),
            'supplier': forms.TextInput(attrs={'class': 'form-control mt-2'}),
            'unit_price': forms.TextInput(attrs={'class': 'form-control mt-2'}),
            'tax_percent': forms.TextInput(attrs={'class': 'form-control mt-2'}),
            'discount': forms.TextInput(attrs={'class': 'form-control mt-2'}),
            'created_at': forms.DateTimeInput(attrs={'type': 'date', 'class': 'form-control', 'min': '2023-01-01'}),
        }
        
        labels = {
            'order': 'Supplier:',
        }
        