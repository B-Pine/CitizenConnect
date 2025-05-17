from django.conf.urls.static import static
from django.urls import path

from citizen_engagemant import settings
from .views import home, submit_complaint, track_complaint_search, TrackComplaintView, dashboard, update_complaint_status, login_view, logout_view

urlpatterns = [
    path('', home, name='home'),
    path('submit/', submit_complaint, name='submit_complaint'),
    path('track/', track_complaint_search, name='track_complaint_all'),
    path('track/<int:pk>/', TrackComplaintView.as_view(), name='track_complaint'),
    path('dashboard/', dashboard, name='dashboard'),
    path('update-status/<int:pk>/', update_complaint_status, name='update_complaint_status'),

    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

]



if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
