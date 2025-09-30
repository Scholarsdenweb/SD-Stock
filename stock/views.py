from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.contrib import messages

from django.views.generic import ListView, DetailView, FormView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from stock.utils import *
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, QueryDict
from .send_sms import send_sms
from datetime import date, timedelta
from django.db.models import Q
from django.forms import inlineformset_factory, formset_factory
from django.db import transaction, IntegrityError
from django.utils.safestring import mark_safe
from django.db.models import F

from django.views.generic.edit import FormMixin
from .models import *
from django.utils.decorators import method_decorator
from authapp.decorators import is_manager
from .forms import *

# from template_partials.shortcuts import render_partial
import json




PAGINATED_BY = 10

@method_decorator(is_manager, name='dispatch')
class VendorsCreateView(CreateView):
    model = Vendor
    template_name = 'stock/vendor/vendor_list.html'
    context_object_name = 'vendors'
    form_class = VendorForm
    success_url = reverse_lazy('stock:vendor_list')
    
    def get_context_data(self, **kwargs):
        vendors = Vendor.objects.all()
        context =  super().get_context_data(**kwargs)
        context['vendors'] = vendors
        return context
    
    def form_valid(self, form):
        print('valid')
        form.save()
        messages.success(self.request, 'Vendor added successfully')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        response = super().form_invalid(form)
        messages.error(self.request, f'Vendor not added. Try again.')
        return response
    
    
def add_success_view(request):
    return render(request, 'stock/add_success.html') 
        


@method_decorator(is_manager, name='dispatch')
class StockCreate(CreateView):
    model = Stock
    context_object_name = 'stocks'
    template_name = 'stock/create_stock.html'
    form_class = StockForm
    success_url = reverse_lazy('stock:create_stock')
    
    
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        stocks = Stock.objects.all()
        context['stocks'] = stocks
        return context
    
    def form_valid(self, form):
        stock = form.save(commit=False)
        item = form.instance.variant.product
        variant = form.instance.variant
        
        in_stock = Stock.objects.filter(variant=stock.variant, location=stock.location, variant__product=item).first()
        
        if in_stock and not variant.is_serialized and not self.request.POST.get("confirm"):
            if self.request.headers.get('hx-request'):
                print('valid')
                form_data = self.request.POST
                stock_data = {
                    'location': Location.objects.get(pk = form_data.get('location')),
                    'variant': Variant.objects.get(pk=form_data.get('variant')),
                    'quantity': int(form_data.get('quantity')) + in_stock.quantity,
                }
                return render(self.request, 'partials/confirm_stock.html', {'stock': in_stock, 'message': 'Stock already exist', 'class': 'text-danger', 'form_data': self.request.POST, 'stock_data': stock_data})
            
        if in_stock and not variant.is_serialized and self.request.POST.get("confirm"):
            if self.request.headers.get('hx-request'):
                form = StockForm(self.request.POST, instance=in_stock)
                in_stock.quantity += int(self.request.POST.get('quantity'))
                stock = in_stock.save()
                messages.success(self.request, "Stock updated successfully")
                return render(self.request, "partials/stock_detail.html", {"stock": stock})
        else:
            if self.request.headers.get('hx-request'):
                serial_number = self.request.POST.getlist('serial')
                if serial_number:
                    serialnumber_obj = Serialnumber.objects.filter(serial_number__in=serial_number)
                    
                    if serialnumber_obj.exists():
                        messages.error(self.request, f'Below serial numbers already exists')
                        return render(self.request, 'partials/stock_detail.html', {'serialnumber_obj': serialnumber_obj, 'class': 'text-danger'})
                    else:
                       try: 
                        with transaction.atomic():
                            if in_stock:
                                stock = in_stock
                            else:
                                stock = form.save()
                            created_serials = []
                            for serial in serial_number:
                                try:
                                    sn = Serialnumber.objects.create(
                                        item=item,
                                        product_variant=stock.variant,
                                        serial_number=serial
                                    )
                                    
                                    created_serials.append(sn)
                                    # increment quantity atomically
                                    Stock.objects.filter(id=stock.id).update(quantity=F('quantity') + 1)
                                except IntegrityError:
                                    messages.warning(self.request, f"⚠️ Serial number '{serial.strip()}' is duplicate and not allowed. Try again.")
                                    return render (self.request, 'partials/stock_detail.html', {'class': 'text-danger'})
                                 
                            stock.refresh_from_db()
                            
                            if created_serials:
                                messages.success(self.request, f'Total {len(created_serials)} serial numbers added successfully')
                                sr_object = Serialnumber.objects.filter(serial_number__in=serial_number)
                            
                            context = {'class': 'text-success', 'serialnumber_obj': sr_object}
                            response =  render(self.request, 'partials/stock_detail.html', context)
                            response['HX-Target'] = '#response_message'
                            return response
                       except Exception as e:
                            messages.error(self.request, f'Error: {str(e)}')
                            return render(self.request, 'partials/stock_detail.html', {'class': 'text-danger'})
                else:
                    stock = form.save()
                    message = f'Stock added successfully'
                    context = {'stock': stock, 'message': message, 'class': 'text-success'}
                    response =  render(self.request, 'partials/stock_detail.html', context)
                    response['HX-Target'] = '#response_message'
                    return response
    
    def form_invalid(self, form):
        if self.request.headers.get('hx-request'):
            print('invalid')
            item = form.cleaned_data['variant']
            variant = form.cleaned_data['variant']
            location = form.cleaned_data['location']
            stock = Stock.objects.filter(variant=variant.pk, location=location.pk).first()
            message = "Stock already exists"
            context = {'stock': stock, 'message': message, 'class': 'text-danger'}
            response = render(self.request, 'partials/stock_detail.html', context)
            response['HX-Target'] = '#response_message'
            return response
        
        return super().form_invalid(form)    
    
    def get(self, request, *args, **kwargs):
        self.object = None  

        if request.headers.get('hx-request'):
            context = self.get_context_data(**kwargs)
            form = self.form_class()
            context['form'] = form
            return render(request, 'partials/create_stock_form.html', context)

        search_text = request.GET.get('search', '')
        
        if search_text:
            stock = search_stock(search_text)
        else:
            stock = Stock.objects.all()
        

        context = self.get_context_data(**kwargs)
        form = self.form_class()
        context['form'] = form
        context['stocks'] = stock

        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        if request.headers.get('hx-request'):
            return super().post(request, *args, **kwargs)
        
        response = download_stock_records(qs=Stock.objects.all())
        
        return response





