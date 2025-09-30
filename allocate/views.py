from django.shortcuts import render, redirect
from stock.models import( Allocations, StockTransactions, Returns, Item, Variant, Location, StockTransactions)
from django.views.generic.edit import CreateView
from .forms import AllocationForm, ReturnForm
from django.urls import reverse_lazy
from .utils import load_variant_by_item
from django.contrib import messages
from authapp.models import Employee
from django.contrib.contenttypes.models import ContentType
from django.db import transaction



# Create your views here.


def main_page(request):
    return redirect('allocate:allocation_list')
class AllocationView(CreateView):
    model = Allocations
    form_class = AllocationForm
    context_object_name = 'allocations'
    template_name = 'allocate/allocation_list.html'
    success_url = reverse_lazy('allocate:allocation_list')
    
    
    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        context['allocations'] = Allocations.objects.all()
        return context
    
    
    def form_valid(self, form ):
        allocation = form.save(commit=False)
        allocation.issued_by = self.request.user
        allocated_to_choice = allocation.allocated_to
        selected_id = self.request.POST.get('name')
        
        if allocated_to_choice == 1:
            allocation.contenttype = ContentType.objects.get_for_model(Employee)
        elif allocated_to_choice == 2:
            allocation.contenttype = ContentType.objects.get_for_model(Location)
        else:
            allocation.contenttype = None

        allocation.allocated_to = int(selected_id)
        
        with transaction.atomic():
            allocation.save()
            transation = StockTransactions.objects.create(
                variant = allocation.variant,
                txn_type = StockTransactions.OT,
                quantity = allocation.quantity,
                created_by = self.request.user,
                contenttype = allocation.contenttype,
                reference = allocation.allocated_to
            )
        
        messages.success(self.request, 'Allocation added successfully')
        return super().form_valid(form )
    
    def form_invalid(self, form):
        response = super().form_invalid(form)
        messages.error(self.request, 'Could not allocate. Try again.')
        return response
    
     
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        allocated_to = self.request.POST.get('allocated_to') or self.request.GET.get('allocated_to')
        if allocated_to:
            kwargs['allocated_to'] = allocated_to
        return kwargs
    
    def get(self, request, *args, **kwargs):
        self.object = None
        if request.headers.get('hx-request'):
            item = request.GET.get('item')
            variant = request.GET.get('variant')
            allocated_to = request.GET.get('allocated_to')
                       
            initial = {
                'variant': variant,
            }
            
            context = self.get_context_data(**kwargs)
            form = self.form_class(initial=initial, allocated_to=allocated_to)
            context['item_id'] = item
            context['alloc_id'] = request.GET.get('allocated_to')
            context['form'] = form
            
            return render(request, self.template_name, context)
        
        return super().get(request, *args, **kwargs)


class ReturnView(CreateView):
    model = Returns
    form_class = ReturnForm
    context_object_name = 'returns'
    template_name = 'allocate/return_list.html'
    success_url = reverse_lazy('allocate:return')
    
    
def load_variant(request):
    response = load_variant_by_item(
        request,
        AllocationForm,
        'allocate/allocation_list.html#optionpart'
    )
    return response