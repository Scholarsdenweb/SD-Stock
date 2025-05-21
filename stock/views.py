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
import json
# Create your views here.
class ItemCreateView(CreateView):
    template_name = 'stock/item_form.html'
    form_class = ItemForm
    success_url = reverse_lazy('stock:add_item')

    def form_valid(self, form):
        form.cleaned_data
        messages.success(self.request, 'Item added successfully')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Item not added')
        return super().form_invalid(form)
    

@login_required()
def create_item(request):
    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Item added successfully')
                return render(request, 'stock/item_form.html', {'form': form})
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


            messages.success(request, "{} updated in purchase list".format(purchase))

            return render(request, 'stock/purchase_form.html', {'form': form})

            # else:
            #    st = Stock.objects.create(user=request.user, stock_item=purchase.item, quantity=purchase.quantity)
            #    st.save()

            #     # Update the stock quantity by the quantity of the new purchase
            #    item_in_stock = Stock.objects.get(user=request.user, stock_item=purchase.item)
            #    if item_in_stock:
            #         item_in_stock.quantity = purchase.quantity
            #         item_in_stock.save()


            #     # Record the transaction
            #    transaction = Transaction.objects.create(item=purchase.item, transaction_type=Transaction.PURCHASE, quantity=purchase.quantity, reference_id=purchase.id, reference_model=purchase.__class__.__name__, notes="Item purchased" ,manager=request.user)

            #    transaction.save()

            #    messages.success(request, "{} is recorded in purchase  and updated in stock".format(purchase))
            #    return render(request, 'stock/purchase_form.html', {'form': form})

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


# @login_required()
# def create_issue_view(request):
#     """
#     Function to issue a kit from the stock to the student.
#     """
#     # Check if the requested item and quantity exist in the stock.
#     if request.method == "POST":
#         form = IssueForm(request.POST)

#         if form.is_valid():
#             print("valid")
#             obj = form.save(commit=False)
#             form.instance.user = request.user
#             enrollement = form.cleaned_data['enrollement']
#             student = Student.objects.get(enrollement=enrollement) 

#             print("found student", student)

#             if student:
#                 #  obj.save()
#                 pass
#             else:
#                 messages.error(request, 'Student not found')
#                 return render(request, 'stock/issue_form.html', {'form': form})


#             # Check if the requested item and quantity exist in the stock
#             for item in obj.items.all():

#                 # Check if the requested item and quantity exist in the stock
#                 stock = Stock.objects.get(user=request.user, stock_item=item)

#                 if stock and stock.quantity <p int(obj.quantity):
#                     messages.error(request, '{} - Out of stock'.format(item))
#                     obj.delete()
#                     return render(request, 'stock/issue_form.html', {'form': form})


#                 # Issue the kit otherwise
#                 # Record the transaction
#                 transaction = Transaction.objects.create(item=item, transaction_type=Transaction.ISSUE, quantity=obj.quantity, reference_id=obj.pk, reference_model=obj.__class__.__name__, manager=request.user, notes="Item issued")
#                 transaction.save()

#                 # Update the stock
#                 update_stock_quantity(request, item, -int(obj.quantity))

              

#                 messages.success(request, 'Kit issued successfully')
#                 return render(request, 'stock/issue_form.html', {'form': form})
        
#     form = IssueForm() 

#     return render(request, 'stock/issue_form.html', {'form': form}) 



@login_required()
def issue_kit(request):
    if request.method == 'POST':
        form = IssueForm(request.POST)

        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user

            # check if there exists a issuance with this enrollement

            issuance_exist = Issue.objects.filter(enrollement=obj.enrollement).first()

            if issuance_exist:
                selected_items = request.POST.getlist('items', None)

                for item in selected_items:
                    stock = update_stock_quantity(request, item, -1)

                    if stock.quantity > 0:
                        issuance_exist.items.add(item)
                        issuance_exist.save()
                    else:
                        messages.error(request, '{} - Out of stock'.format(item))
                        obj.delete()
                        return render(request, 'stock/tables/issue_list.html', {'form': form})

                    if stock.quantity == 0:
                        stock.delete()
                        stock.save()
                    tr_item = Item.objects.get(pk=int(item))

                    transaction = Transaction.objects.create(item=tr_item, transaction_type=Transaction.ISSUE, quantity=issuance_exist.quantity, reference_id=issuance_exist.pk, reference_model=obj.__class__.__name__, manager=request.user, notes="Item issued")
                    transaction.save()


                messages.success(request, 'Updating kits')
                return render(request, 'stock/tables/issue_list.html', {'form': form})
            else:
                obj.save()
                form.save_m2m()


                for item in obj.items.all():
                    stock = update_stock_quantity(request, item, -1)
                    transaction = Transaction.objects.create(item=item, transaction_type=Transaction.ISSUE, quantity=obj.quantity, reference_id=obj.pk, reference_model=obj.__class__.__name__, manager=request.user, notes="Item issued")
                    transaction.save()

                messages.success(request, 'Issuing kits')
                return render(request, 'stock/tables/issue_list.html', {'form': form})

        else:
            messages.error(request, 'Form is not valid')
            return render(request, 'stock/issue_form.html', {'form': form})


    # find issued kit with the enrollement no and modify the selection
    print('enrollement form search', request.GET.get('enrollement'))
    issued_kit = Issue.objects.filter(enrollement=request.GET.get('enrollement')).first()
    items = Item.objects.all()

    if issued_kit is not None:
        given_items = issued_kit.items.all()

        for i in given_items:
            if i in items:
                items = items.exclude(pk=int(i.pk))
    
    form = IssueForm()
    form.fields['items'].queryset = items
    form.fields['enrollement'].initial = int(request.GET.get('enrollement'))
    form.fields['enrollement'].widget.attrs['readonly'] = True
    return render(request, 'stock/issue_form.html', {'form': form})




