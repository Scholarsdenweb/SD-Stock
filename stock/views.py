from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from stock.forms import *
from django.contrib import messages
from django.core import serializers

from django.views.generic import ListView, DetailView, FormView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from stock.utils import *
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .send_sms import send_sms
from datetime import date, timedelta
from django.db.models import Q

# from template_partials.shortcuts import render_partial

import json

PAGINATED_BY = 10

# Create your views here.
class ItemCreateView(CreateView):
    template_name = 'stock/item_form.html'
    form_class = ItemForm
    success_url = reverse_lazy('stock:purchase_list')

    def form_valid(self, form):
        form.cleaned_data
        messages.success(self.request, 'Item added successfully')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Item not added')
        return super().form_invalid(form)
  
def add_success_view(request):
    return render(request, 'stock/add_success.html')  

@login_required()
def create_item(request):
    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            try:
                item = form.save()
                messages.success(request, 'Item {} added successfully'.format(item))
                return render(request, 'stock/add_success.html', {'form': form})
            except ValidationError as e:
                messages.error(request, e.messages[0])
            return render(request, 'stock/item_form.html', {'form': form})
    else:
        form = ItemForm()
    

    itemlist = Item.objects.all()

    return render(request, 'stock/item_form.html', {'form': form, 'itemlist': itemlist})    

class ItemUpdateView(UpdateView):
    model = Item
    form_class = ItemForm
    success_url = reverse_lazy('stock:add_item')
    


@login_required()
def create_purchase_view(request):
    
    if request.method == 'POST':
        form = PurchaseForm(request.POST)
        if form.is_valid():
            purchase = form.save(commit=False)
            purchase.user = request.user

            purchase.save()

            # find item in stock
            item_in_stock = Stock.objects.filter( stock_item=purchase.item).first()

            if item_in_stock:
                item_in_stock.quantity += purchase.quantity
                item_in_stock.save()

            else:
                stock = Stock.objects.create(user=request.user, stock_item=purchase.item, quantity=purchase.quantity)
                stock.save()
               



            # Record the transaction
            transaction = Transaction.objects.create(item=purchase.item, transaction_type=Transaction.PURCHASE, quantity=purchase.quantity, reference_id=purchase.pk, reference_model=purchase.__class__.__name__, notes="Item purchased" ,manager=request.user)
            transaction.save()


            messages.success(request, "{}, {} updated in purchase list".format(purchase.quantity,  purchase))

            return render(request, 'stock/purchase_success.html', {'form': form})


        else:
            messages.error(request, "Couldn't add item")
            return render(request, 'stock/purchase_form.html', {'form': form})
        
    form = PurchaseForm()
    
    
    return render(request, 'stock/purchase_form.html', {'form': form})



@login_required()
def create_stock_view(request):
    if request.method == "POST":

        """
        Function to add an item to the stock.
        """

        form = StockForm(request.POST)

        if form.is_valid():
            stock = form.save(commit=False)
            stock.user = request.user
            existing_stock = Stock.objects.filter(user=request.user, stock_item=stock.stock_item.id).first()
            existing_purchage = Purchase.objects.get(user=request.user, item=stock.stock_item.id)

            if existing_stock:

                if existing_stock.quantity < existing_purchage.quantity:
                    update_stock_quantity(request, stock.stock_item, stock.quantity)
                    messages.success(request, '{} is updated in the stock'.format(existing_stock.stock_item.__str__().upper()))
                    return render(request, 'stock/stock_form.html', {'form': form})
                else:
                    messages.error(request, 'This addition is going beyond the purchased quantity of {}. Already added.'.format(existing_purchage.quantity))
                    return render(request, 'stock/stock_form.html', {'form': form})

            stock.save()
            messages.success(request, '{} is added in the stock'.format(stock))
            return render(request, 'stock/stock_form.html', {'form': form})
                   
    form = StockForm()
    return render(request, 'stock/stock_form.html', {'form': form})





