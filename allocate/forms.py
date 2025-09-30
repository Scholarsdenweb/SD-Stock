from django.forms import ModelForm
from django import forms
from stock.models import Allocations, Returns, Item, Location
from authapp.models import Employee

class AllocationForm(ModelForm):
    CHOICES_LIST  = [
        (None, '---Select---'),
        (1, 'Employee'),
        (2, 'Location'),
    ]
    item = forms.ModelChoiceField(queryset=Item.objects.all(), widget=forms.Select(attrs={'class': 'form-select my-2'}))
    allocated_to = forms.ChoiceField(choices=CHOICES_LIST, widget=forms.Select(attrs={'class': 'form-select my-2'}))
    name = forms.ChoiceField(choices=[], widget=forms.Select(attrs={'class': 'form-select name-select my-2'}))

    class Meta:
        model = Allocations
        fields = ['item', 'variant',  'allocated_to', 'name', 'quantity', 'allocated_date', ]
        
        widgets = {
            'quantity': forms.NumberInput(attrs={'class': 'form-control my-2'}),
            'allocated_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control my-2', 'min': '2023-01-01'}),
            'variant': forms.Select(attrs={'class': 'form-select my-2'}),
        }
        
    def __init__(self, *args, **kwargs):
        allocated_to = kwargs.pop('allocated_to', None)
        super().__init__(*args, **kwargs)

        if allocated_to == '1':
            self.fields['name'].choices = [
                (p.pk, p.user.full_name + ' - ' + str(p.pk)) for p in Employee.objects.all()
            ]
        elif allocated_to == '2':
            self.fields['name'].choices = [
                (loc.pk, loc.name) for loc in Location.objects.all()
            ]
        else:
            self.fields['name'].choices = []
        

class ReturnForm(ModelForm):
    class Meta:
        model = Returns
        fields = ['quantity']
        