class PurchaseListView(LoginRequiredMixin,ListView, FormView):
    model = Purchase
    template_name = 'stock/tables/purchase_list.html'
    context_object_name = 'purchases'
    paginate_by = 5
    ordering = ['-created_at']
    form_class = DownloadForm

    def post(self, request, *args, **kwargs):
        responce = download_purchases(self, request)

        return responce



class PurchaseDetailView(LoginRequiredMixin, DetailView):
    model = Purchase
    template_name = 'stock/purchase_detail.html'

class StockListView(LoginRequiredMixin, ListView, FormView):
    model = Stock
    template_name = 'stock/tables/stock_list.html'
    context_object_name = 'stocks'
    form_class = DownloadForm
    paginate_by = 5

    def post(self, request, *args, **kwargs):
        responce = download_stock(self, request)

        return responce



class StockDetailView(LoginRequiredMixin, DetailView):
    model = Stock
    template_name = 'stock/stock_detail.html'


class TransactionListView(LoginRequiredMixin, ListView, FormView):
    model = Transaction
    template_name = 'stock/tables/transaction_list.html'
    context_object_name = 'transactions'
    paginate_by = 5
    form_class = DownloadForm

    def post(self, request, *args, **kwargs):
        responce = download_transactions(self, request)

        return responce


class IssueListView(LoginRequiredMixin, ListView, FormView):
    model = Issue
    template_name = 'stock/tables/issue_list.html'
    context_object_name = 'kits'
    paginate_by = 5
    form_class = DownloadForm

    def post(self, request, *args, **kwargs):
        responce = download_kits(self, request)

        return responce
    

def purchase_item(request):
    if request.method == 'POST':
        form = PurchaseForm(request.POST)

        if form.is_valid():
            purchase = form.save(commit=False)
            purchase.user = request.user
            purchase.save()
        

        # Update the purchase to the stock
        update_stock_quantity(request, purchase.item, purchase.quantity)
        messages.success(request, '{} is updated in the stock'.format(purchase.item.__str__().upper()))
        return render(request, 'stock/tables/purchase_list.html', {'form': form})
    form = PurchaseForm()




def search_issued_items(request):
    kitlist= []
    if request.method == 'POST':
        
        enrollement = request.POST.get('enrollement')
        kits = Issue.objects.filter(enrollement=enrollement).first()
        if enrollement == '' or kits is None:
            return render(request, 'partials/search_button.html', {'kitlist': kitlist})
            # return HttpResponse("<p class='text-warning'>Please enter valid enrollement number</p><button type='button'>Search</button>")
        else:
            items = kits.items.all()

            for i in items:
                kitlist.append(i)
        return render(request, 'partials/return_list.html', {'kitlist': kitlist, 'enrollement': enrollement})
  

    return render(request, 'stock/return_form.html')


def return_kit(request):
    if request.method == 'POST':
        enrollement = request.POST.get('enrollement')
        issued_kit = Issue.objects.filter(enrollement=enrollement).first()

        for item in request.POST.getlist('items[]'):
            item = Item.objects.get(pk=int(item))
            issued_kit.items.remove(item)
            update_stock_quantity(request, item, issued_kit.quantity)
            issued_kit.save()

            tr = Transaction.objects.create(
                item=item,
                transaction_type=Transaction.RETURN,
                quantity=issued_kit.quantity,
                manager=request.user
            )

            tr.save()

            if issued_kit.items.count() == 0:
                issued_kit.delete()

        messages.success(request, 'Kit with enrolement no. {} is returned'.format(issued_kit.enrollement))
        
       

    return render(request, 'stock/success.html')


def search_student(request):
    # find issued kit with enrollement number
    enrollement = request.GET.get('enrollement')
    print(enrollement)
    print('gett gerjejfd')
    student = None
    url = reverse('stock:issue_kit')

    try:
        student = Student.objects.filter(enrollement=enrollement).first()
        if student:
            issued_kit = Issue.objects.filter(enrollement=enrollement).first()
            items = Item.objects.all()

            if issued_kit is None:
                return HttpResponse(f"<p class='text-success'>One student found with following detailes:</p><p>Name: {student.name}</p><p>Batch: {student.batch}</p><p>Roll Number: {student.roll}</p><button type='submit' class='btn btn-primary mt-3'><a class='text-white link-underline link-underline-opacity-0' href='{url}?enrollement={student.enrollement}'>Issue Kit</button>")

            else:

                # if set(issued_kit.items.all()) == set(items) :
                #     return HttpResponse(f"<p class='text-danger'>This kit is already issued</p>")

                if issued_kit.items.count() == 4:
                    return HttpResponse(f"<p class='text-danger'>This kit is already issued</p>")

                if issued_kit:
                    return HttpResponse(f"<p class='text-success'>One student found with following detailes:</p><p>Name: {student.name}</p><p>Batch: {student.batch}</p><p>Roll Number: {student.roll}</p><p>Issue Date: {issued_kit.get_issued_date()}</p><p>Issued Items: {issued_kit.get_items()}</p><button type='submit' class='btn btn-primary mt-3'><a class='text-white link-underline link-underline-opacity-0' href='{url}?enrollement={issued_kit.enrollement}'>Issue more</button>")
                else:
                    return HttpResponse(f"<p class='text-success'>Issue a kit to this student</p><button type='submit' class='btn btn-primary mt-3'><a class='text-white link-underline link-underline-opacity-0' href='{url}?enrollement={enrollement}'>Issue kit</button>")


    except Issue.DoesNotExist:
        pass
    
    return HttpResponse("<p class='text-danger'>No student found</p>")



