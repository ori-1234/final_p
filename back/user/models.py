from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.core.validators import RegexValidator

phone_regex = RegexValidator(
    regex=r'^\+?1?\d{9,15}$',
    message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
)

class User(AbstractUser):
    # id, username, email, password, first_name, last_name - already created using AbstractUser
    password = models.CharField(
        max_length=128,  # Maximum length of the password
        blank=False,  # Field is required
        validators=[
            RegexValidator(
                regex=r"^\S+$",  # Regex for valid passwords (no spaces allowed)
                message="Password cannot contain spaces.",
            )
        ],
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = 'users'

    def __str__(self):
        return self.username


class LoginHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField() # Stores browser and device info
    location = models.CharField(max_length=100, blank=True) # Stores the login location (can be determined via IP)
    status = models.BooleanField(default=True)  # Success or failure
    timestamp = models.DateTimeField(auto_now_add=True) 


class Note(models.Model):
    desc = models.CharField(max_length=300)
    owner = models.ForeignKey(User, on_delete= models.CASCADE, related_name='note')