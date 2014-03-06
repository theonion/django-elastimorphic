from rest_framework import serializers

from elastimorphic.serializers import ContentTypeField, PolymorphicSerializerMixin

from .models import (
    ChildIndexable, GrandchildIndexable, ParentIndexable, SeparateIndexable
)


class ParentIndexableSerializer(serializers.ModelSerializer):
    polymorphic_ctype = ContentTypeField(source="polymorphic_ctype_id", read_only=True)

    class Meta:
        model = ParentIndexable


class ChildIndexableSerializer(serializers.ModelSerializer):
    polymorphic_ctype = ContentTypeField(source="polymorphic_ctype_id", read_only=True)

    class Meta:
        model = ChildIndexable


class GrandchildIndexableSerializer(serializers.ModelSerializer):
    polymorphic_ctype = ContentTypeField(source="polymorphic_ctype_id", read_only=True)

    class Meta:
        model = GrandchildIndexable


class SeparateIndexableSerializer(serializers.ModelSerializer):
    polymorphic_ctype = ContentTypeField(source="polymorphic_ctype_id", read_only=True)

    class Meta:
        model = SeparateIndexable


class PolymorphicParentIndexableSerializer(
        PolymorphicSerializerMixin, ParentIndexableSerializer):
    pass


class PolymorphicSeparateIndexableSerializer(
        PolymorphicSerializerMixin, SeparateIndexableSerializer):
    pass
