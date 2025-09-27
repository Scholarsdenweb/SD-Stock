from django.shortcuts import render, redirect
from django.views.generic.edit import CreateView
from stock.models import PurchaseOrder, Purchase
from .forms import OrderForm, PurchaseForm
from django.urls import reverse_lazy
from django.contrib import messages
from stock.utils import search_purchase
# Create your views here.


def main(request):
    return redirect('orders:order_list')
def page_one(request):
    return render(request, 'orders/page_one.html')

class OrdersCreateView(CreateView):
    model = PurchaseOrder
    form_class = OrderForm
    template_name = 'orders/order_list.html'
    context_object_name = 'orders'
    success_url = reverse_lazy('orders:order_list')
    
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        orders = PurchaseOrder.objects.all()
        context['orders'] = orders
        return context


def page_two(request):
    return render(request, 'orders/page_two.html')


def page_three(request):
    return render(request, 'orders/page_three.html')



class CreatePurchase(CreateView):
    model = Purchase
    template_name = 'orders/purchase_list.html'
    context_object_name = 'purchases'
    form_class = PurchaseForm
    success_url = reverse_lazy('orders:purchase_list')
    
    def get_context_data(self, **kwargs):
        vendors = Purchase.objects.all()
        context =  super().get_context_data(**kwargs)
        context['purchases'] = vendors
        return context
    
    def form_valid(self, form):
        purchase_obj = form.save(commit=False)
        purchase_obj.user = self.request.user
        purchase_obj.save()
        
        messages.success(self.request, 'Purchase record added successfully')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        response = super().form_invalid(form)
        messages.error(self.request, f'Purchase record not added. Try again.')
        return response
    
    
    def get(self, request, *args, **kwargs):
        self.object = None
        
        if request.headers.get('hx-request'):
            order = request.GET.get('order')
            item = request.GET.get('item')
            variant = request.GET.get('variant')
            quantity = request.GET.get('quantity')
            unit_price = request.GET.get('unit_price')
            
            total_amount = int(quantity) * int(unit_price)
            
            initial = {
                'order':order,
                'item':item,
                'variant':variant,
                'quantity':quantity,
                'unit_price':unit_price,
                'total_amount':total_amount
            }
            
            form = self.form_class(initial=initial)
            context = self.get_context_data(**kwargs)
            context['form'] = form
            return render(request, 'orders/purchase_list.html', context)
        search_text = request.GET.get('search', '')
        if search_text:
            purchases = search_purchase(search_text)
        else:
            purchases = Purchase.objects.all()
        context = self.get_context_data(**kwargs)
        form = self.form_class()
        context['form'] = form
        context['purchases'] = purchases
        return render(request, self.template_name, context)
