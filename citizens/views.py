from django.shortcuts import render

def home(request):
    return render(request, 'citizens/home.html')


def submit_complaint(request):
    return render(request, 'citizens/submit_complaint.html')


def track_status(request):
    return render(request, 'citizens/track_complaint.html')


def login_view(request):
    return None


def dashboard(request):
    return render(request, 'citizens/admin_dashboard.html')