from django.db.models.signals import m2m_changed, pre_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from core.models import Group

MAX_GROUPS_PER_USER = 15


@receiver(pre_save, sender=Group)
def validate_group_limit(sender, instance, **kwargs):
    user_subscription_collection = instance.user_list
    if instance.pk is None:
        if user_subscription_collection.user_groups.count() >= MAX_GROUPS_PER_USER:
            raise ValidationError(
                f"You cannot create more than {MAX_GROUPS_PER_USER} groups."
            )


@receiver(m2m_changed, sender=Group.subscriptions.through)
def update_subscriptions_group(sender, instance, action, reverse, model, **kwargs):
    if action == "post_add":
        subscription_id = (
            instance.subscriptions.through.objects.last()
        ).subscription_id
        user_groups = instance.subscriptions.through.objects.last().group.user_list.user_groups.filter(
            subscriptions=subscription_id
        )
        subscription = model.objects.get(pk=subscription_id)

        # Remove subscription from user's previous groups
        previous_groups = user_groups.exclude(pk=instance.pk)
        if len(previous_groups):
            for prev_group in previous_groups:
                prev_group.subscriptions.remove(subscription)
