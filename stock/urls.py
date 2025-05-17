from django.urls import path
from . import views

app_name = 'stock'

urlpatterns = [

    # path('list/', views.StockListView.as_view(), name='stock_list'),


    path('item/add/', views.create_item, name='add_item'),
    path('purchase/add/', views.create_purchase_view, name='purchase'),
    path('stock/add/', views.create_stock_view, name='add_stock'),
    path('issue/add/', views.issue_kit, name='issue_kit'),


    path('purchase/list/', views.PurchaseListView.as_view(), name='purchase_list'),
    path('purchase/<int:pk>/', views.PurchaseDetailView.as_view(), name='purchase_detail'),

    path('stock/<int:pk>/', views.StockDetailView.as_view(), name='stock_detail'),

    path('transaction/list/', views.TransactionListView.as_view(), name='transaction_list'),

    path('issue/list/', views.IssueListView.as_view(), name='kit_list'),


]