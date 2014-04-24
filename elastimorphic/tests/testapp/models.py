from django.db import models
from polymorphic import PolymorphicModel

from elastimorphic import PolymorphicIndexable, SearchManager
from elastimorphic.mappings import MappingMixin, DocumentType, fields


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


class ParentIndexable(PolymorphicIndexable, PolymorphicModel, MappingMixin):
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


class RelatedModel(models.Model):
    qux = models.CharField(max_length=255, null=True, blank=True)


class GrandchildIndexable(ChildIndexable):
    baz = models.DateField()
    related = models.ForeignKey(RelatedModel, null=True, blank=True)

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

    class Mapping(DocumentType):
        foo = fields.StringField(index="not_analyzed")
        bar = fields.IntegerField(store="yes")
        baz = fields.DateField(format="YYYY-MM-dd")