# stock edit view   
@is_manager 
def edit_stock(request, pk):
    stock = get_object_or_404(Stock, pk=pk)
    form = StockEditForm(instance=stock)
    context = {'form': form, 'stock': stock}
    return render(request, 'stock/edit_stock_form.html', context)
 
@is_manager        
def edit_stock_with_serials(request, pk): 
    context = {}
    stock = get_object_or_404(Stock, pk=pk)
    serials = Serialnumber.objects.filter(product_variant=stock.variant)
    stock_form = StockEditForm(instance=stock)

    if request.method == 'POST':
        stock_form = StockEditForm(request.POST, instance=stock)
        print('data', request.POST)
        if stock_form.is_valid():
            stock_instance = stock_form.save(commit=False)
            old_variant = Stock.objects.get(pk=stock_instance.pk).variant
            stock_instance.save()
            
            if old_variant != stock_instance.variant:
                serials_to_update = Serialnumber.objects.filter(product_variant=old_variant)
                serials_to_update.update(
                    item=stock_instance.variant.product,
                    product_variant=stock_instance.variant
                )
            
            messages.success(request, "Stock and serials updated successfully.")
            context['serial_numbers'] = serials
            return redirect('stock:edit_stock_with_serials', pk=stock.pk)
        else:
            print('form error', stock_form.errors)
            context['stock_form'] = stock_form
            
            messages.error(request, "Please correct the errors below.")
            return render(request, 'stock/edit_stock_with_serials.html', context=context)
        
    stock_form.fields['quantity'].widget.attrs.update({
    'readonly': True,
    'style': 'background-color:#e9ecef; cursor:not-allowed;'
    })

    context['stock_form'] = stock_form
    context['serial_numbers'] = serials
    context['stock'] = stock
    return render(request, 'stock/edit_stock_with_serials.html', context=context)                

