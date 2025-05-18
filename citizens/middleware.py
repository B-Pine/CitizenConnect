from django.shortcuts import redirect
from django.urls import reverse

class CategoryAdminMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    # def process_view(self, request, view_func, view_args, view_kwargs):
    #     if request.user.is_authenticated and request.user.is_category_admin:
    #         # Redirect category admins to their specific dashboard
    #         if request.path not in [reverse('category_dashboard'), reverse('logout')]:
    #             return redirect('category_dashboard')