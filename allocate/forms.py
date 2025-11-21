from django.forms import ModelForm
from django import forms
from stock.models import Allocations, Returns, Item, Location, ReturnItem
from authapp.models import Employee

class AllocationForm(ModelForm):
    CHOICES_LIST  = [
        (None, '---Select---'),
        (1, 'Employee'),
        (2, 'Location'),
    ]
    item = forms.ModelChoiceField(queryset=Item.objects.all(), widget=forms.Select(attrs={'class': 'form-select my-2'}))
    allocated_to = forms.ChoiceField(choices=CHOICES_LIST, widget=forms.Select(attrs={'class': 'form-select my-2'}))
    name = forms.ChoiceField(choices=[], widget=forms.Select(attrs={'class': 'form-select my-2'}))
    is_serialized = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'my-3'}), label='Have Serial Number:')

    class Meta:
        model = Allocations
        fields = ['item', 'variants',  'allocated_to', 'name', 'allocated_date', 'is_serialized' ]
        
        widgets = {
            'quantity': forms.NumberInput(attrs={'class': 'form-control my-2', 'min':'1'}),
            'allocated_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control my-2', 'min': '2023-01-01'}),
            'variant': forms.Select(attrs={'class': 'form-select my-2'}),
        }
        
   
        
    def __init__(self, *args, **kwargs):
        allocated_to = kwargs.pop('allocated_to', None)
        super().__init__(*args, **kwargs)

        if allocated_to == '1':
            self.fields['name'].choices = [
                (p.pk, p.user.full_name) for p in Employee.objects.all()
            ]
        elif allocated_to == '2':
            self.fields['name'].choices = [
                (loc.pk, loc.name) for loc in Location.objects.all()
            ]
        else:
            self.fields['name'].choices = []
        

class ReturnItemForm(ModelForm):
    class Meta:
        model = ReturnItem
        fields = ['variant', 'quantity', 'condition']
        widgets = {
            'variant': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'condition': forms.Select(attrs={'class': 'form-select'}),
        }
        
