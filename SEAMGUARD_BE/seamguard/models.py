from django.db import models
import uuid
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

# Define industries as a tuple for choices
INDUSTRY_CHOICES = [
    ('Glass', 'Glass'),
    ('Iron & Steel', 'Iron & Steel'),
    ('FMCG', 'FMCG'),
    ('IT Hardware', 'IT Hardware'),
    ('Automobiles', 'Automobiles'),
    ('Apparels', 'Apparels'),
    ('Textiles', 'Textiles'),
    ('Furnitures', 'Furnitures'),
    ('Leather', 'Leather'),
    ('Fabricated Metals', 'Fabricated Metals'),
    ('CAD', 'CAD'),
]

class UserManager(BaseUserManager):
    def create_user(self, emp_id, email, password=None, **extra_fields):
        if not emp_id:
            raise ValueError('The Employee ID must be set')
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        user = self.model(emp_id=emp_id, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_admin(self, emp_id, email, password=None, **extra_fields):
        extra_fields.setdefault('is_admin', True)
        extra_fields.setdefault('is_staff', True)
        return self.create_user(emp_id, email, password, **extra_fields)

class User(AbstractBaseUser):
    emp_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    line_number = models.CharField(max_length=50, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    industry = models.CharField(max_length=50, choices=INDUSTRY_CHOICES, blank=True, null=True)  # New field
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'emp_id'
    REQUIRED_FIELDS = ['email', 'name']

    def __str__(self):
        return self.emp_id

class EmployeeMaster(models.Model):
    emp_id = models.CharField(max_length=20)
    name = models.CharField(max_length=100)
    line_number = models.CharField(max_length=20)
    department = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=15, unique=True)
    email = models.EmailField(unique=True)
    industry = models.CharField(max_length=50, choices=INDUSTRY_CHOICES, blank=True, null=True)  # New field

    def __str__(self):
        return f"{self.emp_id} - {self.name}"

class Dashboard(models.Model):
    emp_id = models.CharField(max_length=100)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    line_number = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    password = models.CharField(max_length=255)
    industry = models.CharField(max_length=50, choices=INDUSTRY_CHOICES, blank=True, null=True)  # New field
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.emp_id

class DashboardImage(models.Model):
    dashboard_user = models.ForeignKey(Dashboard, on_delete=models.CASCADE)
    emp_id = models.CharField(max_length=50)
    image = models.ImageField(upload_to='dashboard_images/')
    industry = models.CharField(max_length=50, choices=INDUSTRY_CHOICES, blank=True, null=True)  # New field

class Annotation(models.Model):
    user = models.ForeignKey(Dashboard, on_delete=models.CASCADE)
    image = models.ForeignKey(DashboardImage, on_delete=models.CASCADE)
    class_name = models.CharField(max_length=100)
    x_min = models.FloatField()
    y_min = models.FloatField()
    x_max = models.FloatField()
    y_max = models.FloatField()
    industry = models.CharField(max_length=50, choices=INDUSTRY_CHOICES, blank=True, null=True)  # New field

class DetectionResult(models.Model):
    dashboard_user = models.ForeignKey('Dashboard', on_delete=models.CASCADE)
    emp_id = models.CharField(max_length=50, default='UNKNOWN')
    image_id = models.ForeignKey('DashboardImage', on_delete=models.CASCADE)
    defect_result = models.JSONField(default=dict)
    created_at = models.DateTimeField(default=timezone.now)
    batch_id = models.CharField(max_length=36, default=uuid.uuid4, db_index=True)
    source = models.CharField(max_length=10, choices=[('image', 'Image'), ('video', 'Video'), ('live', 'Live')], default='image')
    industry = models.CharField(max_length=50, choices=INDUSTRY_CHOICES, blank=True, null=True)  # New field

class LoginHistory(models.Model):
    user = models.ForeignKey(Dashboard, on_delete=models.CASCADE)
    login_time = models.DateTimeField(auto_now_add=True)