def stock_detail(request, pk):
    stock = get_object_or_404(Stock, pk=pk)
    if request.method == 'GET':
        if request.headers.get('hx-request'):
            return render(request, 'partials/stock_detail.html', {'stock': stock})
    elif request.method == 'PUT':
        data = QueryDict(request.body).dict()
        form = StockEditForm(data, instance=stock)
        if form.is_valid():
            form.save()
            return render(request, 'partials/stock_detail.html', {'stock': stock})
        context = {'form': form, 'stock': stock}
        return render(request, 'stock/edit_stock_form.html', context)
            
def serial_detail(request, pk):
    serial = get_object_or_404(Serialnumber, pk=pk)
    if request.method == 'GET':
        if request.headers.get('hx-request'):
            return render(request, 'partials/stock_detail.html', {'serialnumber_obj': serial})
        
    elif request.method == 'PUT':
        data = QueryDict(request.body).dict()
        form = SerialEditForm(data, instance=serial)
        if form.is_valid():
            form.save()
            return render(request, 'partials/stock_detail.html', {'serialnumber_obj': serial})
        context = {'form': form, 'serialnumber_obj': serial}
        return render(request, 'stock/edit_serial_form.html', context)

@is_manager    
def edit_serial(request, pk):
    serial = get_object_or_404(Serialnumber, pk=pk)
    form = SerialEditForm(instance=serial)
    context = {'form': form, 'serialnumber_obj': serial}
    
    return render(request, 'stock/edit_serial_form.html', context)    
 

            
class ItemDetailView(DetailView):
    model = Stock
    context_object_name = 'item'
    template_name = 'stock/item_detail.html'


# class base update views 
@method_decorator(is_manager, name='dispatch')
class UpdateSerialNumber(UpdateView):
    model = Serialnumber
    template_name = 'stock/editforms/serial_number_form.html'
    form_class = SerialEditForm
    
    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Serial number updated successfully')
        self.success_url = reverse_lazy('stock:update_serial_number', kwargs={'pk': self.kwargs['pk']})
        return super().form_valid(form)

@method_decorator(is_manager, name='dispatch')
class UpdateStock(UpdateView):
    model = Stock
    template_name = 'stock/editforms/stock_form.html'
    form_class = StockEditForm
    success_url = reverse_lazy('stock:create_stock')
    
    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Stock updated successfully')
        return super().form_valid(form)
    




    
    

        

# class CreateSerialNumber(CreateView):
#     model = Serialnumber
#     template_name = 'stock/create_serial_number.html'
#     form_class = SerialNumberForm
#     success_url = reverse_lazy('stock:create_stock')

#     def get_variant(self):
#         return Variant.objects.get(pk=self.kwargs['pk'])

#     def get_formset(self, data=None, extra=0):
#         variant = self.get_variant()
#         SerialFormSet = formset_factory(SerialNumberForm, extra=extra)
#         formset = SerialFormSet()

#         if data:
#             return SerialFormSet(data, prefix="serial")
#         else:
#             initial_data = [{'item': variant.product, 'product_variant': variant}]
#             formset = SerialFormSet(initial=initial_data, prefix="serial")
#             for form in formset:
#                 form.fields['product_variant'].disabled = True
#                 form.fields['item'].disabled = True
#             return formset

#     def get_context_data(self, **kwargs):
#         self.object = getattr(self, "object", None)
#         context = super().get_context_data(**kwargs)
#         context['variant'] = self.get_variant()
#         context['formset'] = kwargs.get("formset") or self.get_formset()
#         return context


#     def post(self, request, *args, **kwargs):
#         formset = self.get_formset(data=request.POST)
#         if formset.is_valid():
#             for form in formset:
#                 if form.cleaned_data:
#                     print(formset) # avoid empty rows
#                     form.save()
#             messages.success(request, "Serial numbers added successfully")
#             return redirect(self.success_url)
#         return self.render_to_response(self.get_context_data(formset=formset))

#     def get(self, request, *args, **kwargs):
#         if request.headers.get('hx-request'):
#             variant = self.get_variant()
#             add_count = int(request.GET.get('form_count', 1))

#             # Current total forms already rendered
#             current_total = int(request.GET.get('current_total', 0))

#             # New total = existing + newly requested
#             total_forms = current_total + add_count
#             print('total_forms', total_forms)

