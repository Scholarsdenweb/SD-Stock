from stock.models import PurchaseOrder, Purchase
from django.forms import ModelForm
from django import forms



class OrderForm(ModelForm):
    class Meta:
        model = PurchaseOrder
        fields = '__all__'
        
        widgets = {
            'vendor': forms.Select(attrs={'class': 'form-select'}),
            'order_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'min': '2023-01-01'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }
        
        
        
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
        