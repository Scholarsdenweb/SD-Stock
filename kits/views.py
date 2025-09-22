from django.shortcuts import render
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from .models import *
from .forms import *
from django.urls import reverse_lazy
from django.forms import formset_factory
from django.contrib import messages


# Create your views here.

class KitsCreateView(CreateView):
    model = Kits
    form_class = KitForm
    success_url = reverse_lazy('kit:create_kititems')
    
def kititem_view(request):
    if request.method == 'POST':
        form_count = request.POST.get('form_count')
        KitItemFormSet = formset_factory(KitItemsForm, extra=int(form_count), max_num=int(form_count))
        
        formset = KitItemFormSet(request.POST)
        
        print(formset)
        if formset.is_valid():
            print(formset.cleaned_data)
            for form in formset:
                form.save()
            
            messages.success(request, 'Kit items added successfully')
            return render(request, 'kits/kititems_form.html')
        else:
            print('errrors',formset.errors)
            messages.error(request, 'Error in form')
            return render(request, 'kits/kititems_form.html', {'formset': formset})
        
    
    return render(request, 'kits/kititems_form.html')



def get_kititem_form(request):
    form_count = request.POST.get('form_count', 1)
    KitItemFormSet = formset_factory(KitItemsForm, extra=int(form_count), max_num=int(form_count))
    formset = KitItemFormSet()
    context = {'formset': formset, 'form_count': form_count}
    return render(request, 'kits/partials/kititem_form_part.html', context)

