from django.urls import path
from . import views

app_name = 'allocate'

urlpatterns = [
    path('', views.main_page, name='main'),
    path('list/', views.AllocationView.as_view(), name='allocation_list'),
    path('return/', views.ReturnView.as_view(), name='return_list'),
    path('load-variant/', views.load_variant, name='load_variant'),
    path('update-allocation/<int:pk>/', views.UpdateAllocationView.as_view(), name='update_allocation'), 
    path('return-item/', views.return_item, name='return_item'), 
    path('delete-allocation/', views.delete_allocation, name='delete_allocation'),
    path('products/', views.product_view, name='product_view'),  
    path('products/<int:pk>/', views.product_detail_view, name='product_detail'),
    path('add-item/', views.add_to_allocation_item, name='add_item'),  
    path('cart-items/', views.allocation_cart, name='allocation_cart'),
    path('allocate-items/', views.allocate_items, name="allocate_items"),
    path('allocation-detail/<int:pk>/', views.allocation_detail, name="allocation_detail"),
]