#             SerialFormSet = formset_factory(SerialNumberForm, extra=0)
#             initial_data = [
#                 {'item': variant.product, 'product_variant': variant}
#                 for _ in range(total_forms)
#             ]
#             formset = SerialFormSet(initial=initial_data, prefix="serial")

#             for form in formset:
#                 form.fields['product_variant'].disabled = True
#                 form.fields['item'].disabled = True

#             # Render ONLY the partial
#             return render(request, 'partials/serial_form_part.html', {'formset': formset})

#         return super().get(request, *args, **kwargs)
    
#********************************************************************************
class ProductList(ListView):
    model = Item
    template_name = 'stock/item_list.html'


# filter category wise product
def load_product_by_category(request):
    if request.headers.get('hx-request'):
        category_id = request.GET.get('category')
        category = get_object_or_404(Category, id=category_id)
        items = Item.objects.filter(category=category)
        form = VariantForm()
        form.fields['product'].queryset = items
        return render(request, 'catalogue/variant_form.html#optionpart', {'form': form})

def load_variant_by_item(request):
    if request.headers.get('hx-request'):
        item_id = request.GET.get('item')
        item = get_object_or_404(Item, id=item_id)
        variants = Variant.objects.filter(product=item)
        form = StockForm()
        form.fields['variant'].queryset = variants
        response =  render(request, 'partials/create_stock_form.html#optionpart', {'form': form})
        response['HX-Target'] = '#productoptions'
        return response
    
def check_serializable_view(request):
    if request.headers.get('hx-request'):
        variant_id = request.GET.get('variant')
        variant = get_object_or_404(Variant, id=variant_id)
        
        try:
            purchase = Purchase.objects.get(variant=variant)
            total = purchase.quantity
        except:
            total = 0  
        
        if variant.is_serialized:
            response = render(request, 'partials/serial_form_part.html')
            response['HX-Target'] = '#serial_number_container'
            return response
            

        response = HttpResponse(
            f"<p class='text-secondary'>You have total {total} purchase(s)</p><label> Quantity </label><br><input type='number' value='1' name='quantity' size='1'>"
        )
        response['HX-Target'] = '#quantity_or_serial'
        return response
        
def add_serial_view(request):
    if request.headers.get('hx-request'):
        return render(request, 'partials/serial_form_part.html')  
    
    
def remove_input_view(request):
    if request.headers.get('hx-request'):
        return render(request, 'partials/serial_form_part.html')   

# @login_required()
@is_manager
def create_item(request):
    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            try:
                item = form.save()
                messages.success(request, 'Item {} added successfully'.format(item))
                return render(request, 'stock/variant_form.html', {'form': form})
            except ValidationError as e:
                messages.error(request, e.messages[0])
            return render(request, 'stock/item_form.html', {'form': form})
    else:
        form = ItemForm()
    

    itemlist = Item.objects.all()

    return render(request, 'stock/item_form.html', {'form': form,})    

@method_decorator(is_manager, name='dispatch')
class ItemUpdateView(UpdateView):
    model = Item
    form_class = ItemForm
    success_url = reverse_lazy('stock:add_item')
    



# @login_required()
# def create_purchase_view(request):
    
#     if request.method == 'POST':
#         form = PurchaseForm(request.POST)
#         if form.is_valid():
#             purchase = form.save(commit=False)
#             purchase.user = request.user

#             purchase.save()

#             # find item in stock
#             item_in_stock = Stock.objects.filter( stock_item=purchase.item).first()

#             if item_in_stock:
#                 item_in_stock.quantity += purchase.quantity
#                 item_in_stock.save()

#             else:
#                 stock = Stock.objects.create(user=request.user, stock_item=purchase.item, quantity=purchase.quantity)
#                 stock.save()
               



#             # Record the transaction
#             transaction = Transaction.objects.create(item=purchase.item, transaction_type=Transaction.PURCHASE, quantity=purchase.quantity, reference_id=purchase.pk, reference_model=purchase.__class__.__name__, notes="Item purchased" ,manager=request.user)
#             transaction.save()


#             messages.success(request, "{}, {} updated in purchase list".format(purchase.quantity,  purchase))

#             return render(request, 'stock/purchase_success.html', {'form': form})


#         else:
#             messages.error(request, "Couldn't add item")
#             return render(request, 'stock/purchase_form.html', {'form': form})
        
