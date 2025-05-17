from django import forms
from .models import Complaint, ComplaintAttachment, ComplaintCategory
from django.core.validators import FileExtensionValidator


class ComplaintForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=ComplaintCategory.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    attachments = forms.FileField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'multiple': False}),
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'pdf', 'doc', 'docx'])]
    )

    class Meta:
        model = Complaint
        fields = ['category', 'title', 'description', 'location', 'contact_email', 'is_anonymous']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'is_anonymous': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(ComplaintForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        complaint = super().save(commit=False)
        if self.request and self.request.user.is_authenticated:
            complaint.user = self.request.user
        if commit:
            complaint.save()
        return complaint