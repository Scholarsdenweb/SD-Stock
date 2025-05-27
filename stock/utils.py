from stock.models import Stock, Transaction, Issue
from django.http import HttpResponse, JsonResponse
from .admin import (StockResource, PurchaseResource, TransactionResouece,  KitResource)
from datetime import datetime
from django import forms
from django.contrib import messages

now = datetime.now()
timestamp = datetime.timestamp(now)

def update_stock_quantity(request, item, quantity):
    
    stock = Stock.objects.filter(stock_item=item).first()
    if stock:
        stock.quantity += quantity
        stock.save()
        return stock
    else:
        messages.error(request, '{} - Out of stock'.format(item))
        return None


def handle_issue_creation(user, issue_instance):
    for item in issue_instance.items.all():
        Transaction.objects.create(
            issue=issue_instance,
            item=item,
            transaction_type=Transaction.ISSUE,
            quantity=issue_instance.quantity,
            user=user
        )


def create_export_file(self, request, resource, filename):
        qs = self.get_queryset()
        resource =resource()
        dataset = resource.export(qs)
        format = request.POST.get('format')

        if format == 'csv':
           ds = dataset.csv
           content_type = 'text/csv'
        elif format == 'xlsx':
            ds = dataset.xlsx 
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        elif format == 'json':
            ds = dataset.json
            content_type = 'application/json'
        else:
            return JsonResponse({'Error':'Please select a valid format'})

        response = HttpResponse(ds, content_type={content_type})
        response['Content-Disposition'] = f'attachment; filename={filename}-{now}.{format}'

        return response

def download_stock(self, request):
        response =create_export_file(self,request, StockResource, 'stock-list')
        return response



def download_purchases(self, request):

        response =create_export_file(self,request, PurchaseResource, 'purchases-list')
        return response


def download_transactions(self, request):

        response =create_export_file(self,request, TransactionResouece, 'transactions-list')
        return response

def download_kits(self, request):

        response =create_export_file(self,request, KitResource, 'kits-list')
        return response



def delete_issued_kit(request,issued_kit):
        for kit in issued_kit:
            kit = Issue.objects.get(pk=int(kit['id']))
            
            # kit.delete()
            # for item in kit.items.all():
            #       tr = Transaction.objects.create(
            #           item=item,
            #           transaction_type=Transaction.RETURN,
            #           quantity=kit.quantity,
            #           user=request.user
            #       )

            #       tr.save()


            # kit.delete()

        
        return JsonResponse({'kits': issued_kit})
        

def get_issued_items(enrollement=None):
    issued_kit = Issue.objects.filter(enrollement=enrollement)
    issued_items = []
    if issued_kit:
        for item in issued_kit:
            for i in item.items.all():
                issued_items.append(i)
    return issued_items