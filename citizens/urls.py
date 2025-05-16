from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('submit/', views.submit_complaint, name='submit_complaint'),
    path('track/', views.track_status, name='track_complaint'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login')
]
