from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from .models import *
from .forms import *
from django.urls import reverse_lazy
from django.forms import formset_factory
from django.contrib import messages
from django.views.generic import TemplateView, DetailView
from django.db import transaction
from .utils import find_allocation
from stock.models import StockTransactions, Stock
from django.contrib.contenttypes.models import ContentType
from stock.utils import update_stock_quantity
from django.db.models import Sum, F
from django.forms import formset_factory, modelformset_factory
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from authapp.decorators import is_manager

@login_required
@is_manager
def student_index(request):
    return redirect('kit:item_form')

def create_kit(request):
    return render(request, 'kits/item_form.html')
    

class CreateItemView(CreateView):
    model = Kits
    form_class = KitForm
    template_name = 'kits/item_form.html'
    success_url = reverse_lazy('kit:create_kititems')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        kits = Kits.objects.all()
        context['kits'] = kits
        return context
    
    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Item added successfully')
        return super().form_valid(form)
    
    
def kititem_view(request):
    if request.method == 'POST':
        form_count = request.POST.get('form_count')
        KitItemFormSet = formset_factory(KitItemsForm, extra=int(form_count), max_num=int(form_count))
        
        post_data = request.POST.copy()
        first_kit_id = post_data.get('form-0-kit')
        
        for i in range(1, int(form_count)):
            post_data[f'form-{i}-kit'] = first_kit_id
        
        formset = KitItemFormSet(post_data)
        
        if formset.is_valid():
            for form in formset:
                form.save()
            
            messages.success(request, 'Kit items added successfully')
            return render(request, 'kits/kit_form.html')
        else:
            print('errrors',formset.errors)
            messages.error(request, 'Error in form')
            return render(request, 'kits/kit_form.html', {'formset': formset})
        
    kit_packs = KitItems.objects.values('kit__type', 'kit__academic_year', 'kit__name').annotate(kit_total=Sum('quantity'), payable_amount=Sum('price'))
    context = {'kit_packs': kit_packs} 
    
    return render(request, 'kits/kit_form.html', context)



def update_kit(request, kit_id):
    context = dict()
    """
    View for updating a kit item.
    """
    kit = Kits.objects.get(pk=kit_id)

    if request.method == 'POST':
        post_data = request.POST.copy()
        kit_form = ItemAndKitForm(post_data, instance=kit)
        kititems_formset = BaseKitFormSet(request.POST, instance=kit)
        
      
        if kititems_formset.is_valid():
            kit_form.save()
            kititems_formset.save()
            messages.success(request, 'Kit updated successfully')
            return redirect('kit:item_form')
        else:
            print('formset',kititems_formset)
            print('form',kit_form.errors)
            messages.error(request, 'Something went wrong. Try again.')
            
        return redirect('kit:update_kit', kit_id=kit_id)
    
    kit_form = ItemAndKitForm(instance=kit)
    kititems_formset = BaseKitFormSet(instance=kit)

    
    for form in kititems_formset:
        form.fields['price'].widget.attrs.update({
            'readonly':True if kit.type == Kits.FR else False,
        })

        form.fields['price'].widget.attrs.update({
            'class': 'form-control'
        })
        
        for field in form.fields.values():
            field.label = ''
    
    
    context['kit_form'] = kit_form
    context['kititems_formset'] = kititems_formset
    
    return render(request, 'kits/update_kit.html', context)



def delete_kititem(request, pk):
    kit_id = request.GET.get('kit')
    print('kit id',kit_id)
   
    kititem = get_object_or_404(KitItems, pk=pk)
    kititem.delete()
    messages.success(request, 'Kit item deleted successfully')
    return redirect('kit:update_kit', kit_id=int(kit_id))

def get_kititem_form(request):
    form_count = request.POST.get('form_count', 1)
    KitItemFormSet = formset_factory(KitItemsForm, extra=int(form_count), max_num=int(form_count))
    formset = KitItemFormSet()
 
    context = {'formset': formset, 'form_count': form_count}
    return render(request, 'kits/partials/kititem_form_part.html', context)


def delete_kit(request, pk):
    kit = get_object_or_404(Kits, pk=pk)
    kit.delete()
    messages.success(request, 'Kit deleted successfully')
    return redirect('kit:item_form')


def allocation_list(request):
    kit_allocations = KitAllocation.objects.all()
    context = {'kit_allocations': kit_allocations}
    
    
    if request.GET.get('search'):
       kit_allocations = find_allocation(request.GET.get('search'))
       context = {'kit_allocations': kit_allocations}
        
    return render(request, 'kits/allocation_list.html', context)