@login_required()
def issue_kit(request):
    if request.method == 'POST':
        form = IssueForm(request.POST)
        
        for id in request.POST.getlist('items', None):
            print('on post',id)

        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user

            # check if there exists a issuance with this enrollement

            issuance_exist = Issue.objects.filter(student=obj.student).first()

            if issuance_exist:
                selected_items = request.POST.getlist('items', None)

                for item in selected_items:
                    stock = update_stock_quantity(request, item, -1)

                    if stock.quantity > 0:
                        issuance_exist.items.add(item)
                        issuance_exist.save()
                    else:
                        messages.error(request, '{} - Out of stock'.format(item))
                        return render(request, 'stock/tables/issue_list.html', {'form': form})

                    if stock.quantity == 0:
                        stock.delete()
                        stock.save()
                    tr_item = Item.objects.get(pk=int(item))

                    transaction = Transaction.objects.create(item=tr_item, transaction_type=Transaction.ISSUE, quantity=issuance_exist.quantity, reference_id=issuance_exist.student.pk, reference_model=obj.__class__.__name__, manager=request.user, notes="Item issued")
                    transaction.save()


                messages.success(request, 'Kit issued successfully')
                return render(request, 'stock/success.html', {'form': form})
            else:
                # obj.save()
                # form.save_m2m()
                selected_items = form.cleaned_data['items']

                for item in selected_items:
                    # stock = Stock.objects.get(user=request.user, stock_item=item)
                    
                    try:
                        # stock = Stock.objects.get(stock_item=item)
                        stock = Stock.objects.get(pk=int(item.id))
                        if stock.quantity > 0:
                            stock = update_stock_quantity(request, item.id, -1)
                            obj.save()
                            form.save_m2m()
                            transaction = Transaction.objects.create(item=item, transaction_type=Transaction.ISSUE, quantity=obj.quantity, reference_id=obj.id, reference_model=obj.__class__.__name__, manager=request.user, notes="Item issued")
                            transaction.save()
                            messages.success(request, 'Kit {} issued successfully'.format(selected_items))
                            return render(request, 'stock/success.html', {'form': form})
                        else:
                            messages.error(request, '{} - Out of stock'.format(selected_items))
                            return render(request, 'stock/issue_form.html', {'form': form})
                    except Stock.DoesNotExist:
                        messages.error(request, '{} - Out of stock'.format(selected_items))
                        return render(request, 'stock/success.html', {'form': form})

        else:
            messages.error(request, 'Form is not valid')
            print(form.errors)
            return render(request, 'stock/issue_form.html', {'form': form})


    # find issued kit with the enrollement no and modify the selection
    dob = request.GET.get('dob', None)
    enrollement = request.GET.get('enrollement', None)
    name = request.GET.get('name', None)
    
    student = find_student(name, dob, enrollement)
    
    issued_kit = Issue.objects.filter(Q(enrollement=enrollement) | Q(student=student) ).first()
    
    
    # items = Stock.objects.all()
    items = Item.objects.all()
    stocks = Stock.objects.all()
    
    for i in items:
        for st in stocks:
            if i != st.stock_item:
                items = Item.objects.exclude(pk=i.pk)

    if issued_kit is not None:
        given_items = issued_kit.items.all()
        
        for item in given_items:
           if item in items:
               items = items.exclude(pk=item.pk)
        
    
    form = IssueForm()
    form.fields['items'].queryset = items
    form.fields['enrollement'].initial = int(request.GET.get('enrollement'))
    form.fields['enrollement'].widget.attrs['readonly'] = True
    form.fields['student'].initial = student
    form.fields['student'].widget.attrs['readonly'] = True
    return render(request, 'stock/issue_form.html', {'form': form})




class PurchaseListView(LoginRequiredMixin,ListView, FormView):
    model = Purchase
    template_name = 'stock/tables/purchase_list.html'
    context_object_name = 'purchases'
    paginate_by = PAGINATED_BY
    ordering = ['-created_at']
    form_class = DownloadForm

    def post(self, request, *args, **kwargs):
        responce = download_purchases(self, request)

        return responce
class PurchaseUpdateView(LoginRequiredMixin, UpdateView):
    model = Purchase
    template_name = 'stock/purchase_form.html'
    form_class = PurchaseForm
    success_url = reverse_lazy('stock:purchase_list')



class PurchaseDetailView(LoginRequiredMixin, DetailView):
    model = Purchase
    template_name = 'stock/purchase_detail.html'

class StockListView(LoginRequiredMixin, ListView, FormView):
    model = Stock
    template_name = 'stock/tables/stock_list.html'
    context_object_name = 'stocks'
    form_class = DownloadForm
    paginate_by = PAGINATED_BY

    def post(self, request, *args, **kwargs):
        responce = download_stock(self, request)

        return responce

class StudentListView(LoginRequiredMixin, ListView):
    model = Student
    template_name = 'stock/tables/student_list.html'
    context_object_name = 'students'
    paginate_by = PAGINATED_BY




class StockDetailView(LoginRequiredMixin, DetailView):
    model = Stock
    template_name = 'stock/stock_detail.html'


