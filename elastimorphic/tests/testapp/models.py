from django.db import models
from polymorphic import PolymorphicModel

from elastimorphic import Indexable, PolymorphicIndexable, SearchManager
from elastimorphic import mappings


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

    class Mapping(mappings.DocumentType):
        class Meta:
            exclude = ("id",)

        qux = mappings.StringField()


class GrandchildIndexable(ChildIndexable):
    baz = models.DateField()
    related = models.ForeignKey(RelatedModel, null=True, blank=True)

    class Mapping(mappings.DocumentType):
        foo = mappings.StringField()
        bar = mappings.IntegerField(store="yes")
        baz = mappings.DateField()
        related = RelatedModel.Mapping()
