from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import RegexValidator
import random

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
    phone = models.CharField(max_length=15, default='79222222555', validators=[RegexValidator(r'^(\+\d{2})?\d{10}', message="Please enter the valid mobile number. Example +919999998888 or 7925666666")])
    
    
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




class OTPCode(models.Model):
    user = models.ForeignKey(StockUser, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    
    class Meta:
        verbose_name_plural = 'OTPs'
    
    def __str__(self):
        return self.otp
    
    
    def save(self, *args, **kwargs):
        number_list =list(range(10)) # [0,1,2,3,4,5,6,7,8]
        code = []
        
        for i in range(6):
            num = random.choice(number_list)
            code.append(num)
        
        
        code_string = "".join(str(c) for c in code)
        self.otp = code_string
        super().save(*args, **kwargs)