from django.db import models
from django.contrib.auth.models import User

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


class DonationRequest(models.Model):
    createdAt = models.DateTimeField(auto_now_add=True)
    createdBy = models.ForeignKey(
        to=User, related_name='created_requests', on_delete=models.CASCADE)
    bloodGroup = models.CharField(choices=bloodGroups, max_length=4)
    date = models.DateField()
    contactNumber = models.CharField(max_length=15)
    targetDonor = models.ForeignKey(
        to=User, blank=True, null=True, default=None, on_delete=models.CASCADE, related_name="receivedRequests")
    acceptedBy = models.ForeignKey(
        to=User, blank=True, null=True, default=None, on_delete=models.CASCADE, related_name="acceptedRequests")
    description = models.CharField(max_length=256)
    cancelled = models.BooleanField(default=False)
    updatedAt = models.DateTimeField(auto_now_add=True)
