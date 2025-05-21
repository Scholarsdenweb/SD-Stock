from import_export.formats.base_formats import XLSX
from tablib import Dataset
from stock.models import Student
from .admin import StudentResource


def import_and_create_student(file):
    # Read the uploaded file
    dataset = Dataset().load(file.read(), format='xlsx')
    
    student_resource = StudentResource()
    # Test the data import
    result = student_resource.import_data(dataset, dry_run=True)

    if not result.has_errors():
        # Apply the import if no errors found
        student_resource.import_data(dataset, dry_run=False)
        return {'success': True, 'created': len(dataset)}
    else:
        # Return errors for feedback
        return {'success': False, 'errors': result.row_errors()}