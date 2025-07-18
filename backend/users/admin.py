from django.contrib import admin

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("email", "get_full_name", "status", "date_joined", "last_login", "type")
    list_filter = ("status", "date_joined", "email_notifications")
    search_fields = ("email", "first_name", "last_name")
    ordering = ("-date_joined",)
    readonly_fields = ("date_joined",)

    fieldsets = (
        (
            "Personal Information",
            {"fields": ("email", "first_name", "last_name", "phone", "type")},
        ),
        ("Status & Dates", {"fields": ("status", "date_joined", "last_login")}),
        ("Preferences", {"fields": ("email_notifications",)}),
    )

    def get_full_name(self, obj):
        return obj.get_full_name()

    get_full_name.short_description = "Full Name"
