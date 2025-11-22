from django.shortcuts import render, redirect
from stock.models import(AllocationItem, Category, Stock, Allocations, StockTransactions, Returns, Item, Variant, Location, StockTransactions, Serialnumber, ReturnItem)
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic import ListView
from .forms import AllocationForm, ReturnItemForm
from django.urls import reverse_lazy
from .utils import load_variant_by_item, find_allocation_or_returns
from stock.utils import update_stock_quantity
from django.contrib import messages
from authapp.models import Employee, Student
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from authapp.decorators import is_manager
from django.db.models import F
from datetime import datetime
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator
from audit.utils import log_action
from django.forms.models import modelformset_factory
from django.contrib.auth.decorators import login_required


# Create your views here.


def main_page(request):
    return redirect('allocate:allocation_list')
class AllocationView(CreateView):
    model = Allocations
    form_class = AllocationForm
    context_object_name = 'allocations'
    template_name = 'allocate/allocation_list.html'
    success_url = reverse_lazy('allocate:allocation_list')
    paginate_by = 2
    
    
    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        context['allocations'] = Allocations.objects.all()
        paginator = Paginator(context['allocations'], self.paginate_by)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['allocations'] = page_obj
        return context
    
    
    def form_valid(self, form ):
        allocation = form.save(commit=False)
        allocation.issued_by = self.request.user
        allocated_to_choice = allocation.allocated_to #type of recipient, i.e Student or Employee
        selected_id = self.request.POST.get('name') #recipient
        
        if allocated_to_choice == 1:
            allocation.contenttype = ContentType.objects.get_for_model(Employee)
        elif allocated_to_choice == 2:
            allocation.contenttype = ContentType.objects.get_for_model(Location)
        else:
            allocation.contenttype = None

        allocation.allocated_to = int(selected_id)
        
        
        msg_text = ''
        with transaction.atomic():
            try:
                stock = Stock.objects.get(variant=allocation.variant)
            except Stock.DoesNotExist:
                msg_text = 'Stock not found'
                messages.error(self.request, msg_text)
                return self.form_invalid(form)
            
            if stock.quantity > 0 and allocation.quantity <= stock.quantity:
                if allocation.variant.is_serialized:
                    serial_number = self.request.POST.get('serial_number')
                    serial_number_obj = Serialnumber.objects.filter(serial_number__iexact=serial_number).first()
                    
                    if serial_number_obj.status and serial_number_obj.status != Serialnumber.NS:
                        msg_text = f'{serial_number} is already allocated'
                        messages.error(self.request, msg_text)
                        return self.form_invalid(form)
                        
                    if serial_number_obj.status == Serialnumber.NS and allocation.quantity > 1:
                        msg_text = 'Only one serial number is allowed'
                        messages.error(self.request, msg_text)
                        return self.form_invalid(form)
                    
                    serial_number_obj.status = Serialnumber.AL
                    serial_number_obj.content_type = allocation.contenttype
                    serial_number_obj.object_id = allocation.allocated_to
                    serial_number_obj.save()
                    target = serial_number_obj.content_type.get_object_for_this_type(id=serial_number_obj.object_id)
                    msg_text = f'{serial_number} is allocated to {target} successfully'
                    
                allocation.save()
                transation = StockTransactions.objects.create(
                    variant = allocation.variant,
                    txn_type = StockTransactions.OT,
                    quantity = allocation.quantity,
                    created_by = self.request.user,
                    contenttype = allocation.contenttype,
                    reference = allocation.allocated_to
                )
                if not allocation.variant.is_serialized:
                    stock = update_stock_quantity(self.request, item_id = allocation.variant.id, quantity = -allocation.quantity)
                    stock.movement_type = Stock.OT
                    stock.save()
                    
                if msg_text:
                    messages.success(self.request, msg_text)
                messages.success(self.request, f'{allocation.variant} allocated successfully')    
                return super().form_valid(form )
            messages.error(self.request, 'Out of stock. Only {} available'.format(stock.quantity))
            return self.form_invalid(form)
        
        return super().form_valid(form )
    
    def form_invalid(self, form):
        response = super().form_invalid(form)
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
            is_serialized = request.GET.get('is_serialized')
                       
            initial = {
                'variant': variant,
            }
            
            context = self.get_context_data(**kwargs)
            form = self.form_class(initial=initial, allocated_to=allocated_to)
            
            if is_serialized == 'on':
                serial_number = request.GET.get('serial_number')
                context['serial_number'] = serial_number
                form.fields['is_serialized'].initial = True
                
            context['item_id'] = item
            context['alloc_id'] = request.GET.get('allocated_to')
            context['form'] = form
            
            return render(request, self.template_name, context)

        if request.GET.get('search'):
            search_text = request.GET.get('search').strip().lower()
            context = self.get_context_data(**kwargs)
            form = self.form_class()
            allocations = find_allocation_or_returns(search_text, search_model = self.model)
            context['form'] = form
            context['allocations'] = allocations
            paginator = Paginator(context['allocations'], self.paginate_by)
            page_number = self.request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            context['allocations'] = page_obj


            return render(request, self.template_name, context)
        
        return super().get(request, *args, **kwargs)