#     form = PurchaseForm()
    
    
#     return render(request, 'stock/purchase_form.html', {'form': form})



# @login_required()
# def create_stock_view(request):
#     if request.method == "POST":

#         """
#         Function to add an item to the stock.
#         """

#         form = StockForm(request.POST)

#         if form.is_valid():
#             stock = form.save(commit=False)
#             stock.user = request.user
#             existing_stock = Stock.objects.filter(user=request.user, stock_item=stock.stock_item.id).first()
#             existing_purchage = Purchase.objects.get(user=request.user, item=stock.stock_item.id)

#             if existing_stock:

#                 if existing_stock.quantity < existing_purchage.quantity:
#                     update_stock_quantity(request, stock.stock_item, stock.quantity)
#                     messages.success(request, '{} is updated in the stock'.format(existing_stock.stock_item.__str__().upper()))
#                     return render(request, 'stock/stock_form.html', {'form': form})
#                 else:
#                     messages.error(request, 'This addition is going beyond the purchased quantity of {}. Already added.'.format(existing_purchage.quantity))
#                     return render(request, 'stock/stock_form.html', {'form': form})

#             stock.save()
#             messages.success(request, '{} is added in the stock'.format(stock))
#             return render(request, 'stock/stock_form.html', {'form': form})
                   
#     form = StockForm()
#     return render(request, 'stock/stock_form.html', {'form': form})





# @login_required()
# def issue_kit(request):
#     # stock_items = Stock.objects.filter(quantity__gt=0).values_list('stock_item', flat=True)
#     stock_items = Stock.objects.all()
#     IssueItemFormSet = inlineformset_factory(Issue, IssueItem, form=IssueItemForm, extra=stock_items.count())
    
#     if request.method == 'POST':
#         enrollement = request.POST.get("enrollement")
#         quantities = request.POST.getlist("quantity") 
#         issuing_items = []
        
        
#         student = Student.objects.get(enrollement=enrollement)
        
#         try:
#             with transaction.atomic():
#                 issue = Issue.objects.create(
#                     user=request.user,
#                     student=student,
#                     enrollement=enrollement
#                 )
               
#                 for index, item_id in enumerate(request.POST.getlist("items")):
#                     qty = int(quantities[index])

#                     if qty > 0:
#                         item = Item.objects.get(pk=item_id)
#                         issued_items = IssueItem.objects.create(
#                             issue=issue,
#                             item=item,
#                             quantity=qty
#                         )
                        
#                         issued_items.quantity += 1
#                         issued_items.save()
#                         issuing_items.append(Item.objects.get(pk=item_id).name)
                        
#                         transac = Transaction.objects.create(
#                         item=Item.objects.get(pk=item_id),
#                         transaction_type=Transaction.ISSUE,
#                         quantity=qty,
#                         reference_id=issue.id,
#                         reference_model=issue.__class__.__name__,
#                         manager=request.user,
#                         notes="Item {} issued to {}".format(item, issue.student)
#                         )
                        
