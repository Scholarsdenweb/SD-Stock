from django.urls import path
from . import views
from .forms import (ItemForm, CategoryForm, VariantForm
)
app_name = 'stock'

urlpatterns = [

    # path('list/', views.StockListView.as_view(), name='stock_list'),

    path('', views.StockCreate.as_view(), name='create_stock'),
    # path('create-serial/<int:pk>/', views.CreateSerialNumber.as_view(), name='create_serial'),
    path('item-detail/<int:pk>/', views.ItemDetailView.as_view(), name='item_detail'),
    path('category-product/', views.load_product_by_category, name='category_product'),
    path('item-variant/', views.load_variant_by_item, name='item_variant'),
    path('item/update/<int:pk>/', views.ItemUpdateView.as_view(), name = 'update_item'),
    path('transaction-list/', views.StockTransactionList.as_view(), name='transaction_list'),
    # path('purchase/add/', views.create_purchase_view, name='purchase'),
    # path('stock/add/', views.create_stock_view, name='add_stock'),
    path('stock/add-success', views.add_success_view, name='add_success'),
    # path('issue/add/', views.issue_kit, name='issue_kit'),
    


    # path('purchase/list/', views.PurchaseListView.as_view(), name='purchase_list'),
    path('purchase/<int:pk>/', views.PurchaseDetailView.as_view(), name='purchase_detail'),
    # path('purchase/update/<int:pk>', views.PurchaseUpdateView.as_view(), name = 'update_purchase'),

    # path('stock/<int:pk>/', views.StockDetailView.as_view(), name='stock_detail'),

    # path('transaction/list/', views.TransactionListView.as_view(), name='transaction_list'),
    # path('transaction/detail/<int:pk>', views.transaction_detail, name='transaction_detail'),

    path('issue/list/', views.IssueListView.as_view(), name='kit_list'),
    path('issue/list/<int:pk>/', views.IssueDetailView.as_view(), name='kit_detail'),

    # path('search/student/', views.search_student, name='search_student'),

    # path('search/issued-items/', views.search_issued_items, name='search_kit'),

    # path('return/kit/', views.return_kit, name='return_kit'),
    
    path('find/student/', views.filter_student, name='filter_student'),
    
    path('student/list/', views.StudentListView.as_view(), name='student_list'),
    
    ## Download sample excle file student registration
    path('download/sample/', views.sample_excel, name='sample_excel'),
    
    
    path('issue-new-kit/', views.issue_new_kit, name='issue_new_kit'),
    
    path('exchange-kit/', views.exchage_kit, name='exchange_kit'),

    

]



vendor_urlpatterns = [
    path('vendor/list/', views.VendorsCreateView.as_view(), name='vendor_list'),
]

edit_urlpatterns = [
    path('<int:pk>/edit/', views.edit_stock, name='edit_stock'),
    path('stock-detail/<int:pk>/', views.stock_detail, name='stock_detail'),
    path('serial-detail/<int:pk>/', views.serial_detail, name='serial_detail'),
    path('edit-serial/<int:pk>/', views.edit_serial, name='edit_serial'),
    path('<int:pk>/', views.edit_stock_with_serials, name='edit_stock_with_serials'),
    path('update-serial-number/<int:pk>/', views.UpdateSerialNumber.as_view(), name='update_serial_number'),
    path('update-stock/<int:pk>/', views.UpdateStock.as_view(), name='update_stock'),
]

htmx_urlpatterns = [
    path('check-serializable/', views.check_serializable_view, name='check_serializable'),
    path('add-serial/', views.add_serial_view, name='add_serial'),
    path('remove-input/', views.remove_input_view, name='remove_input'),
]


urlpatterns += htmx_urlpatterns
urlpatterns += edit_urlpatterns
urlpatterns += vendor_urlpatterns
