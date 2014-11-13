from django.db import models
from polymorphic import PolymorphicModel

from elastimorphic import PolymorphicIndexable, SearchManager


class SeparateIndexable(PolymorphicIndexable, PolymorphicModel):
    junk = models.CharField(max_length=255)

    search_objects = SearchManager()

    def extract_document(self):
        doc = super(SeparateIndexable, self).extract_document()
        doc["junk"] = self.junk
        return doc

    @classmethod
    def get_mapping_properties(cls):
        properties = super(SeparateIndexable, cls).get_mapping_properties()
        properties.update({
            "junk": {"type": "string"}
        })
        return properties

    @classmethod
    def get_serializer_class(cls):
        from .serializers import SeparateIndexableSerializer
        return SeparateIndexableSerializer


class ParentIndexable(PolymorphicIndexable, PolymorphicModel):
    foo = models.CharField(max_length=255)

    search_objects = SearchManager()

    def extract_document(self):
        doc = super(ParentIndexable, self).extract_document()
        doc['foo'] = self.foo
        return doc

    @classmethod
    def get_mapping_properties(cls):
        properties = super(ParentIndexable, cls).get_mapping_properties()
        properties.update({
            "foo": {"type": "string"}
        })
        return properties

    @classmethod
    def get_serializer_class(cls):
        from .serializers import ParentIndexableSerializer
        return ParentIndexableSerializer


class ChildIndexable(ParentIndexable):
    bar = models.IntegerField()

    def extract_document(self):
        doc = super(ChildIndexable, self).extract_document()
        doc["bar"] = self.bar
        return doc

    @classmethod
    def get_mapping_properties(cls):
        properties = super(ChildIndexable, cls).get_mapping_properties()
        properties.update({
            "bar": {"type": "integer"}
        })
        return properties

    @classmethod
    def get_serializer_class(cls):
        from .serializers import ChildIndexableSerializer
        return ChildIndexableSerializer


class GrandchildIndexable(ChildIndexable):
    baz = models.DateField()

    def extract_document(self):
        doc = super(GrandchildIndexable, self).extract_document()
        doc["baz"] = self.baz
        return doc

    @classmethod
    def get_mapping_properties(cls):
        properties = super(GrandchildIndexable, cls).get_mapping_properties()
        properties.update({
            "baz": {"type": "date"}
        })
        return properties

    @classmethod
    def get_serializer_class(cls):
        from .serializers import GrandchildIndexableSerializer
        return GrandchildIndexableSerializer


class PolyMixin(PolymorphicIndexable, models.Model):
    itsa = models.TextField(default="", blank=True)
    mixin = models.TextField(default="", blank=True)

    class Meta:
        abstract = True


class MixedIndexable(SeparateIndexable, PolyMixin):
    pass
