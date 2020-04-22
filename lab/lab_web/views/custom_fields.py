from rest_framework import serializers
from collections import OrderedDict


class PresentableRelatedFieldMixin(object):
    def __init__(self, **kwargs):
        self.presentation_serializer = kwargs.pop("presentation_serializer", None)
        self.presentation_serializer_kwargs = kwargs.pop(
            "presentation_serializer_kwargs", dict()
        )
        assert self.presentation_serializer is not None, (
                self.__class__.__name__
                + " must provide a `presentation_serializer` argument"
        )
        super(PresentableRelatedFieldMixin, self).__init__(**kwargs)

    def use_pk_only_optimization(self):
        """
        Instead of sending pk only object, return full object. The object already retrieved from db by drf.
        This doesn't cause an extra query.
        It even might save from making an extra query on serializer.to_representation method.
        Related source codes:
        - https://github.com/tomchristie/django-rest-framework/blob/master/rest_framework/relations.py#L41
        - https://github.com/tomchristie/django-rest-framework/blob/master/rest_framework/relations.py#L132
        """
        return False

    def get_queryset(self):
        user = self.context['request'].user
        queryset = self.queryset.filter(user=user)
        return queryset

    def get_choices(self, cutoff=None):
        queryset = self.get_queryset()
        if queryset is None:
            # Ensure that field.choices returns something sensible
            # even when accessed with a read-only field.
            return {}

        if cutoff is not None:
            queryset = queryset[:cutoff]

        return OrderedDict([(item.pk, self.display_value(item)) for item in queryset])

    def to_representation(self, data):
        return self.presentation_serializer(
            data, context=self.context, **self.presentation_serializer_kwargs
        ).data


class PresentablePrimaryKeyRelatedField(
    PresentableRelatedFieldMixin, serializers.PrimaryKeyRelatedField
):
    """
    Override PrimaryKeyRelatedField to represent serializer data instead of a pk field of the object.
    """

    pass


class UserFilteredPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        request = self.context.get('request', None)
        queryset = super(UserFilteredPrimaryKeyRelatedField, self).get_queryset()
        if not request or not queryset:
            return None
        return queryset.filter(user=request.user)
