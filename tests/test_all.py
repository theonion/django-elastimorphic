from __future__ import absolute_import

import copy
import datetime

from django.core.management import call_command
from django.test import TestCase

import elasticsearch

from elasticutils import get_es

from elastimorphic.conf import settings
from elastimorphic.models import polymorphic_indexable_registry

from elastimorphic.tests.base import BaseIndexableTestCase
from elastimorphic.tests.testapp.models import (
    ChildIndexable,
    GrandchildIndexable,
    ParentIndexable,
    SeparateIndexable,
    MixedIndexable)


class IndexableTestCase(BaseIndexableTestCase):

    def setUp(self):
        super(IndexableTestCase, self).setUp()

        ParentIndexable.objects.create(foo="Fighters")
        ChildIndexable.objects.create(foo="Fighters", bar=69)
        GrandchildIndexable.objects.create(foo="Fighters", bar=69, baz=datetime.datetime.now() - datetime.timedelta(hours=1))

        SeparateIndexable.objects.create(junk="Testing")

        ParentIndexable.search_objects.refresh()
        SeparateIndexable.search_objects.refresh()

    def test_mapping_type_names(self):
        self.assertEqual(ParentIndexable.get_mapping_type_name(), "testapp_parentindexable")
        self.assertEqual(ChildIndexable.get_mapping_type_name(), "testapp_childindexable")
        self.assertEqual(GrandchildIndexable.get_mapping_type_name(), "testapp_grandchildindexable")
        self.assertEqual(SeparateIndexable.get_mapping_type_name(), "testapp_separateindexable")
        self.assertEqual(
            ParentIndexable.get_mapping_type_names(), [
                ParentIndexable.get_mapping_type_name(),
                ChildIndexable.get_mapping_type_name(),
                GrandchildIndexable.get_mapping_type_name(),
            ]
        )
        self.assertEqual(
            SeparateIndexable.get_mapping_type_names(), [
                SeparateIndexable.get_mapping_type_name(),
                MixedIndexable.get_mapping_type_name(),
            ]
        )

    def test_get_index_mappings(self):
        pass

    def test_search(self):
        self.assertEqual(ParentIndexable.search_objects.s().count(), 3)
        self.assertEqual(ParentIndexable.search_objects.query(bar=69).count(), 2)
        self.assertEqual(ParentIndexable.search_objects.query(foo__match="Fighters").count(), 3)
        self.assertEqual(ParentIndexable.search_objects.query(baz__lte=datetime.datetime.now()).count(), 1)

        self.assertEqual(SeparateIndexable.search_objects.s().count(), 1)

    def test_instance_of(self):
        self.assertEqual(ParentIndexable.search_objects.s().instance_of(ParentIndexable, exact=True).count(), 1)
        self.assertEqual(ParentIndexable.search_objects.s().instance_of(ChildIndexable, exact=True).count(), 1)
        self.assertEqual(ParentIndexable.search_objects.s().instance_of(GrandchildIndexable, exact=True).count(), 1)

        self.assertEqual(ParentIndexable.search_objects.s().doctypes("testapp_parentindexable").count(), 1)
        self.assertEqual(ParentIndexable.search_objects.s().doctypes("testapp_childindexable").count(), 1)
        self.assertEqual(ParentIndexable.search_objects.s().doctypes("testapp_grandchildindexable").count(), 1)

        self.assertEqual(ParentIndexable.search_objects.s().instance_of(ParentIndexable).count(), 3)
        self.assertEqual(ParentIndexable.search_objects.s().instance_of(ChildIndexable).count(), 2)
        self.assertEqual(ParentIndexable.search_objects.s().instance_of(GrandchildIndexable).count(), 1)

    def test_model_results(self):
        qs = ParentIndexable.search_objects.s().full()
        for obj in qs:
            self.assertTrue(obj.__class__ in [ParentIndexable, ChildIndexable, GrandchildIndexable])

        self.assertEqual(len(qs[:2]), 2)

    def test_s_all_respects_slicing(self):
        s = ParentIndexable.search_objects.s()
        num_s = s.count()
        self.assertEqual(len(s), num_s)
        sliced = s[1:2]
        self.assertEqual(len(sliced.all()), 1)


