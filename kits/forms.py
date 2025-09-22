from .models import Kits, KitItems
from stock.models import Variant
from django.forms import ModelForm


class KitForm(ModelForm):
    class Meta:
        model = Kits
        fields = ['name', 'description', 'academic_year']
        
class KitItemsForm(ModelForm):
    class Meta:
        model = KitItems
        fields = ['kit', 'variant', 'quantity']