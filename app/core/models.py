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

    def __str__(self):
        return self.username


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    username = models.CharField(max_length=100)
    image_url = models.URLField(null=True, blank=True)

    def __str__(self):
        return self.username


## USER Subscription list
class UserSubscriptionCollection(models.Model):
    user = models.OneToOneField(
        Profile, on_delete=models.CASCADE, related_name="user_subscription_list"
    )

    def __str__(self):
        return self.user


class Group(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=255)
    user_list = models.ForeignKey(
        UserSubscriptionCollection, on_delete=models.CASCADE, related_name="user_groups"
    )

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
