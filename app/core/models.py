from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.CharField(max_length=250, unique=True, null=False, blank=False)
    image_url = models.URLField(null=True, blank=True)
    REGISTRATION_CHOICES = [
        ("email", "Email"),
        ("google", "Google"),
    ]
    registration_method = models.CharField(
        max_length=10, choices=REGISTRATION_CHOICES, default="email"
    )
    ROLE_CHOICES = [
        ("user", "User"),
        ("creator", "Creator"),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="user")

    def __str__(self):
        return self.username


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    username = models.CharField(max_length=100, unique=True)
    image_url = models.URLField(null=True, blank=True)
    instagram_url = models.URLField(max_length=255, blank=True, null=True)
    twitter_url = models.URLField(max_length=255, blank=True, null=True)
    linkedin_url = models.URLField(max_length=255, blank=True, null=True)
    youtube_url = models.URLField(max_length=255, blank=True, null=True)
    tiktok_url = models.URLField(max_length=255, blank=True, null=True)
    telegram_url = models.URLField(max_length=255, blank=True, null=True)
    is_public = models.BooleanField(default=False)
    description = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.username


class CustomURL(models.Model):
    profile = models.ForeignKey(
        "Profile", on_delete=models.CASCADE, related_name="custom_urls"
    )
    name = models.CharField(max_length=100)
    url = models.URLField(max_length=255)

    def __str__(self):
        return f"{self.name}: {self.url}"


## USER Subscription list
class UserSubscriptionCollection(models.Model):
    user = models.OneToOneField(
        Profile, on_delete=models.CASCADE, related_name="user_subscription_list"
    )
    last_data_sync = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return str(self.user)


class Group(models.Model):
    title = models.CharField(max_length=100)
    emoji = models.CharField(max_length=10, null=True, blank=True)
    user_list = models.ForeignKey(
        UserSubscriptionCollection, on_delete=models.CASCADE, related_name="user_groups"
    )
    is_public = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    class Meta:
        unique_together = ("title", "user_list")


class Subscription(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=500)
    channel_id = models.CharField(max_length=100, unique=True)
    image_url = models.URLField(null=True, blank=True)
    group = models.ManyToManyField(Group, related_name="subscriptions", blank=True)
    users_list = models.ManyToManyField(
        UserSubscriptionCollection, related_name="subscriptions"
    )

    def __str__(self):
        return self.title
