from django.shortcuts import get_object_or_404, render
from stock.models import Variant, Item, Location
from django.db.models import Q
from stock.models import Allocations, Returns
from authapp.models import User
from authapp.models import Employee, Student
from django.contrib.contenttypes.models import ContentType

def find_allocation_or_returns(search_text, *args, search_model=None, **kwargs):
    if search_model is None:
        return Allocations.objects.none()

    search_dict = {"ids": [], "model": None}

    if search_text:
        # STUDENT (No relation with User)
        students = Student.objects.filter(
            Q(name__icontains=search_text) |
            Q(enrollement__iexact=search_text)
        ).values_list('id', flat=True)

        # EMPLOYEE (Has relation with User)
        employees = Employee.objects.filter(
            Q(user__full_name__icontains=search_text) |
            Q(emp_id__iexact=search_text)
        ).values_list('id', flat=True)

        # LOCATION
        locations = Location.objects.filter(
            Q(name__icontains=search_text)
        ).values_list('id', flat=True)

        # Priority: Student → Employee → Location
        if students:
            search_dict["ids"] = students
            search_dict["model"] = ContentType.objects.get_for_model(Student)

        elif employees:
            search_dict["ids"] = employees
            search_dict["model"] = ContentType.objects.get_for_model(Employee)

        elif locations:
            search_dict["ids"] = locations
            search_dict["model"] = ContentType.objects.get_for_model(Location)

    # If nothing matched → return everything
    if not search_dict["ids"]:
        return search_model.objects.all()

    if search_model is Allocations:
        return search_model.objects.filter(
            allocated_to__in=search_dict["ids"],
            contenttype=search_dict["model"]
        )

    if search_model is Returns:

        # Student matched → Students cannot return items → return none
        if search_dict["model"] == ContentType.objects.get_for_model(Student):
            return search_model.objects.none()

        # Location matched → irrelevant for Returns
        if search_dict["model"] == ContentType.objects.get_for_model(Location):
            return search_model.objects.none()

        # Employee matched → employee → user → returned_by
        if search_dict["model"] == ContentType.objects.get_for_model(Employee):
            # Get Users whose Employee.id is matched
            print('employee')
            user_ids = User.objects.filter(
                employee__id__in=search_dict["ids"]
            ).values_list("id", flat=True)
            
            print('user_ids', user_ids)
            print('search_model', search_model)

            return search_model.objects.filter(returned_by__in=user_ids)


    return search_model.objects.all()

    
    
    

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
    