#                         transac.save()
#                     update_stock_quantity(request, item_id, -qty)  
#                 if(student.phone):
#                     send_sms(
#                         api_key = "2MLivU4Q3tyFXr1WJcNB8l5YhzT0pAesdoIxRPGwuCSgObZmkVMbkSmGBYOAgHrNosjUhXy854JL269E", 
#                         message_id = '186973',
#                         variables_values = ", ".join(issuing_items),
#                         numbers= student.phone, 
#                         sender_id="SCHDEN"
#                     )
#         except Exception as e:
#             print(e)
#             messages.error(request, "Couldn't add item")
         
        # form = IssueForm(request.POST)

        # if form.is_valid():
        #     obj = form.save(commit=False)
        #     obj.user = request.user

        #     # check if there exists a issuance with this enrollement

        #     issuance_exist = Issue.objects.filter(student=obj.student).first()

        #     if issuance_exist:
        #         selected_items = request.POST.getlist('items', None)

        #         for item in selected_items:
        #             stock = update_stock_quantity(request, item, -1)

        #             if stock.quantity > 0:
        #                 issuance_exist.items.add(item)
        #                 issuance_exist.save()
        #             else:
        #                 messages.error(request, '{} - Out of stock'.format(item))
        #                 return render(request, 'stock/tables/issue_list.html', {'form': form})

        #             if stock.quantity == 0:
        #                 stock.delete()
        #                 stock.save()
        #             tr_item = Item.objects.get(pk=int(item))

        #             transaction = Transaction.objects.create(item=tr_item, transaction_type=Transaction.ISSUE, quantity=issuance_exist.quantity, reference_id=issuance_exist.student.pk, reference_model=obj.__class__.__name__, manager=request.user, notes="Item issued")
        #             transaction.save()


        #         messages.success(request, 'Kit issued successfully')
        #         return render(request, 'stock/success.html', {'form': form})
        #     else:
        #         # obj.save()
        #         # form.save_m2m()
        #         selected_items = form.cleaned_data['items']

        #         for item in selected_items:
        #             # stock = Stock.objects.get(user=request.user, stock_item=item)
                    
        #             try:
        #                 # stock = Stock.objects.get(stock_item=item)
        #                 stock = Stock.objects.get(pk=int(item.id))
        #                 if stock.quantity > 0:
        #                     stock = update_stock_quantity(request, item.id, -1)
        #                     obj.save()
        #                     form.save_m2m()
        #                     transaction = Transaction.objects.create(item=item, transaction_type=Transaction.ISSUE, quantity=obj.quantity, reference_id=obj.id, reference_model=obj.__class__.__name__, manager=request.user, notes="Item issued")
        #                     transaction.save()
        #                     messages.success(request, 'Kit {} issued successfully'.format(selected_items))
        #                     return render(request, 'stock/success.html', {'form': form})
        #                 else:
        #                     messages.error(request, '{} - Out of stock'.format(selected_items))
        #                     return render(request, 'stock/issue_form.html', {'form': form})
        #             except Stock.DoesNotExist:
        #                 messages.error(request, '{} - Out of stock'.format(selected_items))
        #                 return render(request, 'stock/success.html', {'form': form})

        # else:
        #     messages.error(request, 'Form is not valid')
        #     print(form.errors)
        #     return render(request, 'stock/issue_form.html', {'form': form})


    # find issued kit with the enrollement no and modify the selection
    # dob = request.GET.get('dob', None)
    # enrollement = request.GET.get('enrollement', None)
    # name = request.GET.get('name', None)
    
    # student = find_student(name, dob, enrollement)
    
    # issued_kit = Issue.objects.filter(Q(enrollement=enrollement) | Q(student=student) )
    # items = []
    
    # if issued_kit.exists():
    #     for k in issued_kit:
    #         for i in k.items.all():
    #             items.append(i)
    
    
    # items_in_stock = Item.objects.filter(id__in=stock_items)

    # form = IssueForm()
    # item_issue_formset = IssueItemFormSet()
    
    # form.fields['items'].queryset = items_in_stock
    # # form.fields['enrollement'].initial = int(request.GET.get('enrollement'))
    # form.fields['enrollement'].initial = request.GET.get('enrollement')
    # form.fields['enrollement'].widget.attrs['readonly'] = True
    # form.fields['student'].initial = student
    # form.fields['student'].widget.attrs['readonly'] = True
    
    # context = {'form': form, 'issued_kit': items, 'item_issue_formset': item_issue_formset, 'items':stock_items, 'student':student }
    
    # return render(request, 'stock/issue_form.html', context)




class PurchaseListView(ListView, FormView):
    model = Purchase
    template_name = 'stock/tables/purchase_list.html'
    context_object_name = 'purchases'
    paginate_by = PAGINATED_BY
    ordering = ['-created_at']
    form_class = DownloadForm

    # def post(self, request, *args, **kwargs):
    #     responce = download_purchases(self, request)

    #     return responce
# class PurchaseUpdateView(UpdateView):
#     model = Purchase
#     template_name = 'stock/purchase_form.html'
#     form_class = PurchaseForm
#     success_url = reverse_lazy('stock:purchase_list')



class PurchaseDetailView(DetailView):
    model = Purchase
    template_name = 'stock/purchase_detail.html'

# class StockListView(ListView, FormView):
#     model = Stock
#     template_name = 'stock/tables/stock_list.html'
#     context_object_name = 'stocks'
#     form_class = DownloadForm
#     paginate_by = PAGINATED_BY

    # def post(self, request, *args, **kwargs):
    #     # responce = download_stock(self, request)
    #     pass

    #     return responce

