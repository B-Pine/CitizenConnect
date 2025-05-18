from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Complaint, ComplaintCategory, ComplaintUpdate, ComplaintAttachment, CustomUser


class ComplaintAttachmentInline(admin.TabularInline):
    model = ComplaintAttachment
    extra = 0


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'is_category_admin', 'managed_category')
    list_filter = ('is_category_admin',)
    fieldsets = UserAdmin.fieldsets + (
        ('Category Management', {
            'fields': ('is_category_admin', 'managed_category'),
        }),
    )

class ComplaintUpdateInline(admin.TabularInline):
    model = ComplaintUpdate
    extra = 0
    readonly_fields = ('created_at',)

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'status', 'created_at')
    list_filter = ('status', 'category', 'created_at')
    search_fields = ('title', 'description', 'location')
    inlines = [ComplaintAttachmentInline, ComplaintUpdateInline]
    readonly_fields = ('created_at', 'updated_at')

@admin.register(ComplaintCategory)
class ComplaintCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'department')
    search_fields = ('name', 'department')

admin.site.register(ComplaintUpdate)
admin.site.register(ComplaintAttachment)