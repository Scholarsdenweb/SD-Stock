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

    return render(request, 'stock/item_form.html', {'form': form})


@login_required()
def create_purchase_view(request):
    if request.method == 'POST':
        form = PurchaseForm(request.POST)
        if form.is_valid():
           purchase = form.save(commit=False)
           purchase.user = request.user

           purchase.save()

            # check if the item being purchased already exists in the purchase list
           existing_purchage = Purchase.objects.filter(item=purchase.item ).first()

           # Update the stock having this item
           item_in_stock = Stock.objects.get( stock_item=existing_purchage.item)
           item_in_stock.quantity += purchase.quantity
           item_in_stock.save()




           if existing_purchage:


                # Record the transaction
               transaction = Transaction.objects.create(item=purchase.item, transaction_type=Transaction.PURCHASE, quantity=purchase.quantity, reference_id=existing_purchage.pk, reference_model=purchase.__class__.__name__, notes="Item purchased" ,manager=request.user)


               messages.success(request, "{} updated in purchase list".format(existing_purchage))

               return render(request, 'stock/purchase_form.html', {'form': form})

           else:
               # If it is a new purchase
               purchase.save()

               st = Stock.objects.create(user=request.user, stock_item=purchase.item, quantity=purchase.quantity)
               st.save()

                # Update the stock quantity by the quantity of the new purchase
               item_in_stock = Stock.objects.get(user=request.user, stock_item=purchase.item)
               if item_in_stock:
                    item_in_stock.quantity = purchase.quantity
                    item_in_stock.save()


                # Record the transaction
               transaction = Transaction.objects.create(item=purchase.item, transaction_type=Transaction.PURCHASE, quantity=purchase.quantity, reference_id=purchase.id, reference_model=purchase.__class__.__name__, notes="Item purchased" ,manager=request.user)

               transaction.save()

               messages.success(request, "{} is recorded in purchase  and updated in stock".format(purchase))
               return render(request, 'stock/purchase_form.html', {'form': form})

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
def create_issue_view(request):
    """
    Function to issue a kit from the stock to the student.
    """
    # Check if the requested item and quantity exist in the stock.
    if request.method == "POST":
        form = IssueForm(request.POST)

        if form.is_valid():
            print("valid")
            obj = form.save(commit=False)
            form.instance.user = request.user
            enrollement = form.cleaned_data['enrollement']
            student = Student.objects.get(enrollement=enrollement) 

            print("found student", student)

            if student:
                #  obj.save()
                pass
            else:
                messages.error(request, 'Student not found')
                return render(request, 'stock/issue_form.html', {'form': form})


            # Check if the requested item and quantity exist in the stock
            for item in obj.items.all():

                # Check if the requested item and quantity exist in the stock
                stock = Stock.objects.get(user=request.user, stock_item=item)

                if stock and stock.quantity < int(obj.quantity):
                    messages.error(request, '{} - Out of stock'.format(item))
                    obj.delete()
                    return render(request, 'stock/issue_form.html', {'form': form})


                # Issue the kit otherwise
                # Record the transaction
                transaction = Transaction.objects.create(item=item, transaction_type=Transaction.ISSUE, quantity=obj.quantity, reference_id=obj.pk, reference_model=obj.__class__.__name__, manager=request.user, notes="Item issued")
                transaction.save()

                # Update the stock
                update_stock_quantity(request, item, -int(obj.quantity))

              

                messages.success(request, 'Kit issued successfully')
                return render(request, 'stock/issue_form.html', {'form': form})
        
    form = IssueForm() 

    return render(request, 'stock/issue_form.html', {'form': form}) 



@login_required()
def issue_kit(request):
    if request.method == 'POST':
        form = IssueForm(request.POST)

        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user


            student_exist = Student.objects.filter(enrollement=obj.enrollement).exists()

            if not student_exist:
                messages.error(request, 'Student not found')
                return render(request, 'stock/issue_form.html', {'form': form})
            else:
                obj.save()
                form.save_m2m()


            for item in obj.items.all():

                try:
                    stock = Stock.objects.get(stock_item__pk=id)
                    if stock.quantity > 0:
                        messages.success(request, f'{item.name} with size {item.size} issued successfully')

                        # Record the transaction
                        transaction = Transaction.objects.create(item=item, transaction_type=Transaction.ISSUE, quantity=obj.quantity, reference_id=obj.pk, reference_model=obj.__class__.__name__, manager=request.user, notes="Item issued")
                        transaction.save()

                        # Update the stock
                        update_stock_quantity(request, item, -int(obj.quantity))


                        # return render(request, 'stock/issue_form.html', {'form': form})
                except Stock.DoesNotExist:
                    messages.error(request, f"{item.name.upper()} is out of stock. Cannot issue.")
                    obj.delete()
                    return render(request, 'stock/issue_form.html', {'form': form})


    form = IssueForm()
    return render(request, 'stock/issue_form.html', {'form': form})




class PurchaseListView(LoginRequiredMixin,ListView, FormView):
    model = Purchase
    template_name = 'stock/tables/purchase_list.html'
    context_object_name = 'purchases'
    paginate_by = 5
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
    