class UpdateAllocationView(UpdateView):
    model = Allocations
    form_class = AllocationForm
    context_object_name = 'allocations'
    template_name = 'allocate/allocation_update.html'
    
    
    def form_valid(self, form):
        instance = form.save(commit=False)
        serial_number = self.request.POST.get('serial_number')
        is_serialized = self.request.POST.get('is_serialized')
        if is_serialized == 'on' and serial_number:
            if instance.quantity > 1 or instance.quantity < 1:
                messages.error(self.request, 'Only one serial number is allowed.')
                return self.get(self.request, *self.args, **self.kwargs)
            
        
        if self.request.POST.get('allocated_to') == '1':
            instance.contenttype = ContentType.objects.get_for_model(Employee)
            print('contenttype after', instance.contenttype)

        elif self.request.POST.get('allocated_to') == '2':
            instance.contenttype = ContentType.objects.get_for_model(Location)
            print('contenttype after', instance.contenttype)

        print('data',form.cleaned_data)
        self.success_url = reverse_lazy('allocate:update_allocation', kwargs={'pk': self.kwargs['pk']})
        messages.success(self.request, 'Allocation updated successfully')
        form.save()
        return super().form_valid(form)
    
    
    def get(self, request, *args, **kwargs):
        self.object = None
        instance = self.get_object()
        context = self.get_context_data(**kwargs)
        alloc_id = request.GET.get('allocated_to')
        
        
        
        try:
            serial_number_obj = Serialnumber.objects.get(product_variant=instance.variant, status=Serialnumber.AL)
        except Serialnumber.DoesNotExist:
            serial_number_obj = None
            messages.error(request, 'Serial number not found for this item')
        
        if instance.contenttype.pk == 27:
            context['alloc_id'] = alloc_id if alloc_id else 1
        elif instance.contenttype.pk == 7:
            context['alloc_id'] = alloc_id if alloc_id else 2
        else:
            context['alloc_id'] = alloc_id if alloc_id else 0
        
        form = self.form_class(instance=instance,  allocated_to=str(context['alloc_id']))
        
        if request.GET.get('allocated_to') == '1':
            form.fields['name'].choices = [(p.pk, p.user.full_name) for p in Employee.objects.all()]
            print('one')
        elif request.GET.get('allocated_to') == '2':
            form.fields['name'].choices = [(l.pk, l.name) for l in Location.objects.all()]
            print('two')
       
        
        if serial_number_obj is not None:
            form.fields['is_serialized'].initial = True
            context['serial_number'] = serial_number_obj.serial_number
        else:
            form.fields['is_serialized'].widget.attrs.update({'hidden':'hidden'})
            form.fields['is_serialized'].label = ''
        context['item_id'] = instance.variant.product.pk
        context['recipient_id'] = instance.allocated_to
        
        context['form'] = form
        
       
        return render(request, self.template_name, context)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        allocated_to = self.request.POST.get('allocated_to') or self.request.GET.get('allocated_to')
        if allocated_to:
            kwargs['allocated_to'] = allocated_to
        return kwargs

    

