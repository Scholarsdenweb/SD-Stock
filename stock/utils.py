from stock.models import Issue
from django.http import HttpResponse, JsonResponse
from .admin import (StockResource)
# from .admin import ( KitResource)
from datetime import datetime
from django import forms
from django.contrib import messages
from stock.models import Student, Stock, Purchase
from django.db.models import Q, F

now = datetime.now()
timestamp = datetime.timestamp(now)




def search_stock(search_text):
    
    text = str(search_text).strip().lower()
    
    return Stock.objects.filter(
        Q(variant__name__icontains=text) | 
        Q(variant__product__name__icontains=text)
    )
    
    
def search_purchase(search_text):
    
    text = str(search_text).strip().lower()
    
    return Purchase.objects.filter(
        Q(item__name__icontains=text) | 
        Q(supplier__icontains=text)
    )

def update_stock_quantity(request, item_id, quantity):
    Stock.objects.filter(variant=item_id).update(quantity=F('quantity') + quantity)

# def handle_issue_creation(user, issue_instance):
#     for item in issue_instance.items.all():
#         Transaction.objects.create(
#             issue=issue_instance,
#             item=item,
#             transaction_type=Transaction.ISSUE,
#             quantity=issue_instance.quantity,
#             user=user
#         )


# def create_export_file(self, request, resource, filename):
#         qs = self.get_queryset()
#         resource =resource()
#         dataset = resource.export(qs)
#         format = request.POST.get('format')

#         if format == 'csv':
#            ds = dataset.csv
#            content_type = 'text/csv'
#         elif format == 'xlsx':
#             ds = dataset.xlsx 
#             content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
#         elif format == 'json':
#             ds = dataset.json
#             content_type = 'application/json'
#         else:
#             return JsonResponse({'Error':'Please select a valid format'})

#         response = HttpResponse(ds, content_type={content_type})
#         response['Content-Disposition'] = f'attachment; filename={filename}-{now}.{format}'

#         return response

# def download_stock(self, request):
#         response =create_export_file(self,request, StockResource, 'stock-list')
#         return response



# def download_purchases(self, request):

#         response =create_export_file(self,request, PurchaseResource, 'purchases-list')
#         return response


# def download_transactions(self, request):

#         response =create_export_file(self,request, TransactionResouece, 'transactions-list')
#         return response

# def download_kits(self, request):

#         response =create_export_file(self,request, KitResource, 'kits-list')
#         return response



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


def find_student(full_name=None, dob=None, enrollement=None):
    
    filters = Q()

    if full_name:
        filters |= Q(name__iexact=str(full_name).strip())
    if dob:
        try:
            # Try parsing dob to ensure it's a valid date
            from datetime import datetime
            dob = datetime.strptime(dob, '%Y-%m-%d').date()
            filters |= Q(date_of_birth=dob)
        except ValueError:
            pass  # Ignore invalid date format
    if enrollement:
        filters |= Q(enrollement=str(enrollement).strip())

    if not filters:
        return None  # Nothing to filter by

    try:
        return Student.objects.get(filters)
    except Student.DoesNotExist:
        return None
    except Student.MultipleObjectsReturned:
        # Optional: handle multiple matches
        return None
    
    
# def calc_in_stock_items(item):
#     try:
#         stock = Stock.objects.get(stock_item=item)
#         return stock.in_stock()
#     except Stock.DoesNotExist:
#         return 0


def create_export_file(qs, resource):
    now = datetime.now()
    now = now.strftime("%d-%m-%Y %H:%M:%S")
    resource =resource()
    dataset = resource.export(qs)
    ds = dataset.xlsx
    content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    response = HttpResponse(ds, content_type={content_type})
    response['Content-Disposition'] = f'attachment; filename=stock-list-{now}.xlsx'

    return response


def download_stock_records(qs, resource=StockResource):
    return create_export_file(qs, resource)