class StudentListView(ListView):
    model = Student
    template_name = 'stock/tables/student_list.html'
    context_object_name = 'students'
    paginate_by = PAGINATED_BY




# class StockDetailView(DetailView):
#     model = Stock
#     template_name = 'stock/stock_detail.html'


# class TransactionListView(ListView, FormView):
#     model = Transaction
#     template_name = 'stock/tables/transaction_list.html'
#     context_object_name = 'transactions'
#     paginate_by = PAGINATED_BY
#     form_class = DownloadForm

    # def post(self, request, *args, **kwargs):
    #     responce = download_transactions(self, request)

    #     return responce

# The list of issued kits
class IssueListView(ListView, FormView):
    model = Issue
    template_name = 'stock/tables/issue_list.html'
    context_object_name = 'kits'
    paginate_by = PAGINATED_BY
    form_class = DownloadForm
    

    # def post(self, request, *args, **kwargs):
    #     responce = download_kits(self, request)

        # return responce
    def get_context_data(self, **kwargs):
        kwargs['date_min'] =( date.today()- timedelta(days=365*10)).isoformat()
        kwargs['date_max'] = (date.today() - timedelta(days=365*5)).isoformat()
        return super().get_context_data(**kwargs)
    
class IssueDetailView(DetailView):
    model = Issue
    template_name = 'stock/issue_detail.html'
    context_object_name = 'kits'

# def search_issued_items(request):
#     """
#     Function to Search for issued items
#     """
#     kitlist= []
#     if request.method == 'POST':
        
#         name = request.POST.get('name', None)
#         dob = request.POST.get('dob', None)
#         enrollement = request.POST.get('enrollement', None)
        
              
#         student = find_student(name, dob, enrollement)
#         context = {'kitlist': kitlist, 'name': name, 'dob': dob, 'enrollement': enrollement}
        
#         kits = Issue.objects.filter(student=student).first()
#         if  kits is None:
#             return render(request, 'partials/search_button.html', context )
#             # return HttpResponse("<p class='text-warning'>Please enter valid enrollement number</p><button type='button'>Search</button>")
#         else:
#             items = kits.items.all()
            
#             for i in items:
#                 kitlist.append(i)
#         # return render(request, 'partials/return_list.html', {'kitlist': kitlist,  'name': name, 'dob': dob, 'enrollement': enrollement})
#         stock_items = Stock.objects.all()
#         context = {'kitlist': kitlist, 'student': student, 'stock_items': stock_items}
#         return render(request, 'partials/return_list.html', context)
  
#     context = dict(
#         min_date = (date.today() - timedelta(days=365*10)).isoformat(),
#         max_date = (date.today() - timedelta(days=365*5)).isoformat(),
#     )
#     return render(request, 'stock/return_form.html', context)    

def exchage_kit(request):
    
    """
    Function to exchange issued items
    """
    if request.method == 'POST':
        what_items = request.POST.getlist('items[]', '0')
        exhange_with = request.POST.getlist('xitems[]', '0')      
       
        resultant = zip(what_items, exhange_with)
        
        print('resultant', list(resultant))
        
            
       
        return JsonResponse({'message':tuple(resultant)})    
    
    # if request.headers.get('hx-request'):
    #     item_ids = request.GET.getlist('items[]', [])
    #     history_ids = request.session.get('selected_items', [])

    #     # merge + deduplicate
    #     all_ids = list(set(history_ids + [int(i) for i in item_ids if i.isdigit()]))

    #     request.session['selected_items'] = all_ids

    #     swapable_items = Stock.objects.filter(stock_item__category__in=all_ids)
    #     context = {'swapable_items': swapable_items}
    #     return render(request, 'partials/return_list.html', context)
    
    
    # if request.headers.get('hx-request'):
    #     item_ids = request.GET.getlist('items[]', '0')
    #     swapable_items = []
        
    #     if len(item_ids) > 0:
    #         for id in item_ids:
    #             try:
    #                 category = Category.objects.get(pk=int(id))
    #             except Category.DoesNotExist:
    #                 continue
                
    #             items = Stock.objects.filter(stock_item__category=category)
    #             print('stock cat', items[0].stock_item.category)
    #             swapable_items.extend(items)
            
    #     context = {'swapable_items': swapable_items}
    #     return render(request, 'partials/return_list.html', context)