def allocate_sale(request):
    
    if request.method == 'POST':
        post_data = request.POST.copy()
        
        enrollement = post_data.get('enrollement')
        phone = post_data.get('phone', '')
        kit = Kits.objects.get(pk=post_data.get('kit'))

        with transaction.atomic():
            student, created = Student.objects.get_or_create(
                enrollement=enrollement,
                defaults={
                    'name': post_data.get('name'),
                    'program': post_data.get('program'),
                    'phone':post_data.get('phone'),
                    'admission_year': post_data.get('admission_year'),
                }
            )
            
            
            if kit.type == Kits.FR:
                already_allocated = KitAllocation.objects.filter(
                    student=student,
                    kit__type=Kits.FR,
                    kit__academic_year=kit.academic_year
                ).exists()

                if already_allocated:
                    messages.error(request, 'This student has already been allocated a free kit for this academic year.')
                    return redirect('kit:allocate_sale')

                kit_alloc_obj = KitAllocation.objects.create(student=student, kit=kit)
                kit_alloc_obj.kititems.set(post_data.getlist('kititems'))
                
                for item in kit_alloc_obj.kititems.all():
                    Stock.objects.filter(variant=item.variant).update(
                        quantity=F('quantity') - item.quantity,
                        movement_type = Stock.OT,
                        updated_at = timezone.now()
                    )
                    
                messages.success(request, 'Kit allocated successfully.')
                return redirect('kit:allocate_sale')
            elif kit.type == Kits.PD:
                kit_alloc_obj = KitAllocation.objects.create(student=student, kit=kit)
                kit_alloc_obj.kititems.set(post_data.getlist('kititems'))
                messages.success(request, 'Kit allocated successfully.')
                return redirect('kit:allocate_sale')
               



    if request.headers.get('hx-request'):
        initial = {
            'name': request.GET.get('name'),
            'enrollement': request.GET.get('enrollement'),
            'program': request.GET.get('program'),
            'admission_year': request.GET.get('admission_year'),
        }
        
        type = request.GET.get('type', '0')
        stdform = StudentForm(initial=initial)
        allocform = KitAllocationForm(type=type)
        
        context = {'stdform': stdform, 'allocform': allocform, 'type': type}
        return render(request, 'kits/allocate_sale.html', context)
        
    stdform = StudentForm()
    allocform = KitAllocationForm()
    context = {'stdform': stdform, 'allocform': allocform}
    return render(request, 'kits/allocate_sale.html', context)


class KitAllocationDetailView(DetailView):
    model = KitAllocation
    context_object_name = 'kit_alloc'
    template_name = 'kits/allocate_sale_detail.html'
    
    
class UpdateKitAllocation(UpdateView):
    model = KitAllocation
    form_class = KitAllocationForm
    template_name = 'kits/allocate_sale_update.html'
    type = None
    
    
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.type = request.GET.get('type') or self.object.kit.type
        return super().get(request, *args, **kwargs)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['kititems'].queryset = KitItems.objects.filter(kit__type=self.type)
        form.fields['kit'].queryset = Kits.objects.filter(type=self.type)
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['kit_alloc'] = self.object
        context['allocform'] = self.form_class(instance=self.object, type=self.type)
        context['stdform'] = StudentForm(instance=self.object.student)
        context['type'] = self.type
        return context
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.type = request.POST.get('type') or self.object.kit.type
        
        form_data = request.POST.copy()
        
        stdform_data = {
            'name': form_data.get('name'),
            'enrollement': form_data.get('enrollement'),
            'program': form_data.get('program'),
            'admission_year': form_data.get('admission_year'),
        }
        
        allocform_data = {
            'kit': form_data.get('kit'),
            'kititems': form_data.getlist('kititems'),
            'student':self.object.student.id,
            'type':self.type
        }

        
        
        stdform = StudentForm(stdform_data, instance=self.object.student)
        allocform = KitAllocationForm(
            allocform_data,
            instance=self.object,
            type=self.type,
        )

        allocform.fields['kititems'].queryset = KitItems.objects.filter(kit__type=self.type)
        allocform.fields['kit'].queryset = Kits.objects.filter(type=self.type)

        if stdform.is_valid() and allocform.is_valid():
            return self.form_valid(stdform, allocform)
        else:
            return self.form_invalid(stdform, allocform)

    def form_valid(self, stdform, allocform):
        self.kwargs['pk'] = self.object.pk
        """Save both forms manually."""
        student = stdform.save(commit=False)
        student.save()

        allocation = allocform.save(commit=False)
        allocation.student = student
        allocation.save()
        allocform.save_m2m()

        messages.success(self.request, "Record updated successfully.")
        return redirect(self.get_success_url())

    def form_invalid(self, stdform, allocform):
        """Re-render template with errors."""
        messages.error(self.request, "Something went wrong. Try again.")
        context = self.get_context_data(stdform=stdform, allocform=allocform)
        return self.render_to_response(context)
    
    def get_success_url(self):
        return reverse_lazy('kit:update_allocation', kwargs={'pk': self.object.pk})

