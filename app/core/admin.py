from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from core.models import (
    User,
    Profile,
    Subscription,
    Group,
    UserSubscriptionCollection,
    CustomURL,
    Upload,
)


class CustomUserAdmin(UserAdmin):
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "registration_method",
        "role",
    )

    fieldsets = UserAdmin.fieldsets + (
        (
            "Additional Info",
            {
                "fields": ("role",),
            },
        ),
    )


class GroupInline(admin.StackedInline):
    model = Group
    extra = 1


class UserListAdmin(admin.ModelAdmin):
    all_fields = ("user", "last_data_sync")
    list_display = ("user", "last_data_sync")
    fields = ("user", "last_data_sync")
    inlines = [GroupInline]


class CustomURLInline(admin.TabularInline):
    model = CustomURL
    extra = 1


class ProfileAdmin(admin.ModelAdmin):
    list_display = ("username", "is_public", "description")
    inlines = [CustomURLInline]


class UploadAdmin(admin.ModelAdmin):
    list_display = ("subscription", "title", "upload_time", "last_sync")


admin.site.register(User, CustomUserAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Subscription)
admin.site.register(UserSubscriptionCollection, UserListAdmin)
admin.site.register(Group)
admin.site.register(CustomURL)
admin.site.register(Upload, UploadAdmin)
