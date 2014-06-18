from django.db import models
from polymorphic import PolymorphicModel

from elastimorphic import Indexable, PolymorphicIndexable, SearchManager
from elastimorphic.mappings import fields
from elastimorphic.mappings import doctype


class SeparateIndexable(PolymorphicIndexable, PolymorphicModel):
    junk = models.CharField(max_length=255)

    search_objects = SearchManager()


class ParentIndexable(PolymorphicIndexable, PolymorphicModel):
    foo = models.CharField(max_length=255)

    search_objects = SearchManager()


class ChildIndexable(ParentIndexable):
    bar = models.IntegerField()


class RelatedModel(Indexable, models.Model):
    qux = models.CharField(max_length=255, null=True, blank=True)

    class Mapping(doctype.DocumentType):
        class Meta:
            exclude = ("id",)

        qux = fields.StringField()


class GrandchildIndexable(ChildIndexable):
    baz = models.DateField()
    related = models.ForeignKey(RelatedModel, null=True, blank=True)

    class Mapping(doctype.DocumentType):
        foo = fields.StringField()
        bar = fields.IntegerField(store="yes")
        baz = fields.DateField()
        related = RelatedModel.Mapping()