class TransactionListView(LoginRequiredMixin, ListView, FormView):
    model = Transaction
    template_name = 'stock/tables/transaction_list.html'
    context_object_name = 'transactions'
    paginate_by = PAGINATED_BY
    form_class = DownloadForm

    def post(self, request, *args, **kwargs):
        responce = download_transactions(self, request)

        return responce


class IssueListView(LoginRequiredMixin, ListView, FormView):
    model = Issue
    template_name = 'stock/tables/issue_list.html'
    context_object_name = 'kits'
    paginate_by = PAGINATED_BY
    form_class = DownloadForm

    def post(self, request, *args, **kwargs):
        responce = download_kits(self, request)

        return responce
    def get_context_data(self, **kwargs):
        kwargs['date_min'] =( date.today()- timedelta(days=365*10)).isoformat()
        kwargs['date_max'] = (date.today() - timedelta(days=365*5)).isoformat()
        return super().get_context_data(**kwargs)
    

    




def search_issued_items(request):
    kitlist= []
    if request.method == 'POST':
        
        name = request.POST.get('name', None)
        dob = request.POST.get('dob', None)
        enrollement = request.POST.get('enrollement', None)
        
        student = find_student(name, dob, enrollement)
        
        
        kits = Issue.objects.filter(student=student).first()
        if  kits is None:
            return render(request, 'partials/search_button.html', {'kitlist': kitlist, 'name': name, 'dob': dob, 'enrollement': enrollement})
            # return HttpResponse("<p class='text-warning'>Please enter valid enrollement number</p><button type='button'>Search</button>")
        else:
            items = kits.items.all()

            for i in items:
                kitlist.append(i)
        # return render(request, 'partials/return_list.html', {'kitlist': kitlist,  'name': name, 'dob': dob, 'enrollement': enrollement})
        return render(request, 'partials/return_list.html', {'kitlist': kitlist, 'student': student})
  
    context = dict(
        min_date = (date.today() - timedelta(days=365*10)).isoformat(),
        max_date = (date.today() - timedelta(days=365*5)).isoformat(),
    )
    return render(request, 'stock/return_form.html', context)    


def return_kit(request):
    if request.method == 'POST':
        enrollement = request.POST.get('enrollement')
        dob = request.POST.get('dob')
        name = request.POST.get('name')
        
        student = find_student(name, dob, enrollement)
        
        issued_kit = Issue.objects.filter(student=student).first()
        returning_items = []
        
        if not issued_kit:
            return JsonResponse({'error': 'No kit found'}, status=404)

        for item in request.POST.getlist('items[]'):
            item = Item.objects.get(pk=int(item))
            issued_kit.items.remove(item)
           
            update_stock_quantity(request, item, issued_kit.quantity)
            
            if issued_kit.items.count() == 0:
                issued_kit.delete()
            else:
                issued_kit.save()

            returning_items.append(item)

            tr = Transaction.objects.create(
                item=item,
                transaction_type=Transaction.RETURN,
                quantity=issued_kit.quantity,
                manager=request.user,
                reference_id = issued_kit.student.pk,
                notes='returned from {}'.format(issued_kit.student.name)
            )

            tr.save()

           
        messages.success(request, 'Kit {} for enrolement no. {} is returned'.format(returning_items, student.enrollement))
        send_sms(
            api_key = "2MLivU4Q3tyFXr1WJcNB8l5YhzT0pAesdoIxRPGwuCSgObZmkVMbkSmGBYOAgHrNosjUhXy854JL269E", 
            message_id = '186973',
            variables_values = returning_items,
            numbers= student.phone, 
            sender_id="SCHDEN"
        )
        
       
    return render(request, 'stock/return_success.html')




def filter_student(request):
    print('find student')
    
    if request.method == 'POST':
        full_name = request.POST.get('full_name', None)
        dob = request.POST.get('dob', None)
        enrollement = request.POST.get('enrollement', None)
        
        student = find_student(full_name, dob, enrollement)
        
        if student is not None:
            url = reverse('stock:issue_kit')
            

            return HttpResponse(f"<div class='bg-success-subtle text-success p-2'><p class='text-success'>One student found with following detailes:</p><p>Name: {student.name}</p><p>Father's Name: {student.father_name}</p><p>Date of Birth: {student.get_dob()}</p><p>Phone Number: {student.phone}</p></div><button type='submit' class='btn btn-primary mt-3'><a class='text-white link-underline link-underline-opacity-0' href='{url}?enrollement={student.enrollement}&name={full_name}&dob={dob}'>Issue Kit</button>")
        
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
    