class ManagementTestCase(BaseIndexableTestCase):

    def test_synces(self):
        backup_settings = copy.copy(settings.ES_SETTINGS)
        test_tokenizer = {
            "type": "edgeNGram",
            "min_gram": "3",
            "max_gram": "4"
        }
        settings.ES_SETTINGS.update({
            "index": {
                "analysis": {
                    "tokenizer": {
                        "edge_ngram_test_tokenizer": test_tokenizer
                    }
                }
            }
        })
        call_command("synces", self.index_suffix, force=True)
        es_settings = self.es.indices.get_settings(index=ParentIndexable.get_index_name())
        index_settings = es_settings[es_settings.keys()[0]]["settings"]
        self.assertEqual(index_settings["index"]["analysis"]["tokenizer"]["edge_ngram_test_tokenizer"], test_tokenizer)

        settings.ES_SETTINGS = backup_settings

    def test_bulk_index(self):
        ParentIndexable(foo="Fighters").save(index=False)
        ChildIndexable(foo="Fighters", bar=69).save(index=False)

        GrandchildIndexable(
            foo="Fighters",
            bar=69,
            baz=datetime.datetime.now() - datetime.timedelta(hours=1)
        ).save(index=False)

        SeparateIndexable(junk="Testing").save(index=False)

        # Let's make sure that nothing is indexed yet.
        self.assertEqual(ParentIndexable.search_objects.s().count(), 0)
        self.assertEqual(SeparateIndexable.search_objects.s().count(), 0)

        # Now that everything has been made, let's try a bulk_index.
        call_command("bulk_index")
        ParentIndexable.search_objects.refresh()
        SeparateIndexable.search_objects.refresh()

        # Let's make sure that everything has the right counts
        self.assertEqual(ParentIndexable.search_objects.s().count(), 3)
        self.assertEqual(SeparateIndexable.search_objects.s().count(), 1)

        # Let's add another one, make sure the counts are right.
        ParentIndexable(foo="Mr. T").save(index=False)
        self.assertEqual(ParentIndexable.search_objects.s().count(), 3)
        call_command("bulk_index")
        ParentIndexable.search_objects.refresh()
        self.assertEqual(ParentIndexable.search_objects.s().count(), 4)

        # Let's fuck up some data in ES.
        obj = ParentIndexable.objects.all()[0]
        es = get_es(urls=settings.ES_URLS)
        doc = obj.extract_document()
        doc["foo"] = "DATA LOVERS"
        es.update(
            index=obj.get_index_name(),
            doc_type=obj.get_mapping_type_name(),
            id=obj.id,
            body=dict(doc=doc, doc_as_upsert=True),
            refresh=True)

        # Make sure the bad data works
        self.assertEqual(ParentIndexable.search_objects.query(foo__match="DATA LOVERS").count(), 1)
        call_command("bulk_index")
        ParentIndexable.search_objects.refresh()
        self.assertEqual(ParentIndexable.search_objects.query(foo__match="DATA LOVERS").count(), 0)

        # Let's delete an item from the db.
        obj = ParentIndexable.objects.all()[0]
        obj.delete()

        # Make sure the count is the same
        self.assertEqual(ParentIndexable.search_objects.s().count(), 4)

        # This shoulnd't remove the item
        call_command("bulk_index")
        ParentIndexable.search_objects.refresh()
        self.assertEqual(ParentIndexable.search_objects.s().count(), 4)

        # This should
        call_command("synces", self.index_suffix, drop_existing_indexes=True)
        call_command("es_swap_aliases", self.index_suffix)
        call_command("bulk_index")
        ParentIndexable.search_objects.refresh()
        self.assertEqual(ParentIndexable.search_objects.s().count(), 3)

    def test_index_upgrade(self):
        ParentIndexable(foo="Fighters").save()
        ChildIndexable(foo="Fighters", bar=69).save()
        GrandchildIndexable(
            foo="Fighters",
            bar=69,
            baz=datetime.datetime.now() - datetime.timedelta(hours=1)
        ).save()
        SeparateIndexable(junk="Testing").save()
        # make sure we have some indexed stuff
        ParentIndexable.search_objects.refresh()
        SeparateIndexable.search_objects.refresh()
        self.assertEqual(ParentIndexable.search_objects.s().count(), 3)
        self.assertEqual(SeparateIndexable.search_objects.s().count(), 1)

        call_command("synces", "vtest123", drop_existing_indexes=True)
        call_command("bulk_index", index_suffix="vtest123")
        call_command("es_swap_aliases", "vtest123")
        ParentIndexable.search_objects.refresh()
        SeparateIndexable.search_objects.refresh()
        # Let's make sure that everything has the right counts
        self.assertEqual(ParentIndexable.search_objects.s().count(), 3)
        self.assertEqual(SeparateIndexable.search_objects.s().count(), 1)
        self.delete_indexes_with_suffix("vtest123")  # clean up


class TestDynamicMappings(BaseIndexableTestCase):

    maxDiff = 2000

    def test_bad_index(self):
        """Check to make sure that the mappings are strict"""
        index_mapping = self.es.indices.get_mapping(index=ParentIndexable.get_index_name(), doc_type=ParentIndexable.get_mapping_type_name())
        alias_name = index_mapping.keys()[0]
        mapping = index_mapping[alias_name]["mappings"]
        self.assertDictEqual(mapping, ParentIndexable.get_mapping())

        obj = ParentIndexable.objects.create(foo="Fighters")
        ParentIndexable.search_objects.refresh()
        doc = obj.extract_document()
        doc["extra"] = "Just an additional string"

        with self.assertRaises(elasticsearch.RequestError):
            self.es.update(
                obj.get_index_name(),
                obj.get_mapping_type_name(),
                obj.id,
                body=dict(doc=doc, doc_as_upsert=True)
            )

        index_mapping = self.es.indices.get_mapping(index=ParentIndexable.get_index_name(), doc_type=ParentIndexable.get_mapping_type_name())
        alias_name = index_mapping.keys()[0]
        mapping = index_mapping[alias_name]["mappings"]
        self.assertDictEqual(mapping, ParentIndexable.get_mapping())


class TestPolymorphicIndexableRegistry(TestCase):
    def test_registry_has_models(self):
        self.assertTrue(polymorphic_indexable_registry.all_models)
        self.assertTrue(polymorphic_indexable_registry.families)
        types = polymorphic_indexable_registry.get_doctypes(ParentIndexable)
        desired_classes = set([
            ParentIndexable, ChildIndexable, GrandchildIndexable
        ])
        result_classes = set()
        for name, klass in types.items():
            result_classes.add(klass)
        self.assertEqual(desired_classes, result_classes)

    def test_registry_has_no_abstract_models(self):
        types = polymorphic_indexable_registry.get_doctypes(SeparateIndexable)
        desired_classes = set([SeparateIndexable, MixedIndexable])
        result_classes = set()
        for name, klass in types.items():
            result_classes.add(klass)
        self.assertEqual(desired_classes, result_classes)
