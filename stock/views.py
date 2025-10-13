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
                
                with transaction.atomic():
                    stock = in_stock.save()
                    StockTransactions.objects.create(
                        variant= in_stock.variant,
                        quantity = int(self.request.POST.get('quantity')),
                        txn_type = StockTransactions.AD,
                        created_by = self.request.user,
                        contenttype =  ContentType.objects.get_for_model(Stock),
                        reference = in_stock.pk
                    )
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
                            StockTransactions.objects.create(
                                variant= stock.variant,
                                quantity = len(created_serials),
                                txn_type = StockTransactions.IN,
                                created_by = self.request.user,
                                contenttype =  ContentType.objects.get_for_model(Stock),
                                reference = stock.pk
                            )     
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
                    with transaction.atomic():
                        stock = form.save(commit=False)
                        stock.movement_type = Stock.IN
                        stock.save()
                        print('new record')
                        StockTransactions.objects.create(
                            variant= stock.variant,
                            quantity = stock.quantity,
                            txn_type = StockTransactions.IN,
                            created_by = self.request.user,
                            contenttype =  ContentType.objects.get_for_model(Stock),
                            reference = stock.pk
                        )
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
        stock = form.save(commit=False)
        stock.movement_type = Stock.AD
        
        with transaction.atomic():
            stock.save()        
            StockTransactions.objects.create(
                variant = stock.variant,
                txn_type = StockTransactions.AD,
                quantity = int(self.request.POST.get('quantity')),
                created_by = self.request.user,
                contenttype = ContentType.objects.get_for_model(stock),
                reference = stock.id
            )
            messages.success(self.request, 'Stock updated successfully')
        return super().form_valid(form)
    
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
    


class StockTransactionList(ListView):
    model = StockTransactions
    context_object_name = 'transactions'
    template_name = 'stock/transaction_list.html'
    ordering = ['-txn_date']





class PurchaseListView(ListView, FormView):
    model = Purchase
    template_name = 'stock/tables/purchase_list.html'
    context_object_name = 'purchases'
    paginate_by = PAGINATED_BY
    ordering = ['-created_at']
    form_class = DownloadForm


class PurchaseDetailView(DetailView):
    model = Purchase
    template_name = 'stock/purchase_detail.html'


class StudentListView(ListView):
    model = Student
    template_name = 'stock/tables/student_list.html'
    context_object_name = 'students'
    paginate_by = PAGINATED_BY





# The list of issued kits
class IssueListView(ListView, FormView):
    model = Issue
    template_name = 'stock/tables/issue_list.html'
    context_object_name = 'kits'
    paginate_by = PAGINATED_BY
    form_class = DownloadForm
    

    def get_context_data(self, **kwargs):
        kwargs['date_min'] =( date.today()- timedelta(days=365*10)).isoformat()
        kwargs['date_max'] = (date.today() - timedelta(days=365*5)).isoformat()
        return super().get_context_data(**kwargs)
    
class IssueDetailView(DetailView):
    model = Issue
    template_name = 'stock/issue_detail.html'
    context_object_name = 'kits'


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