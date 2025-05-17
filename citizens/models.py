from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class ComplaintCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    department = models.CharField(max_length=100, help_text="Responsible government department")

    def __str__(self):
        return self.name


class Complaint(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('rejected', 'Rejected'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    category = models.ForeignKey(ComplaintCategory, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=200)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_anonymous = models.BooleanField(default=False)
    contact_email = models.EmailField()

    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('track_complaint', kwargs={'pk': self.pk})


class ComplaintUpdate(models.Model):
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name='updates')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=Complaint.STATUS_CHOICES)
    comment = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Update for {self.complaint.title}"


class ComplaintAttachment(models.Model):
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='complaint_attachments/')
    uploaded_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Attachment for {self.complaint.title}"