@method_decorator(login_required, name='dispatch')
@method_decorator(is_manager, name='dispatch')
class ReturnView(ListView):
    model = Returns
    context_object_name = 'returns'
    template_name = 'allocate/return_list.html'

    def get_queryset(self):
        qs = Returns.objects.all()

        search = self.request.GET.get('search')
        if search:
            search_text = search.strip().lower()
            qs = find_allocation_or_returns(search_text, search_model=self.model)

        return qs


    
def load_variant(request):
    response = load_variant_by_item(
        request,
        AllocationForm,
        'allocate/allocation_list.html#optionpart'
    )
    return response


@is_manager
def return_item(request):
    if request.method == 'POST':
        serial_number = request.POST.get('serial_number')
        quantity = request.POST.get('quantity')
        variant = request.POST.get('variant')
        allocation_id = request.POST.get('allocation_id')
        condition = request.POST.get('condition')
        
        if serial_number:
            serial_number_obj = Serialnumber.objects.filter(serial_number__iexact=serial_number, product_variant__id=int(variant)).first()
            allocation = Allocations.objects.get(pk=int(allocation_id))
            if serial_number_obj:
                with transaction.atomic():
                    serial_number_obj.status = Serialnumber.NS
                    serial_number.content_type = None
                    serial_number.object_id = None
                    serial_number_obj.save()
                    # allocation.delete()
                    StockTransactions.objects.create(
                        variant= serial_number_obj.product_variant,
                        quantity = int(quantity),
                        txn_type = StockTransactions.RN,
                        txn_date = datetime.now(),
                        created_by = request.user,
                        contenttype = allocation.contenttype,
                        reference = allocation.content_object.id
                    )
                    
                    Returns.objects.create(
                        allocation = allocation,
                        variant = serial_number_obj.product_variant,
                        returned_by = request.user,
                        quantity = int(quantity),
                        condition = Returns.CONDITION_CHOICES[condition][0]
                    )
                    messages.success(request, 'Returned successfully')
        else:
            with transaction.atomic():
                allocation = Allocations.objects.filter(pk=int(allocation_id)).update(quantity=F('quantity') - int(quantity))
                stock = update_stock_quantity(request, int(variant), int(quantity))
                stock.movement_type = Stock.RN
                stock.save()
                allocation = Allocations.objects.get(pk=int(allocation_id))
                
                StockTransactions.objects.create(
                        variant= allocation.variant,
                        quantity = int(quantity),
                        txn_type = StockTransactions.RN,
                        txn_date = datetime.now(),
                        created_by = request.user,
                        contenttype = allocation.contenttype,
                        reference = allocation.content_object.id
                    )
                
                Returns.objects.create(
                    allocation = allocation,
                    variant = Variant.objects.get(pk=int(variant)),
                    returned_by = request.user,
                    quantity = int(quantity),
                    condition = Returns.CONDITION_CHOICES[int(condition)][0]
                )
                if allocation.quantity == 0:
                    allocation.delete()
                messages.success(request, 'Returned successfully')
        
    return redirect('allocate:allocation_list')


@is_manager
def delete_allocation(request):
    if request.method == 'POST':
        id = request.POST.get('allocation_id')
        allocation = Allocations.objects.get(pk=int(id))
        allocation.delete()
        messages.success(request, 'Allocation deleted successfully')
    return redirect('allocate:allocation_list')



@is_manager
def product_view(request):
    categories = Category.objects.all()
    items = Item.objects.all()
    
    if request.method == 'GET':
        category_id = request.GET.get('category', None)
        if category_id is None:
            items = Item.objects.all()
        else:
            items = Item.objects.filter(category=int(category_id))
        print('items', items)
    
    context = {
        'categories': categories,
        'items': items
    }
    
    return render(request, 'allocate/product_view.html', context)


