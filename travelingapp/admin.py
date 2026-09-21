from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import (
    Package, Location, Itineary, ItinearyPoint, TravelDriver,
    PricingBreakdown, PackageGallery, Booking, Subscribers, User, EmailOTP, Profile, Review
)

admin.site.register(Package)
admin.site.register(Location)
admin.site.register(Itineary)
admin.site.register(ItinearyPoint)
admin.site.register(TravelDriver)
admin.site.register(PricingBreakdown)
admin.site.register(PackageGallery)
admin.site.register(Booking)
admin.site.register(Subscribers)


class CustomUserAdmin(UserAdmin):
    model = User

    # "Edit user" form — fields grouped into sections
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    # "Add user" form — this was missing, and still referenced username by default
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "first_name", "last_name", "password1", "password2"),
        }),
    )

    list_display = ("email", "first_name", "last_name", "is_staff", "is_active")
    list_filter = ("is_staff", "is_active")
    ordering = ("email",)
    search_fields = ("email", "first_name", "last_name")


admin.site.register(User, CustomUserAdmin)


@admin.register(EmailOTP)
class EmailOTPAdmin(admin.ModelAdmin):
    list_display = ("user", "otp", "created_at", "expires_at", "is_valid_now")
    readonly_fields = ("user", "otp", "created_at", "expires_at")
    search_fields = ("user__email",)
    ordering = ("-created_at",)

    def is_valid_now(self, obj):
        return obj.is_valid()
    is_valid_now.boolean = True
    is_valid_now.short_description = "Still valid?"

    def has_add_permission(self, request):
        # OTPs should only ever be created by the signup/resend flow, not manually
        return False

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "phone", "date_of_birth")
    search_fields = ("user__email", "phone")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("package", "user", "rating", "is_approved", "created_at")
    list_filter = ("is_approved", "rating", "package")
    search_fields = ("user__email", "package__package_name", "comment")
    actions = ["approve_reviews", "unapprove_reviews"]

    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)
    approve_reviews.short_description = "Approve selected reviews"

    def unapprove_reviews(self, request, queryset):
        queryset.update(is_approved=False)
    unapprove_reviews.short_description = "Unapprove selected reviews"