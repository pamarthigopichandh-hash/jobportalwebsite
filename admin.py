from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import User, JobSeekerProfile, Job, JobApplication,EmployerProfile
from django.contrib.auth import get_user_model

User = get_user_model()
# ==========================================================
# CUSTOM USER ADMIN
# ==========================================================

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User

    list_display = ('username', 'email', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')
    search_fields = ('username', 'email')
    ordering = ('username',)

    fieldsets = UserAdmin.fieldsets + (
        ('Role Information', {'fields': ('role',)}),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Role Information', {'fields': ('role',)}),
    )


# ==========================================================
# JOB SEEKER PROFILE ADMIN
# ==========================================================

@admin.register(JobSeekerProfile)
class JobSeekerProfileAdmin(admin.ModelAdmin):

    list_display = (
        'user',
        'full_name',
        'phone',
        'qualification',
        
    )

    search_fields = ('full_name', 'user__username',)
    


# ==========================================================
# JOB ADMIN
# ==========================================================

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):

    list_display = (
        'title',
        'company',
        'location',
        'salary',
        'created_at',
    )

    search_fields = ('title', 'company', 'location')
    list_filter = ('company', 'location', 'created_at')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)


# ==========================================================
# JOB APPLICATION ADMIN
# ==========================================================

@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):

    list_display = (
        'full_name',
        'job',
        'status_badge',
        'applied_at',
        'resume_link',
    )

    list_filter = ('status', 'applied_at')
    search_fields = ('full_name', 'email', 'job__title')
    ordering = ('-applied_at',)
    readonly_fields = ('applied_at',)

    # -------------------------------
    # Colored Status Badge
    # -------------------------------

    def status_badge(self, obj):
        colors = {
            'Pending': '#f0ad4e',
            'Viewed': '#5bc0de',
            'Accepted': '#5cb85c',
            'Rejected': '#d9534f',
        }

        return format_html(
            '<span style="color:white; padding:5px 10px; border-radius:8px; background-color:{};">{}</span>',
            colors.get(obj.status, '#777'),
            obj.status
        )

    status_badge.short_description = 'Status'

    # -------------------------------
    # Resume Download Link
    # -------------------------------

    def resume_link(self, obj):
        if obj.resume:
            return format_html(
                '<a href="{}" target="_blank">Download Resume</a>',
                obj.resume.url
            )
        return "No Resume"

    resume_link.short_description = "Resume"

@admin.register(EmployerProfile)
class EmployerProfileAdmin(admin.ModelAdmin):
    list_display = ("company_name", "location")