def product_detail_view(request, pk):
    categories = Category.objects.all()
    product = Item.objects.get(pk=pk)
    
    variants = product.variant.all()
    
    for v in variants:
        if v.is_serialized:
            serial_numbers = Serialnumber.objects.filter(product_variant=v, item=product)
            print('serial_numbers', serial_numbers)
        else:
            serial_numbers = None
            print('serial_numbers', serial_numbers)
            
    context = {
        'categories': categories,
        'product': product,
    }
    return render(request, 'allocate/product_detail.html', context)


def add_to_allocation_item(request):
    if request.method == 'POST':
        variants = request.POST.getlist('variant')
        
        variants = [int(v) for v in variants]
        
        cart = request.session.get('allocation_cart', [])
        
        for v in variants:
            if v not in cart:
                cart.append(v)

        request.session['allocation_cart'] = cart
        
        return redirect('allocate:product_view')

    return redirect('allocate:product_view')


def allocation_cart(request):
    cart = request.session.get('allocation_cart', [])
    employees = Employee.objects.all()
    variants = Variant.objects.filter(id__in=cart)
    locations = Location.objects.all()
    
    if request.method == 'GET':
        variant_id = request.GET.get('id', None)
        if variant_id is None:
            variants = Variant.objects.filter(id__in=cart)
        else:
            variant_id = int(variant_id)
            if variant_id in cart:
                cart.remove(variant_id)
                request.session['allocation_cart'] = cart
            variants = Variant.objects.filter(id__in=cart)
    
    context = {
        'employees': employees,
        'variants': variants,
        'locations': locations
    }
    return render(request, "allocate/cart.html", context)





def allocate_items(request):
    
    if request.method != "POST":
        return redirect("allocate:product_view")

    cart = request.session.get("allocation_cart", [])

    if not cart:
        messages.error(request, "No items selected for allocation.")
        return redirect("allocate:product_view")

    employee_id = request.POST.get("employee")
    location_id = request.POST.get("location")

    # Validate required fields
    if not employee_id or not location_id:
        messages.error(request, "Employee or location not selected.")
        return redirect("allocate:product_view")

    # Fetch all variants in one go (optimised)
    variants = Variant.objects.filter(id__in=cart).select_related().all()

    # Pre-check stock before allocating anything
    for v in variants:
        try:
            stock = Stock.objects.get(variant_id=v.id)
        except Stock.DoesNotExist:
            messages.error(request, f"Stock not found for {v.name}.")
            return redirect("allocate:product_view")

        if v.is_serialized:
            serial_qs = Serialnumber.objects.filter(product_variant=v.id, status=Serialnumber.NS)
            if not serial_qs.exists():
                messages.error(request, f"No available serial numbers for {v.name}.")
                return redirect("allocate:product_view")
        else:
            if stock.quantity < 1:
                messages.error(request, f"Insufficient stock for {v.name}.")
                return redirect("allocate:product_view")

    # All validations passed — now begin atomic allocation
    with transaction.atomic():

        allocation = Allocations.objects.create(
            issued_by=request.user,
            contenttype=ContentType.objects.get_for_model(Employee),
            allocated_to=int(employee_id),
            location=Location.objects.get(pk=int(location_id)),
        )

        # Process each variant
        for v in variants:

            # Create AllocationItem FIRST only after stock check
            AllocationItem.objects.create(
                allocation=allocation,
                variant=v,
                quantity=1
            )

            # SERIALIZED PRODUCT FLOW
            if v.is_serialized:
                serial_obj = Serialnumber.objects.filter(
                    product_variant=v.id,
                    status=Serialnumber.NS
                ).first() 
                serial_obj.status = Serialnumber.AL
                serial_obj.save()

                StockTransactions.objects.create(
                    variant=v,
                    quantity=1,
                    txn_type=StockTransactions.OT,
                    txn_date=datetime.now(),
                    created_by=request.user,
                    contenttype=allocation.contenttype,
                    reference=allocation.allocated_to
                )

            # NORMAL COUNT-BASED STOCK
            else:
                stock = Stock.objects.select_for_update().get(variant_id=v.id)
                stock.quantity -= 1
                stock.movement_type = Stock.OT
                stock.save()

                StockTransactions.objects.create(
                    variant=v,
                    quantity=1,
                    txn_type=StockTransactions.OT,
                    txn_date=datetime.now(),
                    created_by=request.user,
                    contenttype=allocation.contenttype,
                    reference=allocation.allocated_to
                )

        # Clear cart
        request.session["allocation_cart"] = []

    messages.success(request, "Allocation created successfully.")
    log_action(request.user, request=request, action="Created allocation", instance=allocation, extra={"allocated_item_ids":[v.id for v in variants] })
    return redirect("allocate:allocation_list")


