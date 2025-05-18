import secrets

from django.conf import settings
from django.core.mail import send_mail
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.template.loader import render_to_string
from django.utils import timezone

from django.utils.html import strip_tags


class CustomUser(AbstractUser):
    is_category_admin = models.BooleanField(default=False)
    managed_category = models.ForeignKey('ComplaintCategory', on_delete=models.SET_NULL, null=True, blank=True)

class ComplaintCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    department = models.CharField(max_length=100)
    admin_email = models.EmailField(blank=True)

    def __str__(self):
        return f"{self.name} ({self.department})"

    def save(self, *args, **kwargs):
        creating = self.pk is None
        super().save(*args, **kwargs)

        if creating and self.admin_email:
            self.create_category_admin()

    def create_category_admin(self):
        username = f"admin_{self.name.lower().replace(' ', '_')}"
        password = secrets.token_urlsafe(12)  # Generate secure random password

        admin_user, created = CustomUser.objects.get_or_create(
            email=self.admin_email,
            defaults={
                'username': username,
                'is_category_admin': True,
                'managed_category': self
            }
        )

        if created:
            admin_user.set_password(password)
            admin_user.save()
            self.send_admin_credentials(admin_user, password)

    def send_admin_credentials(self, admin_user, password):
        subject = f"Your Administrator Access for {self.name}"

        context = {
            'category': self,
            'username': admin_user.username,
            'password': password,
            'login_url': f"https://{settings.DOMAIN}/login"  # Add DOMAIN to settings.py
        }

        html_message = render_to_string('emails/category_admin_credentials.html', context)
        plain_message = strip_tags(html_message)

        send_mail(
            subject=subject,
            message=plain_message,
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[self.admin_email],
            fail_silently=False,
        )

class Complaint(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('rejected', 'Rejected'),
    ]

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
    assigned_to = models.ForeignKey(CustomUser, related_name='assigned_complaints', on_delete=models.SET_NULL, null=True, blank=True)

    def get_responsible_admin(self):
        return CustomUser.objects.filter(
            is_category_admin=True,
            managed_category=self.category
        ).first()



    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('track_complaint', kwargs={'pk': self.pk})


class ComplaintUpdate(models.Model):
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name='updates')
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