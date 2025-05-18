from django.db import models
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.generic import DetailView
from .models import Complaint, ComplaintCategory, ComplaintUpdate, ComplaintAttachment



def is_category_admin(user):
    return user.is_authenticated and user.is_category_admin


@login_required
@user_passes_test(is_category_admin)
def category_dashboard(request):
    category = request.user.managed_category
    complaints = Complaint.objects.filter(
        category=category
    ).order_by('-created_at')

    status_counts = complaints.values('status').annotate(count=models.Count('id'))
    your_assigned_count = complaints.filter(assigned_to=request.user).count()

    return render(request, 'government/category_dashboard.html', {
        'category': category,
        'complaints': complaints,
        'your_assigned_count': your_assigned_count,
        'status_counts': status_counts,
        'pending_count': complaints.filter(status='pending').count(),
        'in_progress_count': complaints.filter(status='in_progress').count(),
        'resolved_count': complaints.filter(status='resolved').count(),
    })


@login_required
@user_passes_test(is_category_admin)
def update_complaint_status(request, pk):
    complaint = get_object_or_404(Complaint, pk=pk, category=request.user.managed_category)

    if request.method == 'POST':
        status = request.POST.get('status')
        comment = request.POST.get('comment')

        if status and comment:
            ComplaintUpdate.objects.create(
                complaint=complaint,
                author=request.user,
                status=status,
                comment=comment
            )

            complaint.status = status
            complaint.assigned_to = request.user if status == 'in_progress' else None
            complaint.save()

            messages.success(request, 'Complaint status updated successfully!')
        else:
            messages.error(request, 'Please provide both status and comment.')

        return redirect('category_dashboard')

    return redirect('category_dashboard')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')  # Or your preferred redirect page

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, 'You have successfully logged in!')

            # Redirect to next parameter if it exists
            next_url = request.GET.get('next')
            return redirect(next_url if next_url else 'category_dashboard')
        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'citizens/login.html')


def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')

def submit_complaint(request):
    if request.method == 'POST':
        try:
            # Get form data
            category_id = request.POST.get('category')
            title = request.POST.get('title')
            description = request.POST.get('description')
            location = request.POST.get('location')
            contact_email = request.POST.get('contact_email')
            is_anonymous = request.POST.get('is_anonymous') == 'on'

            # Validate required fields
            if not all([category_id, title, description, location, contact_email]):
                messages.error(request, 'Please fill all required fields')
                return redirect('submit_complaint')

            # Get category instance
            try:
                category = ComplaintCategory.objects.get(id=category_id)
            except ComplaintCategory.DoesNotExist:
                messages.error(request, 'Invalid category selected')
                return redirect('submit_complaint')

            # Create complaint
            complaint = Complaint.objects.create(
                category=category,
                title=title,
                description=description,
                location=location,
                contact_email=contact_email,
                is_anonymous=is_anonymous,

            )

            # Handle file attachments
            files = request.FILES.getlist('attachments')
            for file in files:
                ComplaintAttachment.objects.create(
                    complaint=complaint,
                    file=file
                )

            # Create initial status update
            ComplaintUpdate.objects.create(
                complaint=complaint,
                status='pending',
                comment='Complaint received and is being processed.'
            )

            messages.success(request, 'Your complaint has been submitted successfully!')
            return redirect('track_complaint', pk=complaint.pk)

        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
            return redirect('submit_complaint')

    # GET request - show form
    categories = ComplaintCategory.objects.all()
    return render(request, 'citizens/submit_complaint.html', {
        'categories': categories
    })


def track_complaint_search(request):
    if request.method == 'POST':
        reference_number = request.POST.get('reference_number', '').strip()

        if not reference_number:
            messages.error(request, 'Please enter a reference number')
            return redirect('track_complaint_search')

        try:
            # Extract the numeric part from reference (CC-1234 → 1234)
            complaint_id = int(reference_number.split('-')[-1])
            complaint = get_object_or_404(Complaint, pk=complaint_id)
            return redirect('track_complaint', pk=complaint.pk)

        except Complaint.DoesNotExist:
            messages.error(request, 'No complaint found with this reference number')
            return redirect('track_complaint_all')

        except (ValueError, IndexError):
            messages.error(request, 'Invalid reference number format')
            return redirect('track_complaint_all')


    # GET request - show search form
    return render(request, 'citizens/track_complaint_all.html')

class TrackComplaintView(DetailView):
    model = Complaint
    template_name = 'citizens/track_complaint.html'
    context_object_name = 'complaint'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['updates'] = self.object.updates.all().order_by('-created_at')
        return context


@login_required
def dashboard(request):
    if request.user.is_staff:
        complaints = Complaint.objects.all().order_by('-created_at')
    else:
        complaints = Complaint.objects.filter(user=request.user).order_by('-created_at')

    return render(request, 'citizens/admin_dashboard.html', {
        'complaints': complaints
    })


@login_required
def update_complaint_status(request, pk):
    complaint = get_object_or_404(Complaint, pk=pk)

    if request.method == 'POST':
        status = request.POST.get('status')
        comment = request.POST.get('comment')

        if status and comment:
            ComplaintUpdate.objects.create(
                complaint=complaint,
                status=status,
                comment=comment
            )

            # Update the complaint status
            complaint.status = status
            complaint.save()

            messages.success(request, 'Complaint status updated successfully!')
        else:
            messages.error(request, 'Please provide both status and comment.')

        return redirect('track_complaint', pk=complaint.pk)

    return redirect('dashboard')
def home(request):
    return render(request, 'citizens/home.html')



def track_status(request):
    return render(request, 'citizens/track_complaint.html')