def allocation_detail(request, pk):
    allocation = Allocations.objects.get(pk=pk)

    items_allocated = AllocationItem.objects.filter(allocation=allocation)
    status_list = Returns.CONDITION_CHOICES
    
    # return form
    ReturnItemFormSet = modelformset_factory(
        ReturnItem,
        form=ReturnItemForm,
        extra=items_allocated.count(),
    )
    
    context = {
        'items_allocated': items_allocated,
        'allocation': allocation,
        'status_list': status_list,
    }
    
    if request.method == 'POST':
        form_data = request.POST.copy()
        return_allocated_items(request,form_data, allocation_id = allocation.id)
    return render(request, 'allocate/allocation_detail.html', context)



def return_allocated_items(request, form_data=None, allocation_id=None):
    if not form_data:
        return redirect('allocate:allocation_detail', pk=allocation_id)

    items = form_data.getlist('items')
    statuses = form_data.getlist('status')
    item_status_map = dict(zip(items, statuses))

    allocation = Allocations.objects.get(id=allocation_id)

    with transaction.atomic():

        return_record = Returns.objects.create(
            allocation=allocation,
            returned_by=request.user
        )

        return_ct = ContentType.objects.get_for_model(Returns)

        for variant_id, condition in item_status_map.items():

            variant_id = int(variant_id)
            variant = Variant.objects.get(id=variant_id)

            # Create ReturnItem
            ReturnItem.objects.create(
                return_record=return_record,
                variant_id=variant_id,
                quantity=1,
                condition=condition
            )

            # Serialized item → mark serial as not-in-stock
            if variant.is_serialized:
                serial = Serialnumber.objects.filter(
                    product_variant=variant,
                    status=Serialnumber.AL
                ).first()

                if serial:
                    serial.status = Serialnumber.NS
                    serial.save()

                StockTransactions.objects.create(
                    variant=variant,
                    quantity=1,
                    txn_type=StockTransactions.RN,
                    txn_date=datetime.now(),
                    created_by=request.user,
                    contenttype=return_ct,
                    reference=return_record.id
                )

            else:
                stock = Stock.objects.select_for_update().get(variant=variant)
                stock.quantity += 1
                stock.movement_type = Stock.RN
                stock.save()

                StockTransactions.objects.create(
                    variant=variant,
                    quantity=1,
                    txn_type=StockTransactions.RN,
                    txn_date=datetime.now(),
                    created_by=request.user,
                    contenttype=return_ct,
                    reference=return_record.id
                )

            # Reduce allocation quantity
            try:
                allocation_item = AllocationItem.objects.select_for_update().get(
                    allocation=allocation,
                    variant=variant
                )
            except AllocationItem.DoesNotExist:
                continue

            if allocation_item.quantity > 1:
                allocation_item.quantity -= 1
                allocation_item.save()
            else:
                allocation_item.delete()

        if not allocation.allocationitem_set.exists(): 
            allocation.delete()

        messages.success(request, "Return created successfully.")

        log_action(
            request.user,
            request=request,
            action="returned items",
            instance=return_record,
            extra={"return_item_ids": items}
        )

    return redirect('allocate:allocation_detail', pk=int(allocation_id))



