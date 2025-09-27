from django.shortcuts import render, redirect
from authapp.decorators import is_manager
from django.utils.decorators import method_decorator
from stock.models import Variant, Item
from stock.forms import VariantForm, CategoryForm, ItemForm
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.contrib import messages

# Create your views here.
def main(request):
    return redirect('catalogue:add_category')


@method_decorator(is_manager, name='dispatch')
class CreateCategory(CreateView):
    template_name = 'catalogue/category_form.html'
    form_class = CategoryForm
    success_url = reverse_lazy('catalogue:add_item')
    
    def form_valid(self, form):
        messages.success(self.request, "Category added successfully")
        return super().form_valid(form)
    

@method_decorator(is_manager, name='dispatch')
class CreateVariant(CreateView):
    template_name = 'catalogue/variant_form.html'
    model = Variant
    form_class = VariantForm
    success_url = reverse_lazy('catalogue:add_variant')
    
    def form_valid(self, form):
        form_data = self.request.POST
        keys = form_data.getlist('key')
        vals = form_data.getlist('val')

        # build dict safely
        dict_data = dict(zip(keys, vals))

        # attach to instance before save
        form.instance.meta_data = dict_data
        form.instance.is_active = True

        messages.success(self.request, "Variant added successfully")
        return super().form_valid(form)

    
    def get(self, request, *args, **kwargs):
        if request.headers.get('hx-request'):
            return render(request, 'catalogue/variant_form.html#key_value', {'form': self.form_class()})
        
        return super().get(request, *args, **kwargs)
    

    
# Create your views here.
@method_decorator(is_manager, name='dispatch')
class ItemCreateView(CreateView):
    model = Item
    template_name = 'catalogue/item_form.html'
    form_class = ItemForm
    success_url = reverse_lazy('catalogue:add_variant')

    def form_valid(self, form):
        name = form.cleaned_data.get('name')
        category = form.cleaned_data.get('category')
        
        print(name, category)

        if Item.objects.filter(name__iexact=name.lower(), category=category).exists():
            messages.error(self.request, 'This item is already added.')
            return self.form_invalid(form)

        messages.success(self.request, 'Item added successfully')
        return super().form_valid(form)    
    
    def form_invalid(self, form):
        return super().form_invalid(form)
  

