from django.shortcuts import get_object_or_404, render
from stock.models import Variant, Item


def load_variant_by_item(request, f, template):
    response = None
    
    if request.headers.get('hx-request'):
        item_id = request.GET.get('item')
        item = get_object_or_404(Item, id=int(item_id))
        variants = Variant.objects.filter(product=item)
        form = f()
        form.fields['variant'].queryset = variants
        response =  render(request, template, {'form': form})
        response['HX-Target'] = '#productoptions'
        response = response
    return response


def load_recipient(request, f, template):
    pass
    
