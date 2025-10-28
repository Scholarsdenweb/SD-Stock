from django.shortcuts import get_object_or_404, render
from stock.models import Variant, Item, Location
from django.db.models import Q
from stock.models import Allocations
from authapp.models import Employee, Student
from django.contrib.contenttypes.models import ContentType

def find_allocation(search_text, *arge, **kwargs):
    search_dict = dict(ids=[], model=None)
    if search_text:
        
        students = Student.objects.filter(Q(name__icontains=search_text) | Q(enrollement__iexact=search_text)).values_list('id', flat=True) 
        
        employees = Employee.objects.filter(Q(user__full_name__icontains=search_text) | Q(emp_id__iexact=search_text)).values_list('id', flat=True)
        
        locations = Location.objects.filter(Q(name__icontains=search_text)).values_list('id', flat=True)
        
        if students:
            search_dict['ids'] = students
            search_dict['model'] = ContentType.objects.get_for_model(Student)
        elif employees:
            search_dict['ids'] = employees
            search_dict['model'] = ContentType.objects.get_for_model(Employee)
        elif locations:
            search_dict['ids'] = locations
            search_dict['model'] = ContentType.objects.get_for_model(Location)
    
    return Allocations.objects.filter(allocated_to__in=search_dict['ids'], contenttype=search_dict['model']) or Allocations.objects.all()
    
    
    

def load_variant_by_item(request, f, template):
    response = None
    
    if request.headers.get('hx-request'):
        item_id = request.GET.get('item')
        item = get_object_or_404(Item, id=int(item_id))
        variants = Variant.objects.filter(product=item)
        form = f()
        form.fields['variant'].queryset = variants
        response =  render(request, template, {'form': form})
        response['HX-Target'] = '#productoptions'
        response = response
    return response


def load_recipient(request, f, template):
    pass
    
