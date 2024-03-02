from django.db import models
from django.contrib.auth.models import User
from django.forms import ValidationError

# Create your models here.

bloodGroups = [
    ('O+', 'O+'),
    ('O-', 'O-'),
    ('A+', 'A+'),
    ('A-', 'A-'),
    ('B+', 'B+'),
    ('B-', 'B-'),
    ('AB+', 'AB+'),
    ('AB-', 'AB-'),
]


# def fieldRequiredValidatorString(val: str):
#     if len(val) == 0:
#         raise ValidationError('This field is required')
#     return val


# def fieldRequiredValidatorAny(val):
#     if val == None:
#         raise ValidationError('This field is required')
#     return val

class Profile(models.Model):
    user = models.OneToOneField(
        User, related_name="profile", on_delete=models.CASCADE)
    bloodGroup = models.CharField(
        choices=bloodGroups, max_length=6, blank=True, null=True, default=None)
    age = models.IntegerField(default=0)
    address = models.CharField(max_length=255, default='')
    lastDonationDate = models.DateField(blank=True, null=True, default=None)
    available = models.BooleanField(default=False)