# def return_kit(request):
#     if request.method == 'POST':
#         enrollement = request.POST.get('enrollement')
#         dob = request.POST.get('dob')
#         name = request.POST.get('name')
        
#         student = find_student(name, dob, enrollement)
        
#         issued_kit = Issue.objects.filter(student=student).first()
#         returning_items = []
        
#         if not issued_kit:
#             return JsonResponse({'error': 'No kit found'}, status=404)

#         for item in request.POST.getlist('items[]'):
#             item = Item.objects.get(pk=int(item))
#             issued_kit.items.remove(item)
           
#             update_stock_quantity(request, item, issued_kit.quantity)
            
#             if issued_kit.items.count() == 0:
#                 issued_kit.delete()
#             else:
#                 issued_kit.save()

#             returning_items.append(item)

#             tr = Transaction.objects.create(
#                 item=item,
#                 transaction_type=Transaction.EXCHANGE,
#                 quantity=issued_kit.quantity,
#                 manager=request.user,
#                 reference_id = issued_kit.student.pk,
#                 notes='returned from {}'.format(issued_kit.student.name)
#             )

#             tr.save()

           
#         messages.success(request, 'Kit {} for enrolement no. {} is returned'.format(returning_items, student.enrollement))
#         send_sms(
#             api_key = "2MLivU4Q3tyFXr1WJcNB8l5YhzT0pAesdoIxRPGwuCSgObZmkVMbkSmGBYOAgHrNosjUhXy854JL269E", 
#             message_id = '186973',
#             variables_values = returning_items,
#             numbers= student.phone, 
#             sender_id="SCHDEN"
#         )
        
       
#     return render(request, 'stock/return_success.html')




def filter_student(request):
    
    if request.method == 'POST':
        full_name = request.POST.get('full_name', None)
        dob = request.POST.get('dob', None)
        enrollement = request.POST.get('enrollement', None)
        
       
        student = find_student(full_name, dob, enrollement)
        
        if student is not None:
            url = reverse('stock:issue_kit')

            return HttpResponse(f"<div class='text-bg-dark p-2'><p class='text-warning'>One student found with following detailes:</p><p>Name: {student.name}</p><p>Father's Name: {student.father_name}</p><p>Date of Birth: {student.get_dob()}</p><p>Phone Number: {student.phone}</p></div><button type='submit' class='btn btn-primary mt-3'><a class='text-white link-underline link-underline-opacity-0' href='{url}?enrollement={student.enrollement}&name={student.name}&dob={student.get_dob()}'>Issue Kit</button>")
        
        return HttpResponse("<div class='form-group' id='searchresult'><p class='text-danger'>No student found</p> <button type='submit'   class='btn btn-dark'>Search</button> </div>")
                               
                           
def sample_excel(request):
    
    with open('stock/static/file/sample.xlsx', 'rb') as excel_file:
        data = excel_file.read()
        
    response = HttpResponse(data, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    
    response['Content-Disposition'] = 'attachment; filename="sample.xlsx"'
    return response


def transaction_detail(request, pk):
    type = request.GET.get('type', None)
    
    match type.lower():
        case 'issue' | 'return':
            student = Student.objects.get(pk=pk)
            return HttpResponse(f'<div><p>Name: {student.name}</p> <p>Roll Number: {student.roll}</p> <p>Receipt No: {student.receipt}</p>  <p>Enrollement: {student.enrollement}</p>Father\'s Name: <p>{student.father_name}</p> <p>{student.get_dob()}</p> <p></p> </div>')
        case 'purchase':
            purchage = Purchase.objects.get(pk=pk)
            return HttpResponse(f'<div><p>Item name: {purchage.item.name}</p> <p>Size: {purchage.item.size }</p> <p> Quantity: {purchage.quantity}</p>  <p>Unit Price: {purchage.unit_price}</p> <p>Total Amount: {purchage.total_amount}</p> <p>Supplier: {purchage.supplier}</p> <p>Supplier\'s location: {purchage.supplier_location}</p> <p></p> </div>')
        case _:
            return HttpResponse(f'<h1>Transaction Detail pk:{pk}, xxxx</h1>')
    


def issue_new_kit(request):
    return render(request, 'stock/issue_kit.html')