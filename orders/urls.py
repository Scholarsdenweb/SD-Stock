from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.main, name="main"),
    path('order-list/', views.OrdersCreateView.as_view(), name="order_list"),
    path('purchase/list/', views.CreatePurchase.as_view(), name='purchase_list'),
    path('load-variant/', views.load_variant_by_item, name='load_variant'),

    path('invoice-list/', views.CreateInvoice.as_view(), name="invoice_list"),
    path('page-3/', views.page_three, name="page_three"),
    
]
