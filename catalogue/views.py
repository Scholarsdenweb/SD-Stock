from django.shortcuts import render, redirect, get_object_or_404
from authapp.decorators import is_manager
from django.utils.decorators import method_decorator
from stock.models import Variant, Item, Category
from stock.forms import VariantForm, CategoryForm, ItemForm
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse_lazy
from django.contrib import messages
from audit.utils import log_action, json_safe

# Create your views here.
def main(request):
    return redirect('catalogue:add_category')


@method_decorator(is_manager, name='dispatch')
class CreateCategory(CreateView):
    template_name = 'catalogue/category_form.html'
    form_class = CategoryForm
    success_url = reverse_lazy('catalogue:add_category')
    
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        categories = Category.objects.all()
        context['categories'] = categories
        return context
    
    def form_valid(self, form):
        messages.success(self.request, "Category added successfully")
        log_action(user=self.request.user, request=self.request, action="create", instance=form.instance)
        return super().form_valid(form)
    

@method_decorator(is_manager, name='dispatch')
class CreateVariant(CreateView):
    template_name = 'catalogue/variant_form.html'
    model = Variant
    form_class = VariantForm
    success_url = reverse_lazy('catalogue:add_variant')
    
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        variants = Variant.objects.all()
        context['variants'] = variants
        return context
    
    def form_valid(self, form):
       
        item_id = self.request.POST.get('product')
        item = Item.objects.get(id=item_id)
        variant_name = form.cleaned_data['name']
        
        if Variant.objects.filter(name__iexact=variant_name, product=item).exists():
            messages.error(self.request, "This variant is already added.")
            return self.form_invalid(form)
        
        keys = self.request.POST.getlist('key')
        vals = self.request.POST.getlist('val')
        form.instance.meta_data = dict(zip(keys, vals))
        
        form.instance.product = item
        response = super().form_valid(form)
        item.variant.add(self.object)
        
        messages.success(self.request, "Variant added successfully")
        log_action(user=self.request.user, request=self.request, action="create", instance=form.instance)

        
        return response

        
   
    def form_invalid(self, form):
        print('invalid' , form.errors)
        return super().form_invalid(form)

   

    
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
    success_url = reverse_lazy('catalogue:add_item')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        items = Item.objects.all()
        context['items'] = items
        return context

    def form_valid(self, form):
        name = form.cleaned_data.get('name')
        category = form.cleaned_data.get('category')
        

        if Item.objects.filter(name__iexact=name.lower(), category=category).exists():
            messages.error(self.request, 'This item is already added.')
            return self.form_invalid(form)

        messages.success(self.request, 'Item added successfully')
        log_action(user=self.request.user, request=self.request, action="create", instance=form.instance)
        return super().form_valid(form)    
    
    def form_invalid(self, form):
        return super().form_invalid(form)
  
class UpdateVariant(UpdateView):
    model = Variant
    template_name = 'catalogue/variant_form.html'
    form_class = VariantForm
    success_url = reverse_lazy('catalogue:add_variant')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        instance_id = context['object'].pk
        context['instance_id'] = instance_id
        variant = context['variant']
        context['item_id'] = variant.product.pk
        context['cat_id'] = variant.product.category.pk
        context['variants'] = Variant.objects.all()
        return context
    
    def form_valid(self, form):
        obj = form.save()
        messages.success(self.request, 'Variant updated successfully')
        log_action(user=self.request.user, request=self.request, action="update", instance=obj, changes={"form_data":json_safe( form.cleaned_data)})
        return super().form_valid(form)
    
    
    
class UpdateItem(UpdateView):
    model = Item
    template_name = 'catalogue/item_form.html'
    form_class = ItemForm
    success_url = reverse_lazy('catalogue:add_item')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['items'] = Item.objects.all()
        context['instance_id'] = context['object'].pk
        return context
    
    def form_valid(self, form):
        obj = form.save()
        messages.success(self.request, 'Item updated successfully')
        log_action(user=self.request.user, request=self.request, action="update", instance=obj, changes={"form_data": json_safe(form.cleaned_data)})
        return super().form_valid(form)
    
    
class UpdateCategory(UpdateView):
    model = Category
    template_name = 'catalogue/category_form.html'
    form_class = CategoryForm
    success_url = reverse_lazy('catalogue:add_category')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['instance_id'] = context['object'].pk
        return context
    
    
    def form_valid(self, form):
        obj = form.save()
        messages.success(self.request, 'Category updated successfully')
        log_action(user=self.request.user, request=self.request, action="update", instance=obj, changes={"form_data": form.json_safe( form.cleaned_data)})
        return super().form_valid(form)
    
def delete_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    messages.success(request, 'Category deleted successfully')
    log_action(user=request.user, request=request, action="delete", instance=category)
    return redirect('catalogue:add_category')
