from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, AbstractUser
from django.core.validators import RegexValidator
import random
from datetime import datetime

current_year = datetime.now().year
previous_five_years = [year for year in range(current_year - 5, current_year)] + [current_year]
previous_five_years = sorted(previous_five_years, reverse=True)



# Create your models here.
class UserManager(BaseUserManager):
    """Custom manager for User model with email as the unique identifier."""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields) 
 
class Roles(models.Model):
    MANAGER = 1
    EMPLOYEE = 2
    FACULTY = 3
    
    ROLE_CHOICES = [
        (MANAGER, 'Manager'),
        (EMPLOYEE, 'Employee'),
        (FACULTY, 'Faculty'),
    ]
    
    id = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, primary_key=True)
    
    class Meta:
        verbose_name = 'Role'
        verbose_name_plural = 'Roles'
    
    def __str__(self):
        return self.get_id_display()
    
    
    

class User(AbstractBaseUser, PermissionsMixin):
    role = models.ManyToManyField("Roles")
    full_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []  

    objects = UserManager()

    def __str__(self):
        return self.email    
    
    
class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    emp_id = models.CharField(max_length=10, unique=True, verbose_name='Employee ID', validators=[RegexValidator(r'^\d+$')])
    phone = models.CharField(
        max_length=15,
        blank=True,
        validators=[RegexValidator(
            r"^(\+\d{2})?\d{10}$",
            message="Please enter a valid mobile number. Example +919999998888 or 7925666666"
        )]
    )

    department = models.CharField(max_length=100)
    designation = models.CharField(max_length=100)
    
    def __str__(self):
        return self.user.full_name
    
    
    
class Student(models.Model):
    YEAR_CHOICES = [(str(year), str(year)) for year in previous_five_years]
    
    name = models.CharField(max_length=100)
    enrollement = models.CharField(max_length=15, unique=True, null=True, blank=True)
    program = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, blank=True, validators=[RegexValidator(r'^(\+?\d{2})?\d{10}$', message="Please enter a valid mobile number. Example +919999998888 or 7925666666")])
    admission_year = models.CharField(max_length=4, choices=YEAR_CHOICES)
    
    def __str__(self):
        return self.name
    




# class OTPCode(models.Model):
#     user = models.ForeignKey(StockUser, on_delete=models.CASCADE)
#     otp = models.CharField(max_length=6)
    
#     class Meta:
#         verbose_name_plural = 'OTPs'
    
#     def __str__(self):
#         return self.otp
    
    
#     def save(self, *args, **kwargs):
#         number_list =list(range(10)) # [0,1,2,3,4,5,6,7,8]
#         code = []
        
#         for i in range(6):
#             num = random.choice(number_list)
#             code.append(num)
        
        
#         code_string = "".join(str(c) for c in code)
#         self.otp = code_string
#         super().save(*args, **kwargs)