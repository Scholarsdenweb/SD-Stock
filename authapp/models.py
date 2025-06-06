from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import RegexValidator


# Create your models here.
class StockUserManager(BaseUserManager):
    
    def create_user(self, emp_id, password=None, **extra_fields):
        if not emp_id:
            raise ValueError('The employee ID must be set.')
        user = self.model(emp_id=emp_id, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, emp_id, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(emp_id, password, **extra_fields)

class StockUser(AbstractBaseUser, PermissionsMixin):
    emp_id = models.CharField(max_length=10, unique=True, verbose_name='Employee ID', validators=[RegexValidator(r'^\d+$')])
    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = StockUserManager()

    USERNAME_FIELD = 'emp_id'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return f"{self.emp_id} - {self.name}"
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
