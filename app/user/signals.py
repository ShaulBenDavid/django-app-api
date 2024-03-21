from django.db.models.signals import post_save
from django.dispatch import receiver
from core.models import Profile, User


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(
            user=instance, username=instance.username, image_url=instance.image_url
        )
