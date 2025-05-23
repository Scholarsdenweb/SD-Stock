from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import StockUser
from .utils import import_and_create_student