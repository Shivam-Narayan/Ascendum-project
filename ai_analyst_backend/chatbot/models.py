from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from datetime import datetime, timedelta
from django.utils.timezone import now
import uuid



class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    full_name = models.CharField(max_length=30)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(
        default=(datetime.utcnow() + timedelta(hours=5, minutes=30))
    )
    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    def __str__(self):
        return self.email
    
class DocumentGroup(models.Model):
    documents_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=now)


    def __str__(self):
        return str(self.documents_id)


class UploadedFile(models.Model):
    FILE_TYPE_CHOICES = [
        ('PDF', 'PDF'),
        ('EXCEL', 'EXCEL'),
        ('WORD', 'WORD'),
        # add more as needed
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file_id = models.CharField(max_length=100, unique=True)  # could be pdf_id, dataset_id, etc
    file_type = models.CharField(max_length=20, choices=FILE_TYPE_CHOICES)
    file_path = models.CharField(max_length=500)     # Path on server
    filename = models.CharField(max_length=255)
    metadata = models.JSONField(blank=True, null=True)  # optional: for pdf metadata, etc
    uploaded_at = models.DateTimeField(auto_now_add=True)
    document_group = models.ForeignKey(DocumentGroup, on_delete=models.CASCADE, related_name='files', null=True, blank=True)

    def __str__(self):
        return f"{self.user.email} - {self.filename} ({self.file_id})"
