from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from core.models import User, Profile, Subscription, Group, UserSubscriptionCollection


class CustomUserAdmin(UserAdmin):
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "registration_method",
    )


class GroupInline(admin.StackedInline):
    model = Group
    extra = 1


class UserListAdmin(admin.ModelAdmin):
    all_fields = ("user", "last_data_sync")
    list_display = ('user', 'last_data_sync')
    fields = ('user', 'last_data_sync')
    inlines = [GroupInline]


admin.site.register(User, CustomUserAdmin)
admin.site.register(Profile)
admin.site.register(Subscription)
admin.site.register(UserSubscriptionCollection, UserListAdmin)
admin.site.register(Group)
