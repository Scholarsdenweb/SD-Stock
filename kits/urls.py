from django.urls import path
from . import views

app_name = 'kit'

urlpatterns = [
    path('', views.student_index, name='student_index'),
    path('add-item/', views.CreateItemView.as_view(), name='item_form'),
    path('create-kit/', views.kititem_view, name='create_kititems'),
    path('kititem-form/', views.get_kititem_form, name='kititem_form'),
    path('allocation/list/', views.allocation_list, name="allocate_list"),
    path('allocate-sale/', views.allocate_sale, name="allocate_sale"),
    path('allocate-save/<int:pk>/', views.KitAllocationDetailView.as_view(), name="allocate_save_detail"),
    path('alloccate/update/<int:pk>/', views.UpdateKitAllocation.as_view(), name="update_allocation"),
    path('update/kit/<int:kit_id>/', views.update_kit, name="update_kit"),
    path('delete/kititem/<int:pk>/', views.delete_kititem, name="delete_kititem"),
    path('delete/kit/<int:pk>/', views.delete_kit, name="delete_kit"),
]