from django import template
from django.core.paginator import Paginator


register = template.Library()

@register.inclusion_tag(filename='stock/tags/pagination.html')
def show_pagination(page_obj):
    # paginator = Paginator(obj_list, 5)
    # page_number = request.GET.get('page')
    # page_obj = paginator.get_page(page_number)
    return {'page_obj': page_obj}