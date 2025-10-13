from .models import Kits, KitItems, KitAllocation
from stock.models import Variant
from django.forms import ModelForm
from django import forms
from authapp.models import Student
from django.forms import inlineformset_factory
from datetime import datetime

current_year = datetime.now().year
previous_five_years = [year for year in range(current_year - 5, current_year)]


class KitForm(ModelForm):
    class Meta:
        model = Kits
        fields = ['name', 'type', 'description', 'academic_year']
        
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder':'i.e. Welcome Kit'}),
            'type': forms.Select(attrs={'class': 'form-select mt-2'}),
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder':'i.e. First year welcome kit'}),
            'academic_year': forms.TextInput(attrs={'class': 'form-control mt-2', 'placeholder':'i.e. 2023-2024'}),
            }
            
        labels = {
            'name': 'Kit Name',
        }
        
        def clean(self):
            cleaned_data = super().clean()
            name = cleaned_data.get('name')
            academic_year = cleaned_data.get('academic_year')

            qs = Kits.objects.filter(name__iexact=name, academic_year=academic_year)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)

            if qs.exists():
                raise forms.ValidationError('Kit already exists.')
            return cleaned_data
        
class KitItemsForm(ModelForm):
    class Meta:
        model = KitItems
        fields = ['kit', 'variant', 'price', 'quantity']
        
        widgets = {
            'quantity': forms.TextInput(attrs={'class': 'form-control', 'min':'1'}),
            'price': forms.TextInput(attrs={'class': 'form-control', 'min':'1'}),
            'kit': forms.Select(attrs={'class': 'form-select'}),
            'variant': forms.Select(attrs={'class': 'form-select'}),
        }
        
        labels = {
            "variant":'Item'
        }
        
        
class StudentForm(ModelForm):
    class Meta:
        model = Student
        fields = ['name', 'enrollement', 'program','phone', 'admission_year']
        
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control my-2'}),
            'enrollement': forms.TextInput(attrs={'class': 'form-control my-2'}),
            'program': forms.TextInput(attrs={'class': 'form-control my-2'}),
            'phone': forms.TextInput(attrs={'class': 'form-control my-2'}),
            'admission_year': forms.Select(attrs={'class': 'form-select my-2'}),
        }
        
        labels = {
            'phone':'Phone(optional)',
        }
        
class KitAllocationForm(ModelForm):
    TYPE_CHOICES = (
        ('free', 'free'),
        ('paid', 'paid'),
    )
    
    type = forms.ChoiceField(choices=TYPE_CHOICES, widget=forms.RadioSelect, label="This kit is:")
    class Meta:
        model = KitAllocation
        fields = ['student', 'kit', 'kititems']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-select my-2'}),
            'kit': forms.Select(attrs={'class': 'form-select my-2'}),
            'kititems': forms.SelectMultiple(attrs={'class': 'form-select-input my-2'})
        }
        
        labels = {
            'kit':'select kit',
            'kititems': 'Select Items',
        }
        
      
    field_order = ['student', 'type', 'kit', 'kititems']
    def __init__(self, *args, **kwargs):
        type = kwargs.pop('type', None)
        super().__init__(*args, **kwargs)

        if type == 'free':
            self.fields['kit'].choices = [
                (kit.pk, kit) for kit in Kits.objects.filter(type='free')
            ]
            
            self.fields['kititems'].queryset = KitItems.objects.filter(kit__type='free')
            
        elif type == 'paid':
            self.fields['kit'].choices = [
                (kit.pk, kit) for kit in Kits.objects.filter(type='paid')
            ]
            self.fields['kititems'].queryset = KitItems.objects.filter(kit__type='paid')
        else:
            self.fields['kit'].choices = [(None, '---------')]
            self.fields['kititems'].queryset = KitItems.objects.none()
            
            
BaseKitFormSet = inlineformset_factory(
    Kits,
    KitItems,
    fields=('kit', 'variant', 'price', 'quantity'),
    extra=0,
    can_delete=False,
    widgets={
        'kit': forms.Select(attrs={'class': 'form-select mt-2'}),
        'variant': forms.Select(attrs={'class': 'form-select'}),
        'quantity': forms.TextInput(attrs={'class': 'form-control', 'min':'1'}),
        'price': forms.TextInput(attrs={'class': 'form-control', 'min':'1'}),
    }
    )
           
class ItemAndKitForm(forms.ModelForm):
    class Meta:
        model = Kits
        fields = ['name', 'type', 'description', 'academic_year']
        
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder':'i.e. Welcome Kit'}),
            'type': forms.Select(attrs={'class': 'form-select mt-2'}),
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder':'i.e. First year welcome kit'}),
            'academic_year': forms.TextInput(attrs={'class': 'form-control mt-2', 'placeholder':'i.e. 2023-2024'}),
            }
            
        labels = {
            'name': 'Kit Name',
        }