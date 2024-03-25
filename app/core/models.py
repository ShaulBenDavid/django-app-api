from django.contrib.auth.models import AbstractUser
from django.conf import settings
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
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    username = models.CharField(max_length=100)
    image_url = models.URLField(null=True, blank=True)

    def __str__(self):
        return self.username


## USER Subscription list
class Group(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    def __str__(self):
        return self.title

    class Meta:
        unique_together = ('title', 'user')

class Subscription(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=500)
    channel_id = models.CharField(max_length=100, unique=True)
    image_url = models.URLField(null=True, blank=True)
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='subscriptions')

    def __str__(self):
        return self.title


class UserSubscriptionList(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_subscription_list')
    subscriptions = models.ManyToManyField(Subscription, related_name='subscription_lists')

    def __str__(self):
        return f"{self.user.name}'s Item List"
