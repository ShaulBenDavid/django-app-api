from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from core.models import Group


@receiver(m2m_changed, sender=Group.subscriptions.through)
def update_subscriptions_group(sender, instance, action, reverse, model, **kwargs):
    if action == "post_add":
        subscription_id = (
            instance.subscriptions.through.objects.last()
        ).subscription_id
        user_groups = (
            instance.subscriptions.through.objects.last().group.user_list.user_groups.all()
        )
        subscription = model.objects.get(pk=subscription_id)

        # Remove subscription from user's previous groups
        previous_groups = user_groups.exclude(pk=instance.pk)
        for prev_group in previous_groups:
            prev_group.subscriptions.remove(subscription)
