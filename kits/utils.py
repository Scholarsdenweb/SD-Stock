from .models import KitAllocation
from django.db.models import Q


def find_allocation(search_text, *arge, **kwargs):
    queryset = KitAllocation.objects.filter(
        Q(student__name__icontains=search_text) |
        Q(student__enrollement__iexact=search_text) |
        Q(student__admission_year=search_text)|
        Q(kit__type__iexact=search_text)
    )
    
    if not queryset.exists():
        queryset = KitAllocation.objects.none()
    return queryset
