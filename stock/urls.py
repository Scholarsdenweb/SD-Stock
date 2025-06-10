from django.urls import path
from . import views

app_name = 'stock'

urlpatterns = [

    # path('list/', views.StockListView.as_view(), name='stock_list'),


    path('item/add/', views.create_item, name='add_item'),
    path('item/update/<int:pk>', views.ItemUpdateView.as_view(), name = 'update_item'),
    path('purchase/add/', views.create_purchase_view, name='purchase'),
    path('stock/add/', views.create_stock_view, name='add_stock'),
    path('stock/add-success', views.add_success_view, name='add_success'),
    path('issue/add/', views.issue_kit, name='issue_kit'),


    path('purchase/list/', views.PurchaseListView.as_view(), name='purchase_list'),
    path('purchase/<int:pk>/', views.PurchaseDetailView.as_view(), name='purchase_detail'),
    path('purchase/update/<int:pk>', views.PurchaseUpdateView.as_view(), name = 'update_purchase'),

    path('stock/<int:pk>/', views.StockDetailView.as_view(), name='stock_detail'),

    path('transaction/list/', views.TransactionListView.as_view(), name='transaction_list'),
    path('transaction/detail/<int:pk>', views.transaction_detail, name='transaction_detail'),

    path('issue/list/', views.IssueListView.as_view(), name='kit_list'),

    # path('search/student/', views.search_student, name='search_student'),

    path('search/issued-items/', views.search_issued_items, name='search_kit'),

    path('return/kit/', views.return_kit, name='return_kit'),
    
    path('find/student/', views.filter_student, name='filter_student'),
    
    path('student/list/', views.StudentListView.as_view(), name='student_list'),
    
    ## Download sample excle file student registration
    path('download/sample/', views.sample_excel, name='sample_excel'),
    

]

