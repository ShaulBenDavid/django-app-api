import django_filters
from core.models import Subscription


class SubscriptionFilter(django_filters.FilterSet):
    group = django_filters.CharFilter(method="filter_by_group")

    class Meta:
        model = Subscription
        fields = ["group"]

    def filter_by_group(self, queryset, name, value):
        if value.lower() == "ungroup":
            # Return subscriptions without any group
            return queryset.filter(group__isnull=True)
        if value:
            # Return all subscriptions
            return queryset.filter(group=value)

        # Return subscriptions filtered by specific group ID
        return queryset.all()
