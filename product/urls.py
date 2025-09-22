from django.urls import path
from product.views import *

app_name = 'catelogue'


urlpatterns = [
    path('', CatelogueView.as_view(), name='catelogue'),
]