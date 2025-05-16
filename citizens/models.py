from django.db import models

CATEGORY_CHOICES = [
    ('water', 'Water Supply'),
    ('road', 'Roads'),
    ('electricity', 'Electricity'),
    ('health', 'Health Services'),
    ('violation', 'Domestic Violations'),
    ('other', 'Other')
]

STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('in_progress', 'In Progress'),
    ('resolved', 'Resolved')
]

class Complaint(models.Model):
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    national_id = models.CharField(max_length=100)
    email = models.EmailField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    message = models.TextField()
    attachment = models.FileField(upload_to='attachments/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    response = models.TextField(blank